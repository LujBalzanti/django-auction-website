from django.test import TestCase, Client
from django.urls import reverse
from auctions.models import Category, Listing, Bid, Comment, User


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()

        self.userInfo = {
            'username': "testUser", 
            'password': "testPass",
            'email': "testUser@testEmail.com"
        }
        self.userInfoUnregistered = {
            'username': "testUser2", 
            'password': "testPass2",
            'confirmation': 'testPass2',
            'email': "testUser@testEmail.com"
        }
        self.listingInfo = {
            'listingTitle': "test title",
            'listingDescription': "test description: It's slightly longer than the title",
            'listingPrice': 250,
            'listingCategories': [],
            'listingPhotoUrl': ''
        }

        User.objects.create_user(**self.userInfo)

        self.testUser = User.objects.create(
            username="testUser3", 
            password="testPass3", 
            email="testUser@testEmail.com"
            )
        self.testCategory1 = Category.objects.create(tag="testTag") 
        self.testListing = Listing.objects.create(
            creator = self.testUser,
            title="test title",
            description="test description: It's slightly longer than the title",
            price=250,
        )
        self.testListing.categories.set([self.testCategory1])
        self.testUser.watchlist.set([self.testListing])

        self.indexViewUrl = reverse('index')
        self.loginViewUrl = reverse('login')
        self.logoutViewUrl = reverse('logout')
        self.registerViewUrl = reverse('register')
        self.createListingViewUrl = reverse('createListing')
        self.watchlistViewUrl = reverse('watchlist')
        self.watchlistCategoryViewUrl = reverse('watchlistCategory', args=["testTag"]) 
        self.categoriesViewUrl = reverse('categories')
        self.displayCategoryViewUrl = reverse('search', args=["testTag"])
        self.displayUserListingCategoryViewUrl = reverse('displayUserListingCategory', args=["testTag"]) 
        self.userListingsViewUrl = reverse('userListings')
        self.listingViewUrl = reverse('listing', args=[1]) 

    def testIndexViewGET(self):
        response = self.client.get(self.indexViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/index.html')

    def testLoginViewGET(self):
        response = self.client.get(self.loginViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/login.html')

    def testLoginViewCorrectLoginPOST(self):
        response = self.client.post(self.loginViewUrl, self.userInfo, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, '/')
        self.assertTemplateUsed(response, 'auctions/index.html')
        self.assertTrue(response.context['user'].is_authenticated)

    def testLoginViewWrongLoginPOST(self):
        response = self.client.post(self.loginViewUrl, {
            'username': 'wrongUsername',
            'password': 'wrongPass',
            }, 
            follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/login.html')
        self.assertFalse(response.context['user'].is_authenticated)
    
    def testLogoutViewGET(self):
        response = self.client.get(self.logoutViewUrl)

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/')
            
    def testRegisterViewGET(self):
        response = self.client.get(self.registerViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/register.html')
    
    def testRegisterViewSuccessfulRegistrationPOST(self):
        response = self.client.post(self.registerViewUrl, self.userInfoUnregistered, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, '/')
        self.assertTemplateUsed(response, 'auctions/index.html')
        self.assertTrue(response.context['user'].is_authenticated)

    def testRegisterViewIncorrectConfirmationPOST(self):
        self.userInfoUnregistered['confirmation'] = 'wrongPass'
        response = self.client.post(self.registerViewUrl, self.userInfoUnregistered, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/register.html')
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEquals(response.context['message'], 'Passwords must match.')

    def testRegisterViewDuplicateUsernamePOST(self):
        self.userInfoUnregistered['username'] = 'testUser'
        response = self.client.post(self.registerViewUrl, self.userInfoUnregistered, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/register.html')
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEquals(response.context['message'], 'Username already taken.')

    def testCreateListingViewNotLoggedInGET(self):
        response = self.client.get(self.createListingViewUrl)

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/login?next=/createListing')
    
    def testCreateListingViewGET(self):
        self.client.login(**self.userInfo)
        response = self.client.get(self.createListingViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/createListing.html')

    def testCreateListingViewSuccessfulPOST(self):
        self.client.login(**self.userInfo)
        response = self.client.post(self.createListingViewUrl, self.listingInfo)

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/')

    def testCreateListingViewCategoryErrorPOST(self):
        self.client.login(**self.userInfo)
        self.listingInfo['listingCategories'] = ['MissingCategory']

        response = self.client.post(self.createListingViewUrl, self.listingInfo)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/error.html')
        self.assertTrue(response.context['error'])

    def testCreateListingViewCreationErrorPOST(self):
        self.client.login(**self.userInfo)
        self.listingInfo['listingPrice'] = -500

        response = self.client.post(self.createListingViewUrl, self.listingInfo)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/error.html')
        self.assertTrue(response.context['error'])
        
    def testWatchlistViewGET(self):
        self.client.login(**self.userInfo)
        response = self.client.get(self.watchlistViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/watchlist.html')
    
    def testCategoryViewGET(self):
        response = self.client.get(self.categoriesViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/categories.html')

    def testUserListingsViewGET(self):
        self.client.login(**self.userInfo)
        response = self.client.get(self.userListingsViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/userListings.html')
    
    def testWatchlistCategoryViewGET(self):
        self.client.login(**self.userInfo)
        response = self.client.get(self.watchlistCategoryViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/watchlist.html')
        self.assertEquals(response.context['displayCategory'], 'testTag')

    def testDisplayCategoryViewGET(self):
        response = self.client.get(self.displayCategoryViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/displayCategory.html')
        self.assertEquals(response.context['displayCategory'], 'testTag')
    
    def testDisplayCategoryViewMissingCategoryGET(self):
        response = self.client.get(reverse('search', args=["MissingTag"]))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/error.html')
        self.assertTrue(response.context['error'])

    def testUserListingCategoryViewGET(self):
        self.client.login(**self.userInfo)
        response = self.client.get(self.displayUserListingCategoryViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/userListings.html')
        self.assertEquals(response.context['displayCategory'], 'testTag')

    def testUserListingCategoryViewMissingCategoryGET(self):
        self.client.login(**self.userInfo)
        response = self.client.get(reverse('displayUserListingCategory', args=["MissingTag"]))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/error.html')
        self.assertTrue(response.context['error'])

    def testListingViewGET(self):
        response = self.client.get(self.listingViewUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing.html')

    def testListingViewAddToWatchlistPOST(self):
        self.client.login(**self.userInfo)
        response = self.client.post(self.listingViewUrl, {'_method': "addToWatchlist"})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing.html')
        self.assertEquals(response.context['user'].watchlist.count(), 1)

    def testListingViewCloseAuctionPOST(self):
        self.client.login(**self.userInfo)
        response = self.client.post(self.listingViewUrl, {'_method': "closeAuction"})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing.html')
        self.assertFalse(response.context['visitedListing'].isActive)

    def testListingViewPostCommentSuccessfulPOST(self):
        self.client.login(**self.userInfo)
        response = self.client.post(self.listingViewUrl, {
            '_method': "postComment",
            "content": "TestContent"
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing.html')
        self.assertEquals(response.context['comments'].count(), 1)

    def testListingViewPostCommentInvalidPOST(self):
        self.client.login(**self.userInfo)
        response = self.client.post(self.listingViewUrl, {
            '_method': "postComment",
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/error.html')
        self.assertEquals(response.context['error'], "Comment invalid, limit yourself to 280 characters per comment")

    def testListingViewRemoveFromWatchlistPOST(self):
        self.client.force_login(self.testUser)
        response = self.client.post(self.listingViewUrl, {'_method': "removeFromWatchlist"})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing.html')
        self.assertEquals(response.context['user'].watchlist.count(), 0)

    def testListingViewPlaceBidSuccessfulPOST(self):
        self.client.login(**self.userInfo)
        response = self.client.post(self.listingViewUrl, {
            '_method': "placeBid",
            'listingBid': 500
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/listing.html')
        self.assertEquals(response.context['visitedListing'].highestBid, 500)

    def testListingViewPlaceBidTooLowPOST(self):
        self.client.login(**self.userInfo)
        response = self.client.post(self.listingViewUrl, {
            '_method': "placeBid",
            'listingBid': 200
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/error.html')
        self.assertEquals(response.context['error'], "Your bid was too low")

    def testListingViewPlaceBidInvalidPOST(self):
        self.client.login(**self.userInfo)
        response = self.client.post(self.listingViewUrl, {
            '_method': "placeBid",
            'listingBid': "Invalid"
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'auctions/error.html')
        self.assertTrue(response.context['error'])
