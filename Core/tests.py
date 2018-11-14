from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from .models import User, Workshop


class CoreTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user(name='David', familyname='Tchekachev', email='contact@tchekda.fr', type='STA')
        User.objects.create_user(name='Mikael', familyname='Tchekachev', email='contact@tchekda.fr')
        Workshop.objects.create(name='Atelier1', manager=user, max_participant=20,
                                description='Lorem Ipsum').full_clean()

    def testFamilyCount(self):
        self.assertEqual(2, User.objects.filter(family__name='Tchekachev').count())

    def testUniqueFamilyEmail(self):
        with self.assertRaises(IntegrityError) as ctx:
            User.objects.create_user(name='Antoine', familyname='Doe', email='contact@tchekda.fr')
        self.assertEqual("UNIQUE constraint failed: Core_family.email", str(ctx.exception))

    def testWorkshopManager(self):
        with self.assertRaises(ValidationError) as ctx:
            workshop = Workshop.objects.get(name='Atelier1')
            workshop.manager = User.objects.get(username='Mikael', family__name='Tchekachev')
            workshop.full_clean()
            workshop.save()
        self.assertEqual("{'__all__': ['Le manager doit être Staff']}", str(ctx.exception))
