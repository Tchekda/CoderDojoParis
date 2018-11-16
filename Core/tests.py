from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from .models import User, Workshop


class CoreTestCase(TestCase):

    def setUp(self):
        pass