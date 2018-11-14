from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('login/', views.loginview, name='login'),
    path('adminlogin/', views.adminlogin, name='admin-login'),
    path('logout/', views.logout_request, name='logout'),
]
