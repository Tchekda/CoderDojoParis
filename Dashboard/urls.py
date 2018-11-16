from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),  # Landing page
    path('events/<int:id>/', views.eventView, name='event'),
    path('events/add/', views.addEvent, name='add-event'),
    path('events/past/', views.pastEvents, name='past-events'),
    path('events/futur/', views.futurEvents, name='futur-events'),
    path('workshop/<int:id>/', views.workshops, name='workshops'),
    path('workshop/add/', views.addWorkshop, name='add-workshop'),
    path('user/<int:id>/', views.userShow, name='user'),
    path('user/edit/<int:id>/', views.editUser, name='user-edit'),
    path('user/delete/<int:id>', views.userDelete, name='user-delete'),
    path('family/', views.families, name='families'),
    path('family/add/', views.addMember, name='add-member'),
    path('family/edit/<int:id>/', views.editFamily, name='edit-family'),
    path('family/<int:id>/', views.families, name='family'),
    path('invite/add/', views.sendInvitation, name='new-invite'),
    path('invite/', views.invitations, name='invitations'),
    path('register/<int:id>/', views.register, name='register'),
    path('invited/<token>/', views.invited, name='invited'),
    path('edition/', views.adminEdition, name='edition-list'),
    path('edition/<type>/<int:id>/', views.adminEdition, name='edition-item'),
]
