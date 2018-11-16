from django import forms
from .models import Text, SliderImage
from Dashboard.models import Mail


class EmailForm(forms.ModelForm):
    class Meta:
        model = Mail
        fields = ['subject', 'content']
        labels = {
            'subject': 'Sujet',
            'content': 'Contenu',
        }
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet'}),
            'content': forms.Textarea(attrs={'id': 'ckeditor', 'class': 'form-control', 'placeholder': 'Contenu'}),
        }


class TextForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = ['title', 'text']
        labels = {
            'title': 'Titre',
            'text': 'Contenu',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre'}),
            'text': forms.Textarea(attrs={'id': 'ckeditor', 'class': 'form-control', 'placeholder': 'Contenu'}),
        }


class ImageForm(forms.ModelForm):
    class Meta:
        model = SliderImage
        fields = ['url', 'title', 'text']
        labels = {
            'url': "Lien de l'Image",
            'title': 'Titre',
            'text': 'Description',
        }
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': "Lien de l'image"}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre'}),
            'text': forms.Textarea(attrs={'id': 'ckeditor', 'class': 'form-control', 'placeholder': 'Contenu'}),
        }
