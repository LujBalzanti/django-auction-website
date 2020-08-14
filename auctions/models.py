from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    tag = models.CharField(max_length=35)

class Listing(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=1000, default="")
    price = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    photo = models.URLField(null=True, default=None)
    categories = models.ManyToManyField(Category, related_name="listings")

class User(AbstractUser):
    watchlist = models.ManyToManyField(Listing)
    pass

class Bid(models.Model):
    amount = models.FloatField()
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    listingId = models.ForeignKey(Listing, related_name="bids", on_delete=models.CASCADE)

class Comment(models.Model):
    listingId = models.ForeignKey(Listing, related_name="comments", on_delete=models.CASCADE)
    date = models.DateTimeField()
    content = models.TextField(max_length=280)

    def get_deleted_user():
        return User.objects.get(username="deleted")
    
    userID = models.ForeignKey(User, on_delete=models.SET(get_deleted_user))
