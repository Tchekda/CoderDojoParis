import datetime
import uuid
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import login, logout
from Core.models import Workshop, User, Event, Family, Invitation
from .forms import EditUserForm, AddMember, SendInvitation
from django.core.mail import send_mail
from smtplib import SMTPException


# Create your views here.

@login_required
def index(request):
    return render(request, 'Dashboard/index.html', setReturnedValues(request))


@login_required()
def workshops(request, id):
    try:
        workshop = Workshop.objects.get(id=id)
    except (Workshop.DoesNotExist, Workshop.MultipleObjectsReturned):
        raise Http404('Impossible de trouver l\'Atelier')
    else:
        return render(request, 'Dashboard/workshop.html', setReturnedValues(request, {'workshop': workshop}))


@login_required()
def userShow(request, id):
    if request.user.id is id:
        form = EditUserForm(instance=request.user, initial={'family': str(request.user.family)})
        return render(request, 'Dashboard/user.html', setReturnedValues(request, {'form': form}))
    else:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            request.session['notifications'] = [
                {'text': 'Utilisateur Introuvable',
                 'type': 'error'}]
            return redirect('dashboard:index')

        if user.family.id is request.user.family.id or request.user.is_staff:
            login(request, user)
            request.session['notifications'] = [
                {'text': 'Vous êtes désormais connecter avec le compte de %s' % user.get_short_name(),
                 'type': 'success'}]
            return redirect('dashboard:index')
        else:
            request.session['notifications'] = [
                {'text': 'Vous ne pouvez pas accéder à cette page ', 'type': 'error'}]
            return redirect('dashboard:index')


@login_required()
def editUser(request, id):
    if request.user.id is not id and request.user.is_staff is False:
        request.session['notifications'] = [
            {'text': 'Vous ne pouvez pas accéder à cette page ', 'type': 'error'}]
        return redirect('dashboard:index')
    else:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            request.session['notifications'] = [
                {'text': 'Utilisateur Introuvable ', 'type': 'error'}]
            return redirect('dashboard:index')
        if request.POST:
            form = EditUserForm(request.POST, instance=user)
            if form.save():
                request.session['notifications'] = [
                    {'text': 'Le profil à été modifié avec succès', 'type': 'success'}]
                return redirect(reverse('dashboard:family', kwargs={'id': user.family.id}))
            else:
                request.session['notifications'] = [
                    {'text': 'Formulaire invalide ', 'type': 'error'}]
                return render(request, 'Dashboard/user.html',
                              setReturnedValues(request, {'form': form, 'editUser': user}))

        form = EditUserForm(instance=user, initial={'family': str(user.family)})
        return render(request, 'Dashboard/user.html', setReturnedValues(request, {'form': form, 'editUser': user}))


@login_required()
def families(request, id=None):
    if request.user.is_staff is False:
        request.session['notifications'] = [
            {'text': "Vous ne pouvez accéder à cette page",
             'type': 'error'}]
        return redirect(reverse('dashboard:index'))
    if id:
        try:
            family = Family.objects.get(id=id)
            users = User.objects.filter(family=family)
        except (Family.DoesNotExist, User.DoesNotExist):
            request.session['notifications'] = [
                {'text': "Impossible de trouver cette famille",
                 'type': 'error'}]
            return redirect(reverse('dashboard:families'))
        return render(request, 'Dashboard/family.html',
                      setReturnedValues(request, {'selected_family': family, 'users': users}))
    else:
        return render(request, 'Dashboard/families.html',
                      setReturnedValues(request, {'families': Family.objects.all()}))


