from django.contrib.auth import login, logout
from django.http import HttpResponseServerError, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import FamilyLoginForm, AdminLoginForm
from .models import Family, User


def loginview(request):
    if request.user.is_authenticated:
        return redirect(reverse('dashboard:index'))
    if request.method == 'POST':
        form = FamilyLoginForm(request.POST)
        if form.is_valid():
            try:
                family = Family.objects.get(email=form.cleaned_data['email'], name=form.cleaned_data['name'])
            except (Family.DoesNotExist, Family.MultipleObjectsReturned):
                return HttpResponseServerError("Impossible de trouver le compte : Multiples Résultats / Introuvable")
            users = User.objects.filter(family=family)
            for family_user in users:
                if family_user.has_usable_password():
                    request.session['notifications'] = [
                        {'text': 'Vous êtes Admin, connectez vous avec votre mot de passe', 'type': 'error'}]
                    return redirect(reverse('core:admin-login'))

            for family_user in users:
                if family_user.type == 'STA':
                    login(request, family_user)
                    return redirect(reverse('dashboard:index'))

            for family_user in users:
                if family_user.type == 'ADU':
                    login(request, family_user)
                    request.session['notifications'] = [
                        {'text': 'Vous êtes Connécté', 'type': 'success'}]
                    return redirect(reverse('dashboard:index'))

            family_user = users.first()
            login(request, family_user)
            return redirect(reverse('dashboard:index'))
        else:
            return render(request, 'Core/login.html', {"login_form": form, "admin": False})
    else:
        form = FamilyLoginForm()
        if 'notifications' in request.session:
            notif = request.session['notifications']
            request.session['notifications'] = []
        else:
            notif = []
        return render(request, 'Core/login.html',
                      {"login_form": form, "admin": False, 'notifications': notif})


def adminlogin(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            users = User.objects.filter(email=email)
            for user in users:
                if user.has_usable_password():
                    if user.check_password(password):
                        login(request, user)
                        return redirect('dashboard:index')
            return redirect(reverse('core:admin-login'))
        else:
            return render(request, 'Core/login.html', {"login_form": form, "admin": True})
    else:
        form = AdminLoginForm()
        if 'notifications' in request.session:
            notif = request.session['notifications']
            request.session['notifications'] = []
        else:
            notif = []
        return render(request, 'Core/login.html',
                      {"login_form": form, "admin": True, 'notifications': notif})


def logout_request(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('homepage:index')


def BadRequestError(request, exception=None):
    message = 'Mauvaise Requête'
    if exception:
        message = exception

    return render(request, 'Core/error.html', {
        'code': 400,
        'message': message
    }, status=400)


def PermissionDeniedError(request, exception=None):
    message = 'Accès Refusé'
    if exception:
        message = exception

    return render(request, 'Core/error.html', {
        'code': 403,
        'message': message
    }, status=403)


def NotFoundError(request, exception=None):
    message = 'Page introuvable'
    if exception:
        message = exception

    return render(request, 'Core/error.html', {
        'code': 404,
        'message': message
    }, status=404)


def ServerError(request, exception=None):
    message = 'Erreur interne du Serveur'
    if exception:
        message = exception

    return render(request, 'Core/error.html', {
        'code': 500,
        'message': message
    }, status=500)
