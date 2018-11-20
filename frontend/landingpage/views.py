from django.shortcuts import render
from .forms import InstagramProfileName
from django.http import HttpResponse


# Create your views here.
def index(request):
    if request.method == 'POST':
        form = InstagramProfileName(request.POST)
        print(form)
        if form.is_valid():
            return HttpResponse('Analyze profile: {}'.format(form.cleaned_data['profile_name']))
    else:
        form = InstagramProfileName()
    context = { 'form': form }
    return render(request, 'landingpage/index.html', context)