from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import Event, Category, EventPost, EventPostComment, GroupPost, GroupPostComment, Tag, Game, Group, EventAttendance, GroupLocation, GroupMembers, UserProfile, EventLocation, GameSignup, GameComment, Vote


class GroupLocationInline(admin.StackedInline):
    model = GroupLocation
    can_delete = False  # Prevents deletion of existing GroupLocation from Group admin
    verbose_name_plural = 'Group Location'  # Display name for inline

class GroupAdmin(admin.ModelAdmin):
    inlines = [GroupLocationInline]
    prepopulated_fields = {'slug': ('name',)}

    
class EventAttendanceInline(admin.TabularInline):
    model = EventAttendance
    extra = 1  # Display one extra blank form by default

class EventLocationInline(admin.StackedInline):
    model = EventLocation
    can_delete = False  # Prevents deletion of existing EventLocation from Event admin
    verbose_name_plural = 'Event Location'  # Display name for inline

class EventAdmin(admin.ModelAdmin):
    inlines = [EventAttendanceInline, EventLocationInline]

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


admin.site.register(Event, EventAdmin)
admin.site.register(Game)
admin.site.register(Vote)
admin.site.register(GroupPost)
admin.site.register(GroupPostComment)
admin.site.register(EventPost)
admin.site.register(EventPostComment)
admin.site.register(Group, GroupAdmin)  
admin.site.register(EventAttendance)
admin.site.register(EventLocation)
admin.site.register(GroupMembers)
admin.site.register(GameSignup)
admin.site.register(GameComment)
admin.site.register(Category)
admin.site.register(Tag)

    
