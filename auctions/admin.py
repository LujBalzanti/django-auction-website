from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Bid, Category, Listing, Comment

admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Category)
admin.site.register(Listing)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('commentor', 'content', 'listing', 'date', 'active')
    list_filter = ('active', 'date')
    search_fields = ('commentor', 'content')
    actions = ['approveComments']

    def approveComments(self, request, queryset):
        queryset.update(active=True)