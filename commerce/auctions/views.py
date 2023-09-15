from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listings, Bids, Comments


def index(request):
    return render(request, "auctions/index.html", {"listings": Listings.objects.all(),
                                                   "bids": Bids.objects.all()})


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
    return HttpResponseRedirect(reverse("login"))


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

@login_required(login_url='auctions/login.html')
def create(request):
    if request.method == "POST":
        # post - create a new listing in db
        data = request.POST
        info = {
            "title": data.get("title"),
            "description": data.get("description"),
            "startingBid": data.get("startBid"),
            "url": "https://static.vecteezy.com/system/resources/previews/005/337/799/original/icon-image-not-found-free-vector.jpg",
            "category": ""
        }
        if data.get("url") != "":
            info["url"] = data.get("url")
        if data.get("category"):
            info["category"] = data.get("category")

        listingObj = Listings(user=request.user, 
                           title=info["title"],
                           description=info["description"], 
                           startingBid=info["startingBid"],
                           imageURL=info["url"],
                           category=info["category"]
                           )
        listingObj.save()

        startingBid = Bids(user=request.user, amount=info["startingBid"], listing=listingObj)
        startingBid.save()

        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "auctions/createListing.html")
    
def listing(request, id):
    listingObject = Listings.objects.get(pk=id)
    currentBid = Bids.objects.get(listing=listingObject)
    comments = Comments.objects.filter(listing=listingObject).order_by("-id")
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            return render(request, "auctions/login.html")
        userBid = float(request.POST.get("bid"))
        if userBid >= float(currentBid.amount):
            currentBid.user = request.user
            currentBid.amount = userBid
            currentBid.save()
            listingObject.bidCount += 1
            listingObject.save()
            return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
    user = request.user
    isWatching = False
    try:
        if user.watchlist.get(pk=id):
            isWatching = True
    except:
        pass

    return render(request, "auctions/listing.html", {"listing": listingObject,
                                                     "user": request.user,
                                                     "bid": currentBid,
                                                     "lowestBid": str(float(currentBid.amount)+0.01),
                                                     "isWatching": isWatching,
                                                     "comments": comments})

@login_required(login_url='auctions/login.html')
def close(request, id):
    if request.method == "POST":
        listingObject = Listings.objects.get(pk=id)
        listingObject.winner = request.user.username
        listingObject.save()
    return render(request, "auctions/index.html")

def categories(request):
    if request.method == "POST":
        #post
        categoryValue = request.POST.get("category").title()
        listingMatches = Listings.objects.filter(category=categoryValue)
        noMatches = False
        if len(listingMatches) == 0:
            noMatches = True
        return render(request, "auctions/categories.html", {"categories": listingMatches,
                                                            "bids": Bids.objects.all(),
                                                            "noMatches": noMatches})

    return render(request, "auctions/categories.html")

@login_required(login_url='auctions/login.html')
def watchlist(request):
    userWatchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"watchlist": userWatchlist,
                                                       "bids": Bids.objects.all()})

@login_required(login_url='auctions/login.html')
def toggleWatch(request, id):
    user = request.user
    listing = Listings.objects.get(pk=id)
    try:
        if user.watchlist.get(pk=id):
            user.watchlist.remove(listing)
            user.save()
    except:
        user.watchlist.add(listing)
        user.save()
    return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))

@login_required(login_url='auctions/login.html')
def comment(request, id):
    if request.method == "POST":
        listing = Listings.objects.get(pk=id)
        commentText = request.POST.get("text")
        commentObj = Comments(user=request.user, comment=commentText, listing=listing)
        commentObj.save()
        return HttpResponseRedirect(reverse("listing", kwargs={"id": id}))
