from django.test import TestCase
from django.contrib.auth.models import User


class AccountTest(TestCase):
    fixtures = ['auth', 'catalog']

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_userprofile_is_auto_created(self):
        self.user.save()
        self.assertEqual(self.user.profile.user, self.user)
