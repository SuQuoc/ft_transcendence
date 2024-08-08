from django.contrib import admin
from friends.models import FriendList
from friends.models import FriendRequest

# Register your models here.


class FriendListAdmin(admin.ModelAdmin):
    list_filter = ["user"]
    list_display = ["user"]
    search_fields = ["user"]
    readonly_fields = ["user"]

    class Meta:
        model = FriendList


admin.site.register(FriendList, FriendListAdmin)


class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ["sender", "receiver"]
    list_display = ["sender", "receiver"]
    search_fields = ["sender__displayname", "receiver__displayname"]

    class Meta:
        model = FriendRequest


admin.site.register(FriendRequest, FriendRequestAdmin)
