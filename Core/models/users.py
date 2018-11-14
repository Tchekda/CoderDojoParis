from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import EmailValidator, ValidationError
from django.db import models

from Core.models import Workshop


class Family(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)

    def __str__(self):
        count = 0
        try:
            persons = User.objects.filter(family=self)
            count = persons.count()
        except User.DoesNotExist:
            pass
        return "Famille %s (%s personnes)" % (self.name, count)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Familles"

    def get_number(self):
        count = 0
        try:
            persons = User.objects.filter(family=self)
            count = persons.count()
        except User.DoesNotExist:
            pass
        return count


class Invitation(models.Model):
    token = models.UUIDField(unique=True, editable=False)
    date = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(Family, on_delete=models.CASCADE)
    receiver = models.EmailField(max_length=100, unique=True)
    message = models.TextField(max_length=1500)
    STATES = (
        ('S', 'Sent'),
        ('D', 'Done'),
    )
    state = models.CharField(
        choices=STATES,
        max_length=1,
        default='S'
    )

    def __str__(self):
        return "Pour %s par %s" % (self.receiver, self.sender.name)

    class Meta:
        ordering = ('receiver',)
        verbose_name_plural = "Invitations"


class UserManager(BaseUserManager):
    def create_user(self, name, familyname, type='STU', email=None, password=None, super=False, staff=False):
        if familyname is not Family:
            try:
                family = Family.objects.get(name=familyname)
            except Family.DoesNotExist:
                if email is None:
                    raise ValueError('Vous devez fournir une adresse mail afin de créér le compte famille')
                family = Family(name=familyname, email=self.normalize_email(email))
                family.save()

        else:
            family = familyname

        user = self.model(username=name.title(), family=family, type=type, )
        user.is_staff = staff
        user.is_superuser = super
        if email is None:
            user.email = family.email
        else:
            user.email = email

        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)

        try:
            EmailValidator()(user.email)
        except ValidationError:
            raise ValueError('Adresse Email invalide, veuillez en saisir une valide!')
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email, **other_fields):
        self.create_user(name=username, familyname='Temp', email=email, type='STA', password=password, super=True, staff=True)


class User(AbstractUser):  # Participant

    last_name = None
    first_name = None
    username = models.CharField(max_length=150)
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    registered_workshop = models.ForeignKey(Workshop, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    email = models.EmailField(null=True, blank=True, default=None)

    PARTICIPANT_TYPES = (
        ('STU', 'Participant'),
        ('ADU', 'Adulte'),
        ('STA', 'Mentor'),
    )

    type = models.CharField(
        max_length=3,
        choices=PARTICIPANT_TYPES,
        default='STU'
    )

    GENDER = (
        ('M', 'Homme'),
        ('F', 'Femme')
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER,
        default=None,
        null=True
    )

    objects = UserManager()

    def __str__(self):
        return "%s %s (%s)" % (self.username, self.family.name, self.get_type_display())

    def get_short_name(self):
        return "%s %s" % (self.username, self.family.name[:1])

    def get_full_name(self):
        return "%s %s" % (self.username, self.family.name)

    class Meta:
        ordering = ('username',)
        verbose_name_plural = "Participants"
