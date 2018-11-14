from django.urls import path

from . import views

app_name = 'homepage'
urlpatterns = [
    path('', views.index, name='index'),  # Landing page
    path('events/', views.events, name='events'),  # List of the events
    path('staff/', views.staff, name='staff'),  # List of the staff
    path('about/', views.about, name='about'),  # More about the association
]
