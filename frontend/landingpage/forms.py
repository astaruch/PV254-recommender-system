from django import forms

class InstagramProfileName(forms.Form):
    profile_name = forms.CharField(
        label='Instagram profile name',
        max_length=100,
        )