from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Event, EventAttendance, EventLocation, EventPost, EventPostComment, Game, GameComment, GameSignup, Group, Category, GroupLocation, GroupMembers, GroupPost, GroupPostComment, Notification, Tag, UserProfile, Vote, Waitlist
from django.utils import timezone
from unittest.mock import patch

#-------------------GROUP TESTING-------------------------------
class GroupModelTest(TestCase):
    
    def setUp(self):
        # Create object instances for testing
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.category = Category.objects.create(name='Category1')
        self.tag = Tag.objects.create(name='Tag1')

    def test_group_creation(self):
        group = Group.objects.create(
            name='Test Group',
            description='This is a test group'
        )
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(group.description, 'This is a test group')
        self.assertEqual(group.slug, 'test-group')
        self.assertEqual(group.group_privacy, 'Public')

    def test_group_slug_generation(self):
        group1 = Group.objects.create(name='Test Group')
        self.assertEqual(group1.slug, 'test-group')
        
        group2 = Group.objects.create(name='Test Group')
        self.assertEqual(group2.slug, 'test-group-1')

    def test_group_privacy_default(self):
        group = Group(name='Privacy Default Group', description='Test default privacy.')
        group.save()
        self.assertEqual(group.group_privacy, 'Public')

    def test_group_image_upload(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        group = Group.objects.create(name='Image Group', group_image=image)
        self.assertTrue(group.group_image.name.startswith('group_images/'))

    def test_group_add_members(self):
        group = Group.objects.create(
            name='Group with Members',
            description='This group has members.',
            group_privacy='Public'
        )
        group.members.add(self.user1, self.user2)
        self.assertIn(self.user1, group.members.all())
        self.assertIn(self.user2, group.members.all())

    def test_group_add_categories(self):
        group = Group.objects.create(
            name='Group with Categories',
            description='This group has categories.',
            group_privacy='Public'
        )
        group.categories.add(self.category)
        self.assertIn(self.category, group.categories.all())

    def test_group_add_tags(self):
        group = Group.objects.create(
            name='Group with Tags',
            description='This group has tags.',
            group_privacy='Public'
        )
        group.tags.add(self.tag)
        self.assertIn(self.tag, group.tags.all())

    def test_group_unique_slug(self):
        group1 = Group.objects.create(name='Test Group')
        group2 = Group.objects.create(name='Test Group')
        group3 = Group.objects.create(name='Test Group')
        self.assertEqual(group1.slug, 'test-group')
        self.assertEqual(group2.slug, 'test-group-1')
        self.assertEqual(group3.slug, 'test-group-2')

class GroupLocationTest(TestCase):
    
    # Create object instances for testing
    def setUp(self):
        self.group = Group.objects.create(name='Test Group')  

    def test_create_group_location(self):
        location = GroupLocation.objects.create(
            group=self.group,
            city='Test City',
            sublocality='Test Sublocality',
            state='Test State',
            postcode='12345',
            country='Test Country',
            latitude=40.7728,
            longitude=-64.0050
        )
        
        self.assertEqual(location.group, self.group)
        self.assertEqual(location.city, 'Test City')
        self.assertEqual(location.sublocality, 'Test Sublocality')
        self.assertEqual(location.state, 'Test State')
        self.assertEqual(location.postcode, '12345')
        self.assertEqual(location.country, 'Test Country')
        self.assertEqual(location.latitude, 40.7728)
        self.assertEqual(location.longitude, -64.0050)

    def test_blank_fields(self):
        location = GroupLocation.objects.create(
            group=self.group,
            city='Test City',
            country='Test Country'
        )
        self.assertEqual(location.city, 'Test City')
        self.assertEqual(location.sublocality, '')
        self.assertEqual(location.state, '')
        self.assertEqual(location.postcode, '')
        self.assertEqual(location.country, 'Test Country')
        self.assertIsNone(location.latitude)
        self.assertIsNone(location.longitude)

    def test_latitude_longitude(self):
        location = GroupLocation.objects.create(
            group=self.group,
            city='Test City',
            country='Test Country',
            latitude=27.124500,
            longitude=-182.415400
        )
        self.assertEqual(location.latitude, 27.124500)
        self.assertEqual(location.longitude, -182.415400)
    
    def test_location_with_blank_lat_long(self):
        location = GroupLocation.objects.create(
            group=self.group,
            city='Test City',
            country='Test Country',
            latitude=None,
            longitude=None
        )
        self.assertIsNone(location.latitude)
        self.assertIsNone(location.longitude)


class GroupMembersTest(TestCase):

    def setUp(self):
        # Create object instances for testing
        self.group = Group.objects.create(name='Test Group') 
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_group_member(self):
        member = GroupMembers.objects.create(
            user=self.user,
            group=self.group,
            is_admin=True,
            is_moderator=False
        )
        self.assertEqual(member.user, self.user)
        self.assertEqual(member.group, self.group)
        self.assertTrue(member.is_admin)
        self.assertFalse(member.is_moderator)
        self.assertIsNotNone(member.date_joined)  

    def test_unique_constraint(self):
        GroupMembers.objects.create(
            user=self.user,
            group=self.group,
            is_admin=True,
            is_moderator=False
        )
        with self.assertRaises(Exception) as context:
            GroupMembers.objects.create(
                user=self.user,
                group=self.group,
                is_admin=False,
                is_moderator=True
            )
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))

    def test_admin_and_moderator_flags(self):
        member = GroupMembers.objects.create(
            user=self.user,
            group=self.group,
            is_admin=True,
            is_moderator=True
        )
        self.assertTrue(member.is_admin)
        self.assertTrue(member.is_moderator)

    def test_date_joined_auto_set(self):
        member = GroupMembers.objects.create(
            user=self.user,
            group=self.group
        )
        self.assertIsNotNone(member.date_joined)
        self.assertTrue(member.date_joined <= timezone.now())  


class GroupPostTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(name='Test Group') 
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_group_post(self):
        post = GroupPost.objects.create(
            group=self.group,
            user=self.user,
            content='This is a test post'
        )
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.content, 'This is a test post')
        self.assertIsNotNone(post.date_added)  

    def test_date_added_auto_set(self):
        post = GroupPost.objects.create(
            group=self.group,
            user=self.user,
            content='This is a test post'
        )
        self.assertIsNotNone(post.date_added)
        self.assertTrue(post.date_added <= timezone.now()) 
        
class GroupPostTest(TestCase):

    def setUp(self):
        # Create object instances for testing
        self.group = Group.objects.create(name='Test Group') 
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_group_post(self):
        post = GroupPost.objects.create(
            group=self.group,
            user=self.user,
            content='This is a test post'
        )
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.content, 'This is a test post')
        self.assertIsNotNone(post.date_added) 

    def test_date_added_auto_set(self):
        post = GroupPost.objects.create(
            group=self.group,
            user=self.user,
            content='This is a test post'
        )
        self.assertIsNotNone(post.date_added)
        self.assertTrue(post.date_added <= timezone.now()) 


class GroupPostCommentTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(name='Test Group')  
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.post = GroupPost.objects.create(
            group=self.group,
            user=self.user,
            content='This is a test post'
        )

    def test_create_group_post_comment(self):
        comment = GroupPostComment.objects.create(
            post=self.post,
            user=self.user,
            content='This is a test comment'
        )
        
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertIsNotNone(comment.date_added)  

    def test_date_added_auto_set(self):
        comment = GroupPostComment.objects.create(
            post=self.post,
            user=self.user,
            content='This is a test comment'
        )
        self.assertIsNotNone(comment.date_added)
        self.assertTrue(comment.date_added <= timezone.now())  
        
#-------------------EVENT TESTING-------------------------------
class EventModelTest(TestCase):
    # Create object instances for testing
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.category = Category.objects.create(name='Test Category')
        self.tag = Tag.objects.create(name='Test Tag')

    def test_event_creation(self):
        event = Event.objects.create(
            group=self.group,
            title='Test Event',
            description='Test Event Description',
            date_time=timezone.now()
        )
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.description, 'Test Event Description')
        self.assertEqual(event.group, self.group)

    def test_event_attendees(self):
        event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now()
        )
        EventAttendance.objects.create(event=event, user=self.user)
        self.assertEqual(event.attendees.count(), 1)
        self.assertEqual(event.attendees.first(), self.user)

    def test_event_image_upload(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            event_image=image
        )
        self.assertTrue(event.event_image.name.startswith('event_images/'))

    def test_event_categories(self):
        event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now()
        )
        event.categories.add(self.category)
        self.assertEqual(event.categories.count(), 1)
        self.assertEqual(event.categories.first(), self.category)

    def test_event_tags(self):
        event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now()
        )
        event.tags.add(self.tag)
        self.assertEqual(event.tags.count(), 1)
        self.assertEqual(event.tags.first(), self.tag)

    def test_default_boolean_fields(self):
        event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now()
        )
        self.assertTrue(event.nominations_open)
        self.assertFalse(event.signups_open)
        self.assertFalse(event.admin_only_nominations)
        self.assertFalse(event.skip_nominations)

    def test_custom_boolean_fields(self):
        event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            nominations_open=False,
            signups_open=True,
            admin_only_nominations=True,
            skip_nominations=True
        )
        self.assertFalse(event.nominations_open)
        self.assertTrue(event.signups_open)
        self.assertTrue(event.admin_only_nominations)
        self.assertTrue(event.skip_nominations)

    def test_event_date_time(self):
        future_time = timezone.now() + timezone.timedelta(days=7)
        event = Event.objects.create(
            group=self.group,
            title='Future Event',
            date_time=future_time
        )
        self.assertEqual(event.date_time, future_time)
        
