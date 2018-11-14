import datetime

from django.shortcuts import render
from django.utils import timezone

from Core.models import Event, User

"""
Controller of the Hompage module
The absolute folder of the templates rendered here : ./templates/Homepage/fileName.html
"""


def index(request):  # Landing page
    return render(request, 'Homepage/homepage.html')


def events(request):  # List of events
    return render(request, 'Homepage/events.html', {'events': Event.objects.filter(time_from__gte=datetime.datetime.now(tz=timezone.utc))})


def staff(request):  # List of Staff
    return render(request, 'Homepage/staff.html', {'staff': User.objects.filter(type='STA')})


def about(request):  # More about the association
    return render(request, 'Homepage/about.html')
