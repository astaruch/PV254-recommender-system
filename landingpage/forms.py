from django import forms


class InstagramProfileName(forms.Form):
    profile_name = forms.CharField(
        label='Instagram profile name',
        max_length=100,
        )


class MultipleFilesUpload(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
