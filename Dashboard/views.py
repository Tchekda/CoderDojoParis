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
from .forms import EditUserForm, AddMember, SendInvitation, InvitedFamily, EventForm, EditFamily, WorkshopForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from Homepage.models import SliderImage, Text
from .models import Mail
from Homepage.forms import *


# Create your views here.

@login_required
def index(request):
    return render(request, 'Dashboard/index.html', setReturnedValues(request))


@login_required()
def workshops(request, id):
    try:
        workshop = Workshop.objects.get(id=id)
    except Workshop.DoesNotExist:
        request.session['notifications'] = [
            {'text': "Impossible de trouver l'Atelier",
             'type': 'error'}]
        return render(request, 'Dashboard/index.html',
                      setReturnedValues(request))
    else:
        old = workshop
        if request.POST:
            form = WorkshopForm(request.POST, instance=workshop)
            if form.is_valid():
                request.session['notifications'] = [
                    {'text': "L'atelier a bien été mis à jour!",
                     'type': 'success'}]
                form.save(commit=False)
                return redirect(reverse('dashboard:workshops', kwargs={'id': workshop.id}))
            else:
                request.session['notifications'] = [
                    {'text': "Une erreur est survenue, veuillez vérifier le formulaire",
                     'type': 'error'}]
                return render(request, 'Dashboard/workshop.html',
                              setReturnedValues(request, {'workshop': old, 'form': form}))
        else:
            form = WorkshopForm(instance=workshop)
        return render(request, 'Dashboard/workshop.html',
                      setReturnedValues(request, {'workshop': workshop, 'form': form}))


@login_required()
def addWorkshop(request):
    if request.user.type == 'STA' or request.user.is_staff:
        if request.POST:
            form = WorkshopForm(request.POST)
            if form.is_valid():
                workshop = form.save()
                request.session['notifications'] = [
                    {'text': "L'Atelier a bien été créer!",
                     'type': 'success'}]
                return redirect(reverse('dashboard:workshops', kwargs={'id': workshop.id}))
            else:
                request.session['notifications'] = [
                    {'text': "Une erreur est survenue, veuillez vérifier le formulaire",
                     'type': 'error'}]
                return render(request, 'Dashboard/add-workshop.html',
                              setReturnedValues(request, {'form': form}))
        else:
            form = WorkshopForm()
        return render(request, 'Dashboard/add-workshop.html',
                      setReturnedValues(request, {'form': form}))
    else:
        request.session['notifications'] = [
            {'text': "Vous ne pouvez pas accéder à cette page",
             'type': 'error'}]
        return render(request, 'Dashboard/index.html',
                      setReturnedValues(request))


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
def editFamily(request, id):
    try:
        family = Family.objects.get(id=id)
    except Family.DoesNotExist:
        request.session['notifications'] = [
            {'text': 'Famille Introuvable ', 'type': 'error'}]
        return redirect(reverse('dashboard:index'))
    if request.user.family.id is family.id or request.user.is_staff:
        if request.POST:
            oldfamily = family
            form = EditFamily(request.POST, instance=family)
            if form.is_valid():
                cleaned = form.cleaned_data
                try:
                    for user in User.objects.filter(family=family):
                        user.email = cleaned['email']
                        user.save()
                except User.DoesNotExist:
                    pass

                form.save()
                request.session['notifications'] = [
                    {'text': "Les informations ont bien été mises à jour!",
                     'type': 'success'}]
                return redirect(reverse('dashboard:edit-family', kwargs={'id': family.id}))

        else:
            form = EditFamily(instance=family)
        return render(request, 'Dashboard/editFamily.html', setReturnedValues(request, {'form': form}))

    else:
        request.session['notifications'] = [
            {'text': "Vous ne pouvez accéder à cette page",
             'type': 'error'}]
        return redirect(reverse('dashboard:index'))


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
                                            type=type, gender=cleaned['gender'])
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
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        request.session['notifications'] = [
            {'text': "Utilisateur Introuvable",
             'type': 'error'}]
        return redirect('dashboard:index')
    if request.user.id is id:
        user.delete()
        logout(request)
        request.session['notifications'] = [
            {'text': "L'utilisateur à bel est été supprimé, veuillez vous re-connecter",
             'type': 'success'}]
        return redirect(reverse('core:login'))
    else:
        user.delete()
        request.session['notifications'] = [
            {'text': "L'utilisateur à bel est été supprimé",
             'type': 'success'}]
        return redirect(reverse('dashboard:families'))


