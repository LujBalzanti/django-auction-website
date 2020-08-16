from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
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
    visitedListing = Listing.objects.get(id=id)
    categories = visitedListing.categories.all()
    
    if request.method == "POST":
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

        try:
            newBid = Bid(bidder=request.user, listing=Listing.objects.get(id=id), amount=bidAmount)
        except Exception as error:
            return render(request, "auctions/error.html", {
                "error": error
            })

        newBid.save()
        visitedListing.highestBid = bidAmount
        visitedListing.save()

        util.checkHighest(visitedListing)
        leadBidder = False
        
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
        leadBidder = False
        
        for bid in Bid.objects.filter(bidder=request.user.id):
            if visitedListing.highestBid == bid.amount:
                leadBidder = True

        return render(request, "auctions/listing.html",{
            "visitedListing": visitedListing,
            "categories": categories,
            "leadBidder": leadBidder
        })