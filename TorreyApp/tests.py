from django.test import TestCase
from django.contrib.auth.models import User
from TorreyApp.models import Golfer
from TorreyApp.models import Course


# Create your tests here.
class GolferTestCase(TestCase):
    def test_set_up(self):
        user = User.objects.create(username="testuser1", password="password123")
        # Verify creating a Golfer with a 1-to-1 with User
        print("Verify creating a Golfer")
        golfer = Golfer.objects.create(user=user, num_players="1,2,3,4", 
            send_notifications=True, days_of_week="6,7"
        )
        self.assertEqual(Golfer.objects.all().get(user=user), golfer)
        # Verify adding a Golfer to a Course
        print("Verify adding a Golfer to a Course")
        course = Course.objects.create(name="NotTorrey", course_index=12345)
        course.golfers.add(golfer)
        self.assertIn(course, golfer.golfer_courses.all())
