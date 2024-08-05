from django import template
from boardgame.models import Notification

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def unread_notifications_count(user):
    if user.is_authenticated:
        return Notification.objects.filter(user=user, read=False).count()
    return 0