class EventAttendanceTest(TestCase):
    # Create object instances for testing
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            nominations_open=False,
            signups_open=True,
            admin_only_nominations=True,
            skip_nominations=True
        )
    def test_create_event_attendance(self):
        attendance = EventAttendance.objects.create(
            user=self.user,
            event=self.event
        )
        self.assertEqual(attendance.user, self.user)
        self.assertEqual(attendance.event, self.event)
        self.assertIsNotNone(attendance.date_joined) 

    def test_unique_constraint(self):
        EventAttendance.objects.create(
            user=self.user,
            event=self.event
        )
        
        with self.assertRaises(Exception) as context:
            EventAttendance.objects.create(
                user=self.user,
                event=self.event
            )
        
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))
       
class EventLocationTest(TestCase):
    # Create object instances for testing
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            nominations_open=False,
            signups_open=True,
            admin_only_nominations=True,
            skip_nominations=True
        )

        # Create an EventLocation instance with some blank fields
        self.event_location = EventLocation.objects.create(
            event=self.event,
            address='789 Another St',
            city='Another City',
            postcode='67890',
            country='Another Country',
            state='',  # Blank field allowed for CharField with blank=True
            sublocality='', 
            latitude=None,  
            longitude=None  
        )
    def test_event_location_blank_fields(self):
        self.assertEqual(self.event_location.sublocality, '')  
        self.assertEqual(self.event_location.state, '')  
        self.assertIsNone(self.event_location.latitude)  
        self.assertIsNone(self.event_location.longitude) 

    def test_event_location_creation(self):
        self.assertEqual(self.event_location.event, self.event)
        self.assertEqual(self.event_location.address, '789 Another St')
        self.assertEqual(self.event_location.city, 'Another City')
        self.assertEqual(self.event_location.sublocality, '') 
        self.assertEqual(self.event_location.state, '') 
        self.assertEqual(self.event_location.postcode, '67890')
        self.assertEqual(self.event_location.country, 'Another Country')
        self.assertIsNone(self.event_location.latitude) 
        self.assertIsNone(self.event_location.longitude)  


class EventPostTest(TestCase):

    def setUp(self):
        # Create object instances for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            nominations_open=False,
            signups_open=True,
            admin_only_nominations=True,
            skip_nominations=True
        )
        self.post = EventPost.objects.create(
            event=self.event,
            user=self.user,
            content='This is a test post'
        )

    def test_event_post_creation(self):
        self.assertEqual(self.post.event, self.event)
        self.assertEqual(self.post.user, self.user)
        self.assertEqual(self.post.content, 'This is a test post')
        self.assertTrue(self.post.date_added <= timezone.now())  


class EventPostCommentTest(TestCase):

    def setUp(self):
        # Create object instances for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            nominations_open=False,
            signups_open=True,
            admin_only_nominations=True,
            skip_nominations=True
        )
        # Create test post
        self.post = EventPost.objects.create(
            event=self.event,
            user=self.user,
            content='This is a test post'
        )
        
        # Create test comment
        self.comment = EventPostComment.objects.create(
            post=self.post,
            user=self.user,
            content='This is a test comment'
        )

    def test_event_post_comment_creation(self):
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.content, 'This is a test comment')
        self.assertTrue(self.comment.date_added <= timezone.now())  

