from django.contrib import admin
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


admin.site.register(GameNomination)
admin.site.register(Event, EventAdmin)
admin.site.register(Game)
admin.site.register(Group, GroupAdmin)  
admin.site.register(EventAttendance)
admin.site.register(EventLocation)
admin.site.register(GroupMembers)
admin.site.register(UserProfile)
admin.site.register(GameSignup)
    
