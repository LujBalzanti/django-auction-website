from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Bid, Category, Listing, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Comment)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('commentor', 'content', 'listing', 'date', 'active')
    list_filter = ('active', 'date')
    search_fields = ('commentor', 'content')
    actions = ['approveComments']

    def approveComments(self, request, queryset):
        queryset.update(active=True)