#-------------------GAME TESTING-------------------------------      
class GameModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.event = Event.objects.create(
            group=self.group,
            title='Test Event',
            description='Test Event Description',
            date_time=timezone.now()
        )

    def test_game_creation(self):
        game = Game.objects.create(
            event=self.event,
            nominator=self.user,
            name='Test Game',
            min_players=2,
            max_players=4,
            min_playtime=30,
            max_playtime=60,
            age=12,
            weight='Medium',
            description='Test Game Description'
        )
        self.assertEqual(game.name, 'Test Game')
        self.assertEqual(game.event, self.event)
        self.assertEqual(game.nominator, self.user)
        self.assertEqual(game.nomination_status, 'Pending')

    def test_unique_together_constraint(self):
        Game.objects.create(
            event=self.event,
            nominator=self.user,
            name="Unique Game"
        )
        with self.assertRaises(Exception):
            Game.objects.create(
                event=self.event,
                nominator=self.user,
                name="Unique Game"  
            )
    def test_game_nomination_status_choices(self):
        game = Game.objects.create(
            event=self.event,
            nominator=self.user,
            name='Test Game'
        )
        self.assertEqual(game.nomination_status, 'Pending')
        
        game.nomination_status = 'Approved'
        game.save()
        self.assertEqual(game.nomination_status, 'Approved')

    def test_game_optional_fields(self):
        game = Game.objects.create(
            event=self.event,
            nominator=self.user,
            name='Test Game'
        )
        self.assertIsNone(game.min_players)
        self.assertIsNone(game.max_players)
        self.assertIsNone(game.min_playtime)
        self.assertIsNone(game.max_playtime)
        self.assertIsNone(game.age)
        self.assertIsNone(game.weight)
        self.assertIsNone(game.description)

    def test_game_thumbnail_file_upload(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        game = Game.objects.create(
            event=self.event,
            nominator=self.user,
            name='Test Game',
            thumbnail_file=image
        )
        self.assertTrue(game.thumbnail_file.name.startswith('game_thumbnails/'))

    @patch('requests.get')
    def test_game_thumbnail_url_download(self, mock_get):
        # Mock the requests.get method
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.content = b"fake image content"

        game = Game(
            event=self.event,
            nominator=self.user,
            name='Test Game for URL Download',
            thumbnail_url='http://example.com/image.jpg'
        )
        game.save()  

        # Refresh the game instance from the database
        game.refresh_from_db()

        # Check if the thumbnail_file has been set
        self.assertIsNotNone(game.thumbnail_file)
        self.assertTrue(game.thumbnail_file.name.startswith('game_thumbnails/'))

        
    def test_game_date_nominated_auto_now_add(self):
        game = Game.objects.create(
            event=self.event,
            nominator=self.user,
            name='Test Game'
        )
        self.assertIsNotNone(game.date_nominated)
        self.assertLess((timezone.now() - game.date_nominated).total_seconds(), 1)


class GameSignupTest(TestCase):

    def setUp(self):
        # Create object instances for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            nominations_open=False,
            signups_open=True,
            admin_only_nominations=True,
            skip_nominations=True
        )
        # Create test game
        self.game =  Game.objects.create(
            event=self.event,
            nominator=self.user,
            name='Test Game',
            min_players=2,
            max_players=4,
            min_playtime=30,
            max_playtime=60,
            age=12,
            weight='Medium',
            description='Test Game Description'
        )
        # Create test signup
        self.signup = GameSignup.objects.create(
            nomination=self.game,
            user=self.user
        )

    def test_game_signup_creation(self):
        self.assertEqual(self.signup.nomination, self.game)
        self.assertEqual(self.signup.user, self.user)
        self.assertTrue(self.signup.date_signed_up <= timezone.now())  

    def test_unique_constraint(self):
        with self.assertRaises(Exception) as context:
            GameSignup.objects.create(
                nomination=self.game,
                user=self.user
            )
        self.assertEqual(context.exception.__class__.__name__, 'IntegrityError')

class WaitlistTest(TestCase):

    def setUp(self):
         # Create object instances for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            nominations_open=False,
            signups_open=True,
            admin_only_nominations=True,
            skip_nominations=True
        )
        # Create test game
        self.game =  Game.objects.create(
            event=self.event,
            nominator=self.user,
            name='Test Game',
            min_players=2,
            max_players=4,
            min_playtime=30,
            max_playtime=60,
            age=12,
            weight='Medium',
            description='Test Game Description'
        )
        # Create a test waitlist entry
        self.waitlist = Waitlist.objects.create(
            nomination=self.game,
            user=self.user
        )

    def test_waitlist_creation(self):
        self.assertEqual(self.waitlist.nomination, self.game)
        self.assertEqual(self.waitlist.user, self.user)
        self.assertTrue(self.waitlist.date_added <= timezone.now()) 


    def test_unique_constraint(self):
        with self.assertRaises(Exception) as context:
            Waitlist.objects.create(
                nomination=self.game,
                user=self.user
            )
        self.assertEqual(context.exception.__class__.__name__, 'IntegrityError')

