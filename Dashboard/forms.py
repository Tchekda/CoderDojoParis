from django import forms
from Core.models import User, Invitation, Family


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