@login_required()
def addMember(request):
    if request.POST:
        form = AddMember(request.POST, initial={'family': str(request.user.family), 'email': request.user.family.email,
                                                'family_id': request.user.family.id})

        if form.is_valid():
            cleaned = form.cleaned_data
            username = cleaned['username']
            email = cleaned['email']
            type = cleaned['type']
            try:
                email_families = Family.objects.filter(email=email)
            except Family.DoesNotExist:
                pass
            else:
                for family in email_families:
                    if family.id is not request.user.family.id:
                        request.session['notifications'] = [
                            {'text': 'Cette adresse mail est déjà utilisée par une autre famille',
                             'type': 'error'}]
                        return render(request, 'Dashboard/addmember.html', setReturnedValues(request, {'form': form}))
            user = User.objects.create_user(name=username.title(), email=email, familyname=request.user.family.name,
                                            type=type)
            login(request, user)
            request.session['notifications'] = [
                {'text': 'Vous avez créer et êtes désormais connecté avec le compte de %s' % user.get_short_name(),
                 'type': 'success'}]
            return redirect('dashboard:index')
        else:
            request.session['notifications'] = [
                {'text': 'Formulaire invalide',
                 'type': 'error'}]
    else:
        form = AddMember(initial={'family': str(request.user.family), 'email': request.user.family.email,
                                  'family_id': request.user.family.id})

    return render(request, 'Dashboard/addmember.html', setReturnedValues(request, {'form': form}))


@login_required()
def userDelete(request, id):
    if request.user.id is not id and request.user.is_staff is False:
        request.session['notifications'] = [
            {'text': "Vous n'avez pas la permission de supprimer cet utilisateur",
             'type': 'error'}]
        return redirect('dashboard:index')
    request.user.delete()
    logout(request)
    request.session['notifications'] = [
        {'text': "L'utilisateur à bel est été supprimé, veuillez vous re-connecter",
         'type': 'success'}]
    return redirect(reverse('core:login'))


@login_required()
def eventView(request, id):
    try:
        event = Event.objects.get(id=id)
    except (Event.DoesNotExist, Event.MultipleObjectsReturned):
        raise Http404('Evènement introuvable')
    else:
        return render(request, 'Dashboard/event.html', setReturnedValues(request, {'event': event}))


@login_required()
def pastEvents(request):
    return render(request, 'Dashboard/events.html', setReturnedValues(request, {'past': True,
                                                                                'events': Event.objects.filter(
                                                                                    time_from__lte=datetime.datetime.now(
                                                                                        tz=timezone.utc))}))


@login_required()
def futurEvents(request):
    return render(request, 'Dashboard/events.html', setReturnedValues(request, {'past': False,
                                                                                'events': Event.objects.filter(
                                                                                    time_from__gte=datetime.datetime.now(
                                                                                        tz=timezone.utc))}))


@login_required()
def sendInvitation(request):
    if request.POST:
        form = SendInvitation(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            invitation = Invitation(token=uuid.uuid4(), sender=request.user.family, receiver=cleaned['receiver'],
                                    message=cleaned['message'])
            invitation.save()
            try:
                send_mail(subject='Invitation au Coder-Dojo Paris par %s' % request.user.get_short_name(),
                          from_email=settings.EMAIL_HOST_USER,
                          html_message=invitation.message,
                          recipient_list=[invitation.receiver],
                          message="Ce mail est en HTML, veuillez vous mettre à jour..."
                          )
            except SMTPException:
                request.session['notifications'] = [
                    {'text': "Votre inviation n'à pas pue être envoyée, réessayer plus tard",
                     'type': 'error'}]
            else:
                request.session['notifications'] = [
                    {'text': "Votre inviation à bien été envoyée",
                     'type': 'success'}]
                return redirect(reverse('dashboard:index'))

        return render(request, 'Dashboard/invite.html', setReturnedValues(request, {'form': form}))
    else:
        form = SendInvitation()
        return render(request, 'Dashboard/invite.html', setReturnedValues(request, {'form': form}))


@login_required()
def invitations(request):
    invites = None
    receive = None
    try:
        invites = Invitation.objects.filter(sender=request.user.family)
        receive = Invitation.objects.get(receiver=request.user.family.email)
    except Invitation.DoesNotExist:
        pass
    return render(request, 'Dashboard/invitations.html',
                  setReturnedValues(request, {'invites': invites, 'receive': receive}))


def setReturnedValues(request, args=None):
    user = request.user
    if 'notifications' in request.session:
        notif = request.session['notifications']
        request.session['notifications'] = []
    else:
        notif = []

    default_data = {
        'workshops': Workshop.objects.all(),
        'family': User.objects.filter(family=user.family),
        'notifications': notif
    }
    if user.type == 'STA':
        default_data['families'] = Family.objects.all()

    data = default_data.copy()
    if args:
        data.update(args)
    return data