@login_required()
def eventView(request, id):
    try:
        event = Event.objects.get(id=id)
    except (Event.DoesNotExist, Event.MultipleObjectsReturned):
        request.session['notifications'] = [
            {'text': "Impossible de trouver l'évènement",
             'type': 'error'}]
        return render(request, 'Dashboard/index.html',
                      setReturnedValues(request))

    if request.POST:
        oldstate = event.state
        oldpart = []
        for part in event.participants.all():
            oldpart.append(part)
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            cleaned = form.cleaned_data
            if oldstate != cleaned['state'] and cleaned['state'] == 'REG':
                sent = []
                for family in Family.objects.all():
                    if family.email not in sent:
                        try:
                            mail = Mail.objects.get(type='register_open')
                            subject, from_email, to = mail.subject.replace('%date%', event.time_from.strftime(
                                "%d %b %Y").title()), settings.EMAIL_HOST_USER, family.email
                            html_content = mail.content.replace("%date%", event.time_from.strftime(
                                "%d %b %Y").title()).replace("%joinurl%", request.build_absolute_uri(
                                reverse('dashboard:event', kwargs={
                                    'id': event.id})))
                        except (Mail.DoesNotExist, Mail.MultipleObjectsReturned):
                            subject, from_email, to = 'Inscriptions ouvertes pour le Coder Dojo Paris du %s' % event.time_from.strftime(
                                "%d %b %Y").title(), settings.EMAIL_HOST_USER, family.email

                            html_content = render_to_string('mail/inscriptions_open.html',
                                                            {'date': event.time_from.strftime(
                                                                "%d %b %Y").title(),
                                                             'link': request.build_absolute_uri(
                                                                 reverse('dashboard:event', kwargs={
                                                                     'id': event.id}))})  # render with dynamic value
                        text_content = strip_tags(
                            html_content)  # Strip the html tag. So people can see the pure text at least.

                        # create the email, and attach the HTML version as well.
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                for user in User.objects.all():
                    if user.email not in sent:
                        try:
                            mail = Mail.objects.get(type='register_open')
                            subject, from_email, to = mail.subject.replace('%date%', event.time_from.strftime(
                                "%d %b %Y").title()), settings.EMAIL_HOST_USER, user.email
                            html_content = mail.content.replace("%date%", event.time_from.strftime(
                                "%d %b %Y").title()).replace("%joinurl%", request.build_absolute_uri(
                                reverse('dashboard:event', kwargs={
                                    'id': event.id})))
                        except (Mail.DoesNotExist, Mail.MultipleObjectsReturned):
                            subject, from_email, to = 'Inscriptions ouvertes pour le Coder Dojo Paris du %s' % event.time_from.strftime(
                                "%d %b %Y").title(), settings.EMAIL_HOST_USER, user.email

                            html_content = render_to_string('mail/inscriptions_open.html',
                                                            {'date': event.time_from.strftime(
                                                                "%d %b %Y").title(),
                                                             'link': request.build_absolute_uri(
                                                                 reverse('dashboard:event', kwargs={
                                                                     'id': event.id}))})  # render with dynamic value
                        text_content = strip_tags(
                            html_content)  # Strip the html tag. So people can see the pure text at least.

                        # create the email, and attach the HTML version as well.
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                request.session['notifications'] = [
                    {'text': "L'évènement à bien été mis à jour et les invitations ont bien été envoyées",
                     'type': 'success'}]

            else:
                for participant in cleaned['participants']:
                    if participant not in oldpart:
                        event.participants.add(participant)
                        try:
                            mail = Mail.objects.get(type='register_confirmation')
                            subject, from_email, to = mail.subject.replace('%date%', event.time_from.strftime(
                                "%d %b %Y").title()), settings.EMAIL_HOST_USER, participant.email
                            html_content = mail.content.replace("%date%", event.time_from.strftime(
                                "%d %b %Y").title())
                        except Mail.DoesNotExist:
                            subject, from_email, to = 'Confirmation pour Coder Dojo Paris du %s' % event.time_from.strftime(
                                "%d %b %Y").title(), settings.EMAIL_HOST_USER, participant.email

                            html_content = render_to_string('mail/register_confirmation.html',
                                                            {'event': event})  # render with dynamic value
                        text_content = strip_tags(
                            html_content)  # Strip the html tag. So people can see the pure text at least.

                        # create the email, and attach the HTML version as well.
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
            request.session['notifications'] = [
                {'text': "L'évènement à bien été mis à jour",
                 'type': 'success'}]
            form.save()
            return redirect(reverse('dashboard:event', kwargs={'id': event.id}))
    else:
        form = EventForm(instance=event)
    return render(request, 'Dashboard/event.html', setReturnedValues(request, {'event': event, 'form': form}))


