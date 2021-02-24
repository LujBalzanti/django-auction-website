from django.test import TestCase
from django.db import models
from auctions.models import User, Category, Listing, Bid, Comment 
from django.forms import ValidationError

class TestModels(TestCase):

    def setUp(self):
        self.testUser = User.objects.create(
            username="testUser", 
            password="testPass", 
            email="testUser@testEmail.com"
            )

        self.testDeletedUser = User.objects.create(
            username="deleted",
            password="testPass",
            email="testUser@testEmail.com"
        )

        self.testCategory1 = Category.objects.create(tag="testTag")
        self.testCategory2 = Category.objects.create()

        self.testListing = Listing.objects.create(
            creator = self.testUser,
            title="test title",
            description="test description: It's slightly longer than the title",
            price=250,
            highestBid=500
        )
        self.testListing.categories.set([self.testCategory1, self.testCategory2])

        self.testBid = Bid.objects.create(
            amount=500,
            bidder=self.testUser,
            listing=self.testListing
        )

        self.testComment = Comment.objects.create(
            listing=self.testListing,
            content="test content",
            commentor=self.testUser    
        )

    def testListingWithNegativePrice(self):
        testNegativePriceListing = Listing.objects.create(creator = self.testUser,
            title="test title",
            description="test description: It's slightly longer than the title",
            price=-550)

        self.assertRaises(ValidationError, testNegativePriceListing.full_clean)

    def testListingHasCategories(self):
        self.assertEquals(self.testListing.categories.count(), 2)
    
    def testListingHasCreator(self):
        self.assertEquals(self.testListing.creator, self.testUser)
    
    def testListingStr(self):
        self.assertEquals(str(self.testListing), "test title")
    
    def testListingUsd(self):
        self.assertEquals(self.testListing.usd(), "$250.00")

    def testListingUsdBid(self):
        self.assertEquals(self.testListing.usdBid(),"$500.00")

    def testCategoryStr(self):
        self.assertEquals(str(self.testCategory1), "testTag")

    def testBidHasListing(self):
        self.assertEquals(self.testBid.listing, self.testListing)

    def testBidStr(self):
        self.assertEquals(str(self.testBid), "500")

    def testBidUsd(self):
        self.assertEquals(self.testBid.usd(),"$500.00")

    def testCommentHasListing(self):
        self.assertEquals(self.testComment.listing, self.testListing)
    
    def testCommentHasCommentor(self):
        self.assertEquals(self.testComment.commentor, self.testUser)
    
    def testCommentStr(self):
        self.assertEquals(str(self.testComment), 'Comment test content by testUser') 
   
    def testCommentHasDeletedCommentor(self):
        self.assertEquals(self.testComment.get_deleted_user(), self.testDeletedUser)
          
        

    