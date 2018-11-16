from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
import requests


class Event(models.Model):
    time_from = models.DateTimeField(unique=True)
    time_end = models.DateTimeField(unique=True)
    public_adress = models.CharField(max_length=120)
    adress = models.CharField(max_length=120)
    max_students = models.IntegerField(default=30)
    coordinates = models.CharField(max_length=100, blank=True)  # xxxxxxxxx:yyyyyyyyy for OpenStreetMap
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    twitter = models.URLField(blank=True)

    STATES = (
        ('PLA', 'Planned'),
        ('REG', 'Registration'),
        ('PRO', 'In Progress'),
        ('FIN', 'Finished')
    )

    state = models.CharField(
        choices=STATES,
        max_length=3,
        default='PLA'
    )

    def save(self, *args, **kwargs):
        api_response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(self.adress,
                                                                                           settings.GOOGLE_API))
        api_response_dict = api_response.json()
        if api_response_dict['status'] == 'OK':
            latitude = api_response_dict['results'][0]['geometry']['location']['lat']
            longitude = api_response_dict['results'][0]['geometry']['location']['lng']
            self.coordinates = "%s : %s" % (longitude, latitude)
        else:
            raise ValidationError("API error : %s" % api_response_dict)

        if self.time_from >= self.time_end:
            raise ValidationError("La fin est avant le début??")
        super().save(*args, **kwargs)

    def get_coord(self):
        return self.coordinates.split(' : ')

    def __str__(self):
        return "Event du %s / %s " % (self.time_from.day, self.time_from.month)


class Workshop(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    LEVEL = (
        (1, 'Starter'),
        (2, 'Medium'),
        (3, 'Hard'),
    )

    level = models.IntegerField(
        choices=LEVEL,
        default=1
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.manager.type != 'STA':
            raise ValidationError("Le manager doit être Staff")

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Ateliers"