@login_required()
def addEvent(request):
    if request.user.is_staff is False:
        request.session['notifications'] = [
            {'text': "Vous n'avez pas la permission d'accéder à cette page",
             'type': 'error'}]
        return redirect('dashboard:index')

    if request.POST:
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            sent = []
            for participant in event.participants.all():
                subject, from_email, to = 'Confirmation pour Coder Dojo Paris du %s' % event.time_from.strftime(
                    "%d %b %Y").title(), settings.EMAIL_HOST_USER, participant.email
                sent.append(participant.email)
                try:
                    mail = Mail.objects.get(type='register_confirmation')
                    subject, from_email, to = mail.subject.replace('%date%', event.time_from.strftime(
                        "%d %b %Y").title()), settings.EMAIL_HOST_USER, request.user.email
                    html_content = mail.content.replace("%date%", event.time_from.strftime(
                        "%d %b %Y").title())
                    text_content = strip_tags(
                        html_content)
                except Mail.DoesNotExist:
                    html_content = render_to_string('mail/register_confirmation.html',
                                                    {'event': event})  # render with dynamic value
                    text_content = strip_tags(
                        html_content)
                # create the email, and attach the HTML version as well.
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            if event.state == 'REG':
                for family in Family.objects.all():
                    if family.email not in sent:
                        try:
                            mail = Mail.objects.get(type='register_open')
                            subject, from_email, to = mail.subject.replace('%date%', event.time_from.strftime(
                                "%d %b %Y").title()), settings.EMAIL_HOST_USER, family.email
                            html_content = mail.content.replace("%date%", event.time_from.strftime(
                                "%d %b %Y").title()).replace("%joinurl%", request.build_absolute_uri(
                                reverse('dashboard:event', kwargs={
                                    'id': event.id})))
                        except (Mail.DoesNotExist, Mail.MultipleObjectsReturned):
                            subject, from_email, to = 'Inscriptions ouvertes pour le Coder Dojo Paris du %s' % event.time_from.strftime(
                                "%d %b %Y").title(), settings.EMAIL_HOST_USER, family.email

                            html_content = render_to_string('mail/inscriptions_open.html',
                                                            {'date': event.time_from.strftime(
                                                                "%d %b %Y").title(),
                                                             'link': request.build_absolute_uri(
                                                                 reverse('dashboard:event', kwargs={
                                                                     'id': event.id}))})  # render with dynamic value
                        text_content = strip_tags(
                            html_content)  # Strip the html tag. So people can see the pure text at least.

                        # create the email, and attach the HTML version as well.
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                for user in User.objects.all():
                    if user.email not in sent:
                        try:
                            mail = Mail.objects.get(type='register_open')
                            subject, from_email, to = mail.subject.replace('%date%', event.time_from.strftime(
                                "%d %b %Y").title()), settings.EMAIL_HOST_USER, user.email
                            html_content = mail.content.replace("%date%", event.time_from.strftime(
                                "%d %b %Y").title()).replace("%joinurl%", request.build_absolute_uri(
                                reverse('dashboard:event', kwargs={
                                    'id': event.id})))
                        except (Mail.DoesNotExist, Mail.MultipleObjectsReturned):
                            subject, from_email, to = 'Inscriptions ouvertes pour le Coder Dojo Paris du %s' % event.time_from.strftime(
                                "%d %b %Y").title(), settings.EMAIL_HOST_USER, user.email

                            html_content = render_to_string('mail/inscriptions_open.html',
                                                            {'date': event.time_from.strftime(
                                                                "%d %b %Y").title(),
                                                             'link': request.build_absolute_uri(
                                                                 reverse('dashboard:event', kwargs={
                                                                     'id': event.id}))})  # render with dynamic value
                        text_content = strip_tags(
                            html_content)  # Strip the html tag. So people can see the pure text at least.

                        # create the email, and attach the HTML version as well.
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                request.session['notifications'] = [
                    {'text': "L'évènement à bien été créer et les invitations ont bien été envoyées",
                     'type': 'success'}]
            else:
                request.session['notifications'] = [
                    {'text': "L'évent a bien été créé!",
                     'type': 'success'}]
            return redirect(reverse('dashboard:event', kwargs={'id': event.id}))
        else:
            request.session['notifications'] = [
                {'text': "Une erreur est survenue, veuillez vérifier le formulaire",
                 'type': 'error'}]
            return render(request, 'Dashboard/add-event.html',
                          setReturnedValues(request, {'form': form}))
    else:
        form = EventForm()
    return render(request, 'Dashboard/add-event.html', setReturnedValues(request, {'form': form}))


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
                mail = Mail.objects.get(type='invitation')
                subject, from_email, to = mail.subject.replace('%family%', invitation.sender.name), \
                                          settings.EMAIL_HOST_USER, invitation.receiver
                html_content = mail.content.replace("%family%", invitation.sender.name).replace('%message%',
                                                                                                invitation.message).replace(
                    "%joinurl%", request.build_absolute_uri(
                        reverse('dashboard:invited', kwargs={'token': invitation.token})))
            except (Mail.DoesNotExist, Mail.MultipleObjectsReturned):
                subject, from_email, to = 'Invitation au Coder-Dojo Paris par %s' % request.user.get_short_name(), settings.EMAIL_HOST_USER, invitation.receiver
                html_content = render_to_string('mail/invation.html',
                                                {'invite': invitation, 'url': request.build_absolute_uri(
                                                    reverse('dashboard:invited', kwargs={'token': invitation.token}))})

            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            request.session['notifications'] = [
                {'text': "Votre inviation à bien été envoyée, attention elle peut tomber dans les spams!",
                 'type': 'success'}]
            return redirect(reverse('dashboard:invitations'))

        return render(request, 'Dashboard/invite.html', setReturnedValues(request, {'form': form}))
    else:
        form = SendInvitation()
        return render(request, 'Dashboard/invite.html', setReturnedValues(request, {'form': form}))


