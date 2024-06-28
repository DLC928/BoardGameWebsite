from django.contrib import admin
from .models import Event, Game, Group, EventAttendance, GroupMembers, UserProfile, Nomination

class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    
class EventAttendanceInline(admin.TabularInline):
    model = EventAttendance
    extra = 1  # Display one extra blank form by default

class EventAdmin(admin.ModelAdmin):
    inlines = [EventAttendanceInline]
    # Other admin options for Event model display

admin.site.register(Event, EventAdmin)
admin.site.register(Game)
admin.site.register(Group, GroupAdmin)  # Register Group with GroupAdmin configuration
admin.site.register(EventAttendance)
admin.site.register(GroupMembers)
admin.site.register(UserProfile)
admin.site.register(Nomination)

    
