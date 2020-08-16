from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", related_name="listed")
    pass

class Category(models.Model):
    tag = models.CharField(max_length=35)
    def __str__(self):
        return self.tag

class Listing(models.Model):
    creator = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="userListings")
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=1000, default="")
    price = models.FloatField(default=0)
    isActive = models.BooleanField(default=True)
    photoUrl = models.URLField(blank=True, null=True)
    highestBid = models.FloatField(blank=True, max_length=11, null=True)
    categories = models.ManyToManyField(Category, related_name="categories")
    def __str__(self):
        return self.title

    def usd(self):
        return f"${self.price:,.2f}"
    
    def usdBid(self):
        return f"${self.highestBid:,.2f}"

class Bid(models.Model):
    amount = models.FloatField()
    bidder = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name="bids", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.amount)

    def usd(self):
        return f"${self.amount:,.2f}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, related_name="comments", on_delete=models.CASCADE)
    date = models.DateTimeField()
    content = models.TextField(max_length=280)

    def __str__(self):
        return str(self.date)

    def get_deleted_user():
        return User.objects.get(username="deleted")
    
    commentor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET(get_deleted_user))
