from django.contrib import admin
from .models import Event, Game, Group, EventAttendance, GroupMembers, Profile, Nomination

class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Event)
admin.site.register(Game)
admin.site.register(Group, GroupAdmin)  # Register Group with GroupAdmin configuration
admin.site.register(EventAttendance)
admin.site.register(GroupMembers)
admin.site.register(Profile)
admin.site.register(Nomination)

    
