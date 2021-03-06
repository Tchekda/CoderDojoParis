import datetime

from django.shortcuts import render
from django.utils import timezone

from Core.models import Event, User
from .models import Text, SliderImage

"""
Controller of the Hompage module
The absolute folder of the templates rendered here : ./templates/Homepage/fileName.html
"""


def index(request):  # Landing page
    images = None
    try:
        images = SliderImage.objects.all()
    except SliderImage.DoesNotExist:
        pass
    return render(request, 'Homepage/homepage.html', setReturnedValues(request, {'images': images,
                                                                                 'ints': range(
                                                                                     images.count())}))


def events(request):  # List of events
    return render(request, 'Homepage/events.html',
                  setReturnedValues(request, {
                      'events': Event.objects.filter(time_from__gte=datetime.datetime.now(tz=timezone.utc))}))


def staff(request):  # List of Staff
    return render(request, 'Homepage/staff.html',
                  setReturnedValues(request, {'staff': User.objects.filter(type='STA')}))


def about(request):  # More about the association
    data = {}
    try:
        data['where'] = Text.objects.get(type='where')
    except Text.DoesNotExist:
        pass
    try:
        data['joinus'] = Text.objects.get(type='joinus')
    except Text.DoesNotExist:
        pass
    try:
        data['whatis'] = Text.objects.get(type='whatis')
    except Text.DoesNotExist:
        pass
    return render(request, 'Homepage/about.html', setReturnedValues(request, data))


def setReturnedValues(request, args=None):
    user = request.user
    if 'notifications' in request.session:
        notif = request.session['notifications']
        request.session['notifications'] = []
    else:
        notif = []

    default_data = {}
    try:
        default_data['footer'] = Text.objects.get(type='footer')
    except Text.DoesNotExist:
        pass

    data = default_data.copy()
    if args:
        data.update(args)
    return data
