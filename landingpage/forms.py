from django import forms


class InstagramProfileName(forms.Form):
    profile_name = forms.CharField(
        label='Instagram profile name',
        max_length=100,
        )

ALGORITHM_NAMES = [
    ('random', 'Random algorithm'),
    ('naive', 'Naive algorithm'),
    ('improved_label', 'Improved label matching algorithm'),
    ('vector_distance', 'Vector distance algorithm'),
]

class RankingAlgorithmName(forms.Form):
    algorithm_name = forms.Select(choices=ALGORITHM_NAMES)


class MultipleFilesUpload(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
