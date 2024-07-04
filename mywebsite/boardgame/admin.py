from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import Event, Game, Group, EventAttendance, GroupMembers, UserProfile, GameNomination, EventLocation, GameSignup

class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    
class EventAttendanceInline(admin.TabularInline):
    model = EventAttendance
    extra = 1  # Display one extra blank form by default

class GameNominationInline(admin.TabularInline):
    model = GameNomination
    extra = 1  # Display one extra blank form by default


class EventAdmin(admin.ModelAdmin):
    inlines = [EventAttendanceInline,GameNominationInline]


# Add profile information to user model
class UserProfileInline(admin.StackedInline):
    model = UserProfile

# Extend from the default UserAdmin
class CustomUserAdmin(DefaultUserAdmin):
    inlines = [UserProfileInline]

# Unregister the default User model
admin.site.unregister(User)

# Register the User model with the custom UserAdmin
admin.site.register(User, CustomUserAdmin)


admin.site.register(GameNomination)
admin.site.register(Event, EventAdmin)
admin.site.register(Game)
admin.site.register(Group, GroupAdmin)  
admin.site.register(EventAttendance)
admin.site.register(EventLocation)
admin.site.register(GroupMembers)
admin.site.register(GameSignup)
    
