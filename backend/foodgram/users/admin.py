from django.contrib import admin
from django.contrib.auth.models import Group

from .models import CustomUser, Follower


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username',)
    search_fields = ('email__startswith', 'username__startswith')


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Group)
