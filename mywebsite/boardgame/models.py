import os
from tempfile import NamedTemporaryFile
from django.db import models
from django.core.files import File
import requests
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

# UserProfile model to store additional user information
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username
    
# Create profile when new user signs up 
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(User, through='GroupMembers')
    slug = models.SlugField(unique=True)
    group_image = models.ImageField(upload_to='group_images/', null=True, blank=True)
    TYPE_SELECT = (
        ('Public', 'Public'),
        ('Private', 'Private'),
    )
    group_privacy = models.CharField(max_length=10,choices=TYPE_SELECT,default='Public')
    categories = models.ManyToManyField(Category, related_name='groups', blank=True)
    tags = models.ManyToManyField(Tag, related_name='groups', blank=True)
    
    def save(self, *args, **kwargs):
        if not self.id:
            super(Group, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{self.id}"
            self.save()
        super(Group, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class GroupLocation(models.Model):
    group = models.OneToOneField('Group', on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    sublocality = models.CharField(max_length=100, blank=True)  # neighborhoods or sublocalities
    state = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    def __str__(self):
        return f"{self.city}, {self.state if self.state else ''}, {self.country}"


# GroupMember model to handle the relationship between users and groups
class GroupMembers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group,related_name='group_members', on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = 'GroupMembers'
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"
    
# Event model
class Event(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date_time = models.DateTimeField()
    attendees = models.ManyToManyField(User, through='EventAttendance')
    event_image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='events', blank=True)
    tags = models.ManyToManyField(Tag, related_name='events', blank=True)
    nominations_open = models.BooleanField(default=True)
    signups_open = models.BooleanField(default=False)
    admin_only_nominations = models.BooleanField(default=False)
    skip_nominations = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.title} by {self.group.name}"

# EventAttendance model to handle the relationship between users and events
class EventAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'EventAttendance'
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} attending {self.event.title}"

class EventLocation(models.Model):
    event = models.OneToOneField('Event', on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    sublocality = models.CharField(max_length=100, blank=True)  # neighborhoods or sublocalities
    state = models.CharField(max_length=100, blank=True, null=True)  # Nullable state field
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.country}"

class Game(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='nominated_games')
    nominator = models.ForeignKey(User, on_delete=models.CASCADE)
    date_nominated = models.DateTimeField(auto_now_add=True,)
    TYPE_SELECT = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Deleted', 'Deleted'),
    )
    nomination_status = models.CharField(max_length=10,choices=TYPE_SELECT,default='Pending')
    name = models.CharField(max_length=200)
    min_players = models.PositiveIntegerField(blank=True, null=True)
    max_players = models.PositiveIntegerField(blank=True, null=True)
    min_playtime = models.PositiveIntegerField(blank=True, null=True)
    max_playtime = models.PositiveIntegerField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    weight = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    thumbnail_file = models.ImageField(upload_to='game_thumbnails/', blank=True, null=True)

    class Meta:
        unique_together = ('event', 'name')

    def __str__(self):
        return f"{self.name} nominated for {self.event.title}"
    
    def save(self, *args, **kwargs):
        # Check if there's an image URL and no image file is set
        if self.thumbnail_url and not self.thumbnail_file:
            response = requests.get(self.thumbnail_url)
            if response.status_code == 200:
                # Create a temporary file to store the image data
                image = NamedTemporaryFile(delete=True)
                image.write(response.content)
                image.flush()
                
                # Save the image to the ImageField
                self.thumbnail_file.save(
                    os.path.basename(self.thumbnail_url),  # File name derived from URL
                    File(image)  # File object containing image data
                )
        super().save(*args, **kwargs)

            
class GameSignup(models.Model):
    nomination = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_signed_up = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('nomination', 'user')

    def __str__(self):
        return f"{self.user.username} signed up for {self.nomination.name} at {self.nomination.event.title}"


class GameComment(models.Model):
    nominated_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.nominated_game.name}"    

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} voted for {self.game.name} in event {self.event.id}"

