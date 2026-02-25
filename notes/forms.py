from django import forms
from .models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-deep border border-gold border-opacity-20 text-white rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-gold transition',
                'placeholder': 'Note title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full bg-deep border border-gold border-opacity-20 text-white rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-gold transition h-64',
                'placeholder': 'Write your note here...'
            })
        }
