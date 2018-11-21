from django.shortcuts import render
from .forms import InstagramProfileName
from django.http import HttpResponse
import sys
from lib import instagram_downloader


# Create your views here.
def index(request):
    if request.method == 'POST':
        form = InstagramProfileName(request.POST)
        print(form)
        if form.is_valid():
            profile_name = form.cleaned_data['profile_name']
            instagram_downloader.download_profile(profile=profile_name, folder_prefix='profiles')

            return HttpResponse('Analyze profile: {}'.format(form.cleaned_data['profile_name']))
    else:
        form = InstagramProfileName()
    context = { 'form': form }
    return render(request, 'landingpage/index.html', context)