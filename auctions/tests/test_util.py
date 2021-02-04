from django.test import TestCase
from auctions.util import checkHighest, checkLeadBidder, checkValidBid
from auctions import models

class TestUtil(TestCase):

    def testCheckHighestWithHighestBid(self):
        TestUser1 = models.User.objects.create_user("testUser1", "testUser1@email.com", password="testPassword")
        TestListing1 = models.Listing.objects.create(creator=TestUser1, title="testListing", price=150, highestBid=200)
        TestBidHighest = models.Bid.objects.create(amount=999, bidder=TestUser1, listing=TestListing1)

        checkHighest(TestListing1)

        self.assertEquals(TestListing1.highestBid, TestBidHighest.amount)

    def testCheckHighestWithoutHighestBid(self):
        TestUser1 = models.User.objects.create_user("testUser1", "testUser1@email.com", password="testPassword")
        TestListing1 = models.Listing.objects.create(creator=TestUser1, title="testListing", price=150)
        TestBidHighest = models.Bid.objects.create(amount=999, bidder=TestUser1, listing=TestListing1)

        checkHighest(TestListing1)

        self.assertEquals(TestListing1.highestBid, None)


    def testCheckLeadBidderTrue(self):
        TestUser1 = models.User.objects.create_user("testUser1", "testUser1@email.com", password="testPassword")
        TestListing1 = models.Listing.objects.create(creator=TestUser1, title="testListing", price=150, highestBid=999)
        TestUser2 = models.User.objects.create_user("testUser2", "testUser2@email.com", password="testPassword")
        TestBid1 = models.Bid.objects.create(amount=200, bidder=TestUser1, listing=TestListing1)
        TestBid2 = models.Bid.objects.create(amount=500, bidder=TestUser1, listing=TestListing1)
        TestBidHighest = models.Bid.objects.create(amount=999, bidder=TestUser2, listing=TestListing1)

        userBids = models.Bid.objects.filter(bidder=TestUser2)

        self.assertTrue(checkLeadBidder(userBids, TestListing1))

    def testCheckLeadBidderFalse(self):
        TestUser1 = models.User.objects.create_user("testUser1", "testUser1@email.com", password="testPassword")
        TestListing1 = models.Listing.objects.create(creator=TestUser1, title="testListing", price=150, highestBid=999)
        TestUser2 = models.User.objects.create_user("testUser2", "testUser2@email.com", password="testPassword")
        TestBid1 = models.Bid.objects.create(amount=200, bidder=TestUser1, listing=TestListing1)
        TestBid2 = models.Bid.objects.create(amount=500, bidder=TestUser1, listing=TestListing1)
        TestBidHighest = models.Bid.objects.create(amount=999, bidder=TestUser2, listing=TestListing1)

        userBids = models.Bid.objects.filter(bidder=TestUser1)

        self.assertFalse(checkLeadBidder(userBids, TestListing1))

    def testCheckValidBidTrue(self):
        TestUser1 = models.User.objects.create_user("testUser1", "testUser1@email.com", password="testPassword")
        TestListing1 = models.Listing.objects.create(creator=TestUser1, title="testListing", price=150, highestBid=200)

        self.assertTrue(checkValidBid(TestListing1, 999))

    def testCheckValidBidFalse(self):
        TestUser1 = models.User.objects.create_user("testUser1", "testUser1@email.com", password="testPassword")
        TestListing1 = models.Listing.objects.create(creator=TestUser1, title="testListing", price=150, highestBid=200)

        self.assertFalse(checkValidBid(TestListing1, 1))