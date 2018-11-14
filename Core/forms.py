from django import forms

from .models import Family, User


class FamilyLoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse Email'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de Famille'}))
    fields = ['email', 'name']

    def clean(self):
        cleaned = self.cleaned_data
        email = cleaned['email']
        name = cleaned['name']
        try:
            Family.objects.get(email=email, name=name)
        except Family.MultipleObjectsReturned:
            raise forms.ValidationError("Impossible de trouver la famille : Multiples Résultats")
        except Family.DoesNotExist:
            raise forms.ValidationError('Aucune famille avec ce couple de nom et adresse mail : Introuvable')
        return self.cleaned_data

    def clean_name(self):
        return self.cleaned_data['name'].title()

    def clean_email(self):
        return self.cleaned_data['email'].lower()


class AdminLoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de Passe'}))
    fields = ['email', 'password']

    def clean(self):
        cleaned = self.cleaned_data
        email = cleaned['email']
        password = cleaned['password']
        try:
            users = User.objects.filter(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("Aucun membre avec cette adresse mail")

        for user in users:
            if user.has_usable_password():
                if user.check_password(password):
                    return self.cleaned_data
        raise forms.ValidationError("Aucun compte avec ce couple adresse mail / mot de passe")

    def clean_email(self):
        return self.cleaned_data['email'].lower()
