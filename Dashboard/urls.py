from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),  # Landing page
    path('events/<int:id>/', views.eventView, name='event'),
    path('events/past/', views.pastEvents, name='past-events'),
    path('events/futur/', views.futurEvents, name='futur-events'),
    path('workshop/<int:id>/', views.workshops, name='workshops'),
    path('user/<int:id>/', views.userShow, name='user'),
    path('user/edit/<int:id>/', views.editUser, name='user-edit'),
    path('user/delete/<int:id>', views.userDelete, name='user-delete'),
    path('family/', views.families, name='families'),
    path('family/add/', views.addMember, name='add-member'),
    path('family/<int:id>/', views.families, name='family'),
    path('invite/add/', views.sendInvitation, name='new-invite'),
    path('invite/', views.invitations, name='invitations'),
]
