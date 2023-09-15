from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listings', blank=True, related_name='watchlist')

class Listings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    title = models.CharField(max_length=64)
    description = models.TextField()
    startingBid = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    imageURL = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    bidCount = models.IntegerField(default=0)
    winner = models.CharField(max_length=64, blank=True, null=True, default="None")

class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bid")

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comment")