@login_required()
def register(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        request.session['notifications'] = [
            {'text': "Evènement introuvable",
             'type': 'error'}]
        return redirect(reverse('dashboard:futur-events'))
    if event.state != 'REG':
        request.session['notifications'] = [
            {'text': "Ce évènement n'est pas ouvert aux inscriptions %s" % event.state,
             'type': 'error'}]
        return redirect(reverse('dashboard:futur-events'))
    if event.participants:
        students = 0
        for student in event.participants.all():
            if student.id is request.user.id:
                request.session['notifications'] = [
                    {'text': "Vous êtes déjà inscrit",
                     'type': 'success'}]
                return redirect(reverse('dashboard:event', kwargs={'id': id}))
            if student.type is 'STU':
                students += 1

        if students >= event.max_students:
            request.session['notifications'] = [
                {'text': "Il n'y a plus de places à cet évènement, contactez nous pour plus d'info!",
                 'type': 'error'}]
            return redirect(reverse('dashboard:event', kwargs={'id': id}))

    event.participants.add(request.user)

    try:
        mail = Mail.objects.get(type='register_confirmation')
        subject, from_email, to = mail.subject.replace('%date%', event.time_from.strftime(
            "%d %b %Y").title()), settings.EMAIL_HOST_USER, request.user.email
        html_content = mail.content.replace("%date%", event.time_from.strftime(
            "%d %b %Y").title())
    except Mail.DoesNotExist:
        subject, from_email, to = 'Confirmation pour Coder Dojo Paris du %s' % event.time_from.strftime(
            "%d %b %Y").title(), settings.EMAIL_HOST_USER, request.user.email

        html_content = render_to_string('mail/register_confirmation.html',
                                        {'event': event})  # render with dynamic value

    text_content = strip_tags(html_content)  # Strip the html tag. So people can see the pure text at least.
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    request.session['notifications'] = [
        {
            'text': "Vous avez été inscrit et un mail de confirmation vous a été adressée, attention elle peut tomber dans les spams!",
            'type': 'success'}]
    return redirect(reverse('dashboard:event', kwargs={'id': id}))


@login_required()
def invited(request, token):
    try:
        invitation = Invitation.objects.get(token=token)
    except Invitation.DoesNotExist:
        request.session['notifications'] = [
            {
                'text': "Cette invitation n'est pas valable, demandez à votre ami de vous en renvoyer une!",
                'type': 'error'}]
        return redirect(reverse('core:login'))
    if request.POST:
        form = InvitedFamily(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            user = User.objects.create_user(name=cleaned['username'], familyname=cleaned['family'],
                                            email=cleaned['email'], type=cleaned['type'], gender=cleaned['gender'])
            user.save()
            login(request, user)
            subject, from_email, to = "Confirmation au Coder Dojo Paris", settings.EMAIL_HOST_USER, invitation.receiver

            html_content = render_to_string('mail/creation_confirmation.html',
                                            {'loginUrl': request.build_absolute_uri(
                                                reverse('core:login')),
                                                'email': user.email, 'name': user.family.name})
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            request.session['notifications'] = [
                {'text': "Votre compte a bien été créer, vous êtes désormais connecté",
                 'type': 'success'}]
            invitation.state = 'D'
            invitation.save()

            return redirect(reverse('dashboard:index'))

    else:
        form = InvitedFamily(initial={'email': invitation.receiver})
    return render(request, 'Dashboard/invited.html', setReturnedValues(request, {'form': form,
                                                                                 'uuid': token}))


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


@login_required()
def adminEdition(request, type=None, id=None):
    if request.user.is_staff is False:
        request.session['notifications'] = [
            {'text': "Vous n'avez pas la permission d'accéder à cette page",
             'type': 'error'}]
        return redirect('dashboard:index')
    if type is not None and id is not None:
        if type.lower() == 'mail':
            try:
                mail = Mail.objects.get(id=id)
            except Mail.DoesNotExist:
                request.session['notifications'] = [
                    {'text': "Mail Introuvable",
                     'type': 'error'}]
                return redirect(reverse('dashboard:index'))
            if request.POST:
                form = EmailForm(request.POST, instance=mail)
                if form.is_valid():
                    mail = form.save()
                    request.session['notifications'] = [
                        {'text': "Le Mail a bien été mis à jour",
                         'type': 'success'}]
                    return redirect(reverse('dashboard:edition-item', kwargs={'id': mail.id, 'type': 'mail'}))
                else:
                    request.session['notifications'] = [
                        {'text': "Le formulaire est invalide",
                         'type': 'error'}]
            else:
                form = EmailForm(instance=mail)
            return render(request, 'Dashboard/parameter.html',
                          setReturnedValues(request, {'form': form, 'type': type.lower(), 'id': mail.id}))
        elif type.lower() == 'text':
            try:
                text = Text.objects.get(id=id)
            except Mail.DoesNotExist:
                request.session['notifications'] = [
                    {'text': "Texte Introuvable",
                     'type': 'error'}]
                return redirect('dashboard:index')
            if request.POST:
                form = TextForm(request.POST, instance=text)
                if form.is_valid():
                    text = form.save()
                    request.session['notifications'] = [
                        {'text': "Le Texte a bien été mis à jour",
                         'type': 'success'}]
                    return redirect(reverse('dashboard:edition-item', kwargs={'id': text.id, 'type': 'text'}))
                else:
                    request.session['notifications'] = [
                        {'text': "Le formulaire est invalide",
                         'type': 'error'}]
            else:
                form = TextForm(instance=text)
            return render(request, 'Dashboard/parameter.html',
                          setReturnedValues(request, {'form': form, 'type': type.lower(), 'id': text.id}))
        elif type.lower() == 'image':
            try:
                image = SliderImage.objects.get(id=id)
            except Mail.DoesNotExist:
                request.session['notifications'] = [
                    {'text': "Image Introuvable",
                     'type': 'error'}]
                return redirect('dashboard:index')
            if request.POST:
                form = ImageForm(request.POST, instance=image)
                if form.is_valid():
                    image = form.save()
                    request.session['notifications'] = [
                        {'text': "Le Texte a bien été mis à jour",
                         'type': 'success'}]
                    return redirect(reverse('dashboard:edition-item', kwargs={'id': image.id, 'type': 'image'}))
                else:
                    request.session['notifications'] = [
                        {'text': "Le formulaire est invalide",
                         'type': 'error'}]
            else:
                form = ImageForm(instance=image)
            return render(request, 'Dashboard/parameter.html',
                          setReturnedValues(request, {'form': form, 'type': type.lower(), 'id': image.id}))
        else:
            request.session['notifications'] = [
                {'text': "Paramètre Introuvable",
                 'type': 'error'}]
            return redirect('dashboard:index')

    else:
        data = {}
        try:
            mails = Mail.objects.all()
            data['mails'] = mails
        except Mail.DoesNotExist:
            pass
        try:
            texts = Text.objects.all()
            data['texts'] = texts
        except Text.DoesNotExist:
            pass

        try:
            images = SliderImage.objects.all()
            data['images'] = images
        except SliderImage.DoesNotExist:
            pass

        return render(request, 'Dashboard/parameters.html', setReturnedValues(request, data))


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
