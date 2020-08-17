from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Category, Listing, Bid, Comment
from . import util


def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    return render(request, "auctions/index.html", {
        "activeListings": activeListings,
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
    httpMethodNames = ["post", "patch", "delete", "put", "postComment"]
    visitedListing = Listing.objects.get(id=id)
    categories = visitedListing.categories.all()
    leadBidder = False      

    if request.method == "POST":
        method = request.POST.get("_method", '')

        if method == "put":
            user = request.user
            user.watchlist.add(visitedListing)
            util.checkHighest(visitedListing)
            
            for bid in Bid.objects.filter(bidder=request.user.id):
                if visitedListing.highestBid == bid.amount:
                    leadBidder = True

            return render(request, "auctions/listing.html",{
                "visitedListing": visitedListing,
                "categories": categories,
                "leadBidder": leadBidder
            })

        elif method == "patch":
            pass

        elif method == "postComment":*
            pass

        elif method == "delete":
            user = request.user
            user.watchlist.remove(visitedListing)
            util.checkHighest(visitedListing)
            
            for bid in Bid.objects.filter(bidder=request.user.id):
                if visitedListing.highestBid == bid.amount:
                    leadBidder = True

            return render(request, "auctions/listing.html",{
                "visitedListing": visitedListing,
                "categories": categories,
                "leadBidder": leadBidder
            })
  
        elif method == "post":
            try:
                bidAmount = float(request.POST["listingBid"])

                if visitedListing.highestBid:
                    if bidAmount <= visitedListing.highestBid:
                        return render(request, "auctions/error.html", {
                            "error": "Your bid was too low"
                        })
                elif bidAmount <= visitedListing.price:
                    return render(request, "auctions/error.html", {
                        "error": "Your bid was too low"
                    })

                newBid = Bid(bidder=request.user, listing=Listing.objects.get(id=id), amount=bidAmount)
            except Exception as error:
                return render(request, "auctions/error.html", {
                    "error": error
                })

            newBid.save()
            visitedListing.highestBid = bidAmount
            visitedListing.save()

            util.checkHighest(visitedListing)
            
            for bid in Bid.objects.filter(bidder=request.user.id):
                if visitedListing.highestBid == bid.amount:
                    leadBidder = True    
                
            return render(request, "auctions/listing.html",{
                "visitedListing": visitedListing,
                "categories": categories,
                "leadBidder": leadBidder
            })

    else:
        util.checkHighest(visitedListing)
        
        for bid in Bid.objects.filter(bidder=request.user.id):
            if visitedListing.highestBid == bid.amount:
                leadBidder = True

        return render(request, "auctions/listing.html",{
            "visitedListing": visitedListing,
            "categories": categories,
            "leadBidder": leadBidder
        })

@login_required(login_url='/login')
def watchlist(request):
    watchlisted = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlisted": watchlisted
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
            tag = Category.objects.get(tag=search)
            taggedListings = Listing.objects.filter(categories=tag)

        except Exception as error:
            return render(request, "auctions/error.html", {
                "error": error
            })
        

        return render(request, "auctions/displayCategory.html", {
            "taggedListings": taggedListings
        })

    