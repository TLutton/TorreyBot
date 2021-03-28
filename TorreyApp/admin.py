from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from TorreyApp.models import Golfer

# Define an inline admin descriptor for Golfer model
# which acts a bit like a singleton

class GolferInline(admin.StackedInline):
    model = Golfer
    can_delete = False
    verbose_name_plural = 'golfer'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (GolferInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
