from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

# UserProfile model to store additional user information
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

# Group model
class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=255)
    members = models.ManyToManyField(User, through='GroupMembers')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # Save without slug to get an ID
            super(Group, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{self.id}"
            self.save()  # Save again to update slug
        super(Group, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

# GroupMember model to handle the relationship between users and groups
class GroupMembers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
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
    location = models.CharField(max_length=255)
    attendees = models.ManyToManyField(User, through='EventAttendance')

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

# Game model to store game details
class Game(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    play_time = models.CharField(max_length=100)
    player_count = models.CharField(max_length=100)
    difficulty_rating = models.FloatField()

    def __str__(self):
        return self.name

# Nomination model to handle the relationship between events and games
class Nomination(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    nominator = models.ForeignKey(User, on_delete=models.CASCADE)
    date_nominated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'game')

    def __str__(self):
        return f"{self.game.name} nominated for {self.event.title}"
