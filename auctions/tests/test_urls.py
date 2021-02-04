from django.test import SimpleTestCase
from django.urls import reverse, resolve
from auctions import views

class TestUrls(SimpleTestCase):

    def testIndexUrlResolves(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, views.index)

    def testLoginUrlResolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, views.login_view)
        
    def testLogoutUrlResolves(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, views.logout_view)

    def testRegisterUrlResolves(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, views.register)
    
    def testCreateListingUrlResolves(self):
        url = reverse('createListing')
        self.assertEquals(resolve(url).func, views.createListing)
    
    def testListingUrlResolves(self):
        url = reverse('listing', args=[1])
        self.assertEquals(resolve(url).func, views.listing)

    def testWatchlistUrlResolves(self):
        url = reverse('watchlist')
        self.assertEquals(resolve(url).func, views.watchlist)

    def testCategoriesUrlResolves(self):
        url = reverse('categories')
        self.assertEquals(resolve(url).func, views.categories)

    def testSearchUrlResolves(self):
        url = reverse('search', args=["some search"])
        self.assertEquals(resolve(url).func, views.displayCategory)
    
    def testWatchlistCategoryUrlResolves(self):
        url = reverse('watchlistCategory', args=["some category"])
        self.assertEquals(resolve(url).func, views.watchlistCategory)

    def testMyListingsUrlResolves(self):
        url = reverse('userListings')
        self.assertEquals(resolve(url).func, views.userListings)

    def testMyListingsCategoryUrlResolves(self):
        url = reverse('displayUserListingCategory', args=["some category"])
        self.assertEquals(resolve(url).func, views.displayUserListingCategory)

    


    