class GameCommentTests(TestCase):

    def setUp(self):
        # Create object instances for testing
        self.user = User.objects.create(username='testuser')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            nominations_open=False,
            signups_open=True,
            admin_only_nominations=True,
            skip_nominations=True
        )
        # Create test game
        self.game =  Game.objects.create(
            event=self.event,
            nominator=self.user,
            name='Test Game',
            min_players=2,
            max_players=4,
            min_playtime=30,
            max_playtime=60,
            age=12,
            weight='Medium',
            description='Test Game Description'
        )
        # Create a comment
        self.comment = GameComment.objects.create(
            nominated_game=self.game,
            user=self.user,
            content='This is a test comment.'
        )

    def test_game_comment_creation(self):
        self.assertEqual(self.comment.nominated_game, self.game)
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.content, 'This is a test comment.')
        self.assertIsNotNone(self.comment.date_added) 

class VoteTests(TestCase):

    def setUp(self):
        # Create object instances for testing
        self.user = User.objects.create(username='testuser')
        self.group = Group.objects.create(name='Test Group', description='Test Group Description')
        self.event = Event.objects.create(
            group=self.group,
            title='Test Event',
            date_time=timezone.now(),
            nominations_open=False,
            signups_open=True,
            admin_only_nominations=True,
            skip_nominations=True
        )
        # Create test game
        self.game =  Game.objects.create(
            event=self.event,
            nominator=self.user,
            name='Test Game',
            min_players=2,
            max_players=4,
            min_playtime=30,
            max_playtime=60,
            age=12,
            weight='Medium',
            description='Test Game Description'
        )
        # Create a vote
        self.vote = Vote.objects.create(
            user=self.user,
            game=self.game,
            event=self.event
        )
    def test_vote_creation(self):
        self.assertEqual(self.vote.user, self.user)
        self.assertEqual(self.vote.game, self.game)
        self.assertEqual(self.vote.event, self.event)
      
#-------------------USER PROFILE TESTING-------------------------------   
class UserProfileTest(TestCase):

    def setUp(self):
         # Create object instances for testing
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create some categories and tags
        self.category1 = Category.objects.create(name='Strategy')
        self.category2 = Category.objects.create(name='Family')
        self.tag1 = Tag.objects.create(name='Cooperative')
        self.tag2 = Tag.objects.create(name='Competitive')

    def test_create_user_profile(self):
        profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            favorite_games='Game1, Game2',
            picture='',
            city='Test City',
            state='Test State',
            country='Test Country',
            latitude=40.7128,
            longitude=-74.0060
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(profile.favorite_games, 'Game1, Game2')
        self.assertEqual(profile.picture,'') 
        self.assertEqual(profile.city, 'Test City')
        self.assertEqual(profile.state, 'Test State')
        self.assertEqual(profile.country, 'Test Country')
        self.assertEqual(profile.latitude, 40.7128)
        self.assertEqual(profile.longitude, -74.0060)

    def test_user_profile_with_categories_and_tags(self):
        profile = UserProfile.objects.create(user=self.user)
        profile.categories.set([self.category1, self.category2])
        profile.tags.set([self.tag1, self.tag2])
        
        profile.refresh_from_db()
        self.assertEqual(list(profile.categories.all()), [self.category1, self.category2])
        self.assertEqual(list(profile.tags.all()), [self.tag1, self.tag2])

    def test_user_profile_blank_fields(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.bio, '')
        self.assertEqual(profile.favorite_games, '')
        self.assertTrue(profile.picture is None or profile.picture.name == '')
        self.assertEqual(profile.city, '')
        self.assertEqual(profile.state, '')
        self.assertEqual(profile.country, '')
        self.assertIsNone(profile.latitude)
        self.assertIsNone(profile.longitude)

    def test_user_profile_latitude_longitude(self):
        profile = UserProfile.objects.create(
            user=self.user,
            latitude=37.7749,
            longitude=-122.4194
        )
        self.assertEqual(profile.latitude, 37.7749)
        self.assertEqual(profile.longitude, -122.4194)


class NotificationTests(TestCase):

    def setUp(self):
        # Create object instances for testing
        self.user = User.objects.create(username='testuser')
        self.notification = Notification.objects.create(
            read=False,
            message='This is a test notification.',
            user=self.user
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.read, False)
        self.assertEqual(self.notification.message, 'This is a test notification.')
        self.assertIsNotNone(self.notification.timestamp) 
        self.assertEqual(self.notification.user, self.user)
   
    def test_notification_read_default(self):
        notification = Notification.objects.create(
            message='Another test notification.',
            user=self.user
        )
        self.assertFalse(notification.read)

    def test_notification_user_relationship(self):
        notification = Notification.objects.get(pk=self.notification.pk)
        self.assertEqual(notification.user, self.user)