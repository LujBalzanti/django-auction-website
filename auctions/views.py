from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import CommentForm

from .models import User, Category, Listing, Bid, Comment
from . import util


def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "activeListings": activeListings,
        "categories": categories
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login')
def createListing(request):
    if request.method == "POST":
        title = request.POST["listingTitle"]
        description = request.POST["listingDescription"]
        price = request.POST["listingPrice"]
        selectedCategories = request.POST.getlist("listingCategories")
        photoUrl = request.POST["listingPhotoUrl"]

        try:
            tags = []
            for category in selectedCategories:
                tags.append(Category.objects.get(tag=category))
        except Exception as error:
            return render(request, "auctions/error.html", {
                "error": error
            })

        try:
            newListing = Listing(creator=request.user, title=title, description=description, price=price, photoUrl=photoUrl)
            newListing.save()
            for tag in tags:
                newListing.categories.add(tag)
        except Exception as error:
            return render(request, "auctions/error.html", {
                "error": error
            })

        return HttpResponseRedirect(reverse("index"))
    
    else:
        categories = Category.objects.all()
        return render(request, "auctions/createListing.html", {
            "categories": categories
        })

def listing(request, id):
    httpMethodNames = ["placeBid", "removeFromWatchlist", "addToWatchlist", "postComment", "closeAuction"]
    visitedListing = Listing.objects.get(id=id)
    categories = visitedListing.categories.all()
    leadBidder = util.checkLeadBidder(Bid.objects.filter(bidder=request.user.id), visitedListing)
    comments = visitedListing.comments.filter(active=True).order_by("-date") 
    newComment = None  
    newCommentForm = CommentForm()
    util.checkHighest(visitedListing)

    if request.method == "POST":
        method = request.POST.get("_method", '')

        if method == "addToWatchlist":
            user = request.user
            user.watchlist.add(visitedListing)

            return render(request, "auctions/listing.html",{
                "visitedListing": visitedListing,
                "categories": categories,
                "leadBidder": leadBidder,
                "comments": comments,
                "commentForm": newCommentForm
            })

        elif method == "closeAuction":
            visitedListing.isActive = False
            visitedListing.save()
            
            return render(request, "auctions/listing.html",{
                "visitedListing": visitedListing,
                "categories": categories,
                "leadBidder": leadBidder,
                "comments": comments,
                "commentForm": newCommentForm
            })

        elif method == "postComment":
            newCommentForm = CommentForm(data=request.POST)
            if newCommentForm.is_valid():
                newComment = newCommentForm.save(commit=False)
                newComment.listing = visitedListing
                newComment.commentor = request.user
                newComment.save()

                newComment = None  
                newCommentForm = CommentForm()

                return render(request, "auctions/listing.html",{
                    "visitedListing": visitedListing,
                    "categories": categories,
                    "leadBidder": leadBidder,
                    "comments": comments,
                    "commentForm": newCommentForm
                })
            else:
                error = "Comment invalid, limit yourself to 280 characters per comment"
                return render(request, "auctions/error.html", {
                "error": error
            })


        elif method == "removeFromWatchlist":
            user = request.user
            user.watchlist.remove(visitedListing)

            return render(request, "auctions/listing.html",{
                "visitedListing": visitedListing,
                "categories": categories,
                "leadBidder": leadBidder,
                "comments": comments,
                "commentForm": newCommentForm
            })
  
        elif method == "placeBid":
            try:
                bidAmount = float(request.POST["listingBid"])

                if util.checkValidBid(visitedListing, bidAmount):
                    newBid = Bid(bidder=request.user, listing=Listing.objects.get(id=id), amount=bidAmount)
                else:
                    return render(request, "auctions/error.html", {
                            "error": "Your bid was too low"
                        })

            except Exception as error:
                return render(request, "auctions/error.html", {
                    "error": error
                })

            newBid.save()
            visitedListing.highestBid = bidAmount
            visitedListing.save()
            
            leadBidder = util.checkLeadBidder(Bid.objects.filter(bidder=request.user.id), visitedListing)
                
            return render(request, "auctions/listing.html",{
                "visitedListing": visitedListing,
                "categories": categories,
                "leadBidder": leadBidder,
                "comments": comments,
                "commentForm": newCommentForm
            })

    else:
        return render(request, "auctions/listing.html",{
            "visitedListing": visitedListing,
            "categories": categories,
            "leadBidder": leadBidder,
            "comments": comments,
            "commentForm": newCommentForm
        })

@login_required(login_url='/login')
def watchlist(request):
    watchlisted = request.user.watchlist.all()
    categories = Category.objects.all()
    return render(request, "auctions/watchlist.html", {
        "watchlisted": watchlisted,
        "categories": categories,
        "displayCategory": ""
    })

@login_required(login_url='/login')
def watchlistCategory(request, category):
    categoryID = Category.objects.get(tag=category)
    watchlisted = request.user.watchlist.filter(categories=categoryID)
    categories = Category.objects.all()
    return render(request, "auctions/watchlist.html", {
        "watchlisted": watchlisted,
        "categories": categories,
        "displayCategory": category
    })

def categories(request):
    categories = Category.objects.all() 
    try:
        return render(request, "auctions/categories.html", {
            "categories": categories
        })
    except Exception as error:
        return render(request, "auctions/error.html", {
                "error": error
            })


def displayCategory(request, search):
        try:
            categories = Category.objects.all()
            tag = Category.objects.get(tag=search)
            filterArgs = { 'categories': tag, 'isActive': True}
            taggedListings = Listing.objects.filter(**filterArgs)

        except Exception as error:
            return render(request, "auctions/error.html", {
                "error": error
            })
        

        return render(request, "auctions/displayCategory.html", {
            "taggedListings": taggedListings,
            "categories": categories,
            "displayCategory": search
        })

@login_required(login_url='/login')
def displayUserListingCategory(request, userCategory):
    try:
        categories = Category.objects.all()
        tag = Category.objects.get(tag=userCategory)
        filterArgs = { 'categories': tag, 'isActive': True, 'creator': request.user}
        taggedListings = Listing.objects.filter(**filterArgs)

    except Exception as error:
        return render(request, "auctions/error.html", {
            "error": error
        })
    
    return render(request, "auctions/userListings.html", {
        "userListings": taggedListings,
        "categories": categories,
        "displayCategory": userCategory
    })


@login_required(login_url='/login')
def userListings(request):
    currentUser = request.user
    userListings = currentUser.userListings.all()
    categories = Category.objects.all()
    return render(request, "auctions/userListings.html", {
        "userListings": userListings,
        "categories": categories,
        "displayCategory": ""
    })
    