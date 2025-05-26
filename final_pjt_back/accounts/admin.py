from django.contrib import admin
from .models import User, Profile, FavoriteChannel, FavoriteVideo

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(FavoriteChannel)
admin.site.register(FavoriteVideo)
