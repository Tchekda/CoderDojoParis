from django import forms
from Core.models import User, Invitation, Family, Event, Workshop


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'type', 'gender']
        labels = {
            'username': 'Prénom',
            'type': 'Type',
            'gender': 'Sexe',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Type'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Sexe'}),
        }


class AddMember(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'type', 'gender']
        labels = {
            'username': 'Prenom',
            'email': 'Adresse E-Mail',
            'type': 'Type',
            'gender': 'Sexe',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse E-Mail'}),
            'type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Type'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Sexe'}),
        }


class SendInvitation(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['receiver', 'message']
        labels = {
            'receiver': 'Adresse Mail du destinataire',
            'message': 'Message Personalisé',
        }
        widgets = {
            'receiver': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse E-Mail'}),
            'message': forms.Textarea(attrs={'class': 'textarea form-control', 'placeholder': 'Message Personalisé '
                                                                                              'pour accompagner votre'
                                                                                              ' invitation'}),
        }

    def clean(self):
        cleaned = self.cleaned_data
        email = cleaned['receiver']
        message = cleaned['message']

        try:
            family = Family.objects.get(email=email)
            user = User.objects.filter(email=email)
        except(Family.DoesNotExist, User.DoesNotExist):
            pass
        else:
            raise forms.ValidationError('Une famille ou un utilisateur est déjà inscrit avec cette adresse')

        try:
            invitation = Invitation.objects.get(receiver=email)
        except Invitation.DoesNotExist:
            pass
        else:
            raise forms.ValidationError('une invitation à déjà été envoyée à cette adresse')

        return self.cleaned_data


class InvitedFamily(forms.ModelForm):
    family = forms.CharField(label='Nom de Famille',
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control', 'placeholder': 'Nom de votre Famille'}))

    class Meta:
        model = User
        fields = ['email', 'username', 'type', 'gender']
        labels = {
            'email': 'Adresse Mail de contact',
            'username': 'Prénom',
            'type': 'Type',
            'gender': 'Sexe'
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse E-Mail'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre Prénom'}),
            'type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Type'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Sexe'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['time_from', 'time_end', 'public_adress', 'adress', 'max_students', 'participants', 'state',
                  'twitter']
        labels = {
            'time_from': "Heure de début",
            'time_end': "Heure de fin",
            'public_adress': 'Adresse Publique',
            'adress': 'Adresse Privée',
            'max_students': 'Nombre Maximal de Participants',
            'participants': 'Préinscription',
            'state': 'Etat',
            'twitter': 'Lien de la publication Twitter (Vide si pas encore posté!)',
        }
        widgets = {
            'time_from': forms.TextInput(
                attrs={'class': 'form-control datepicker', 'placeholder': 'Heure de Début'}),
            'time_end': forms.TextInput(
                attrs={'class': 'form-control datepicker', 'placeholder': 'Heure de Fin'}),
            'public_adress': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse Publique'}),
            'adress': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse Privée'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de participants'}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-control', 'placeholder': 'Préinscrits'}),
            'state': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Etat'}),
            'twitter': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Lien de la publication Twitter'}),
        }


class EditFamily(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['email', 'name']
        labels = {
            'email': 'Adresse E-Mail',
            'name': 'Nom de Famille',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse E-Mail'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de Famille'}),
        }


class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = ['name', 'manager', 'description', 'level']
        labels = {
            'manager': "Responsable de l'Atelier",
            'name': "Nom de l'Atelier",
            'description': "Description de l'Atelier",
            'level': "Niveau de difficulté"
        }
        widgets = {
            'manager': forms.Select(attrs={'class': 'form-control', 'placeholder': "Responsable de l'Atelier"}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom de l'Atelier"}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Description de l'Atelier"}),
            'level': forms.Select(attrs={'class': 'form-control', 'placeholder': "Niveau de difficulté"}),
        }
