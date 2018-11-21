from django.shortcuts import render, redirect
from .forms import InstagramProfileName
from django.http import JsonResponse
import sys
from lib import instagram_downloader, vision_image_analyzer, database_sql_commands
import os
from django.db import connection


# Create your views here.
def index(request):
    if request.method == 'POST':
        form = InstagramProfileName(request.POST)
        print(form)
        if form.is_valid():
            profile_name = form.cleaned_data['profile_name']
            return redirect('profile', profile_name=profile_name)
            # instagram_downloader.download_profile(profile=profile_name, folder_prefix='profiles')
            #
            # return HttpResponse('Analyze profile: {}'.format(form.cleaned_data['profile_name']))
    else:
        form = InstagramProfileName()
    context = { 'form': form }
    return render(request, 'index.html', context)


def profile(request, profile_name):
    directory_string = os.path.join('profiles/%s/' % profile_name)
    directory = os.fsencode(directory_string)
    try:
        # -1 because Instagram downloader downloads an id file.
        images_count = len(os.listdir(directory)) - 1
    except FileNotFoundError:
        images_count = 0

    analyzed_count = 0
    with connection.cursor() as cursor:
        cursor.execute(database_sql_commands.CREATE_TABLE_IMAGE_LABEL)

        analyzed_count = cursor.execute(
            'SELECT COUNT(*) FROM (SELECT DISTINCT path_prefix, filename FROM image_label WHERE path_prefix = %s)',
            (directory_string,)).fetchone()[0]

    return render(request, 'profile.html', context={
        'profile_name': profile_name,
        'images_count': images_count,
        'analyzed_count': analyzed_count
    })


def download_profile(request, profile_name):
    if request.method == 'POST':
        instagram_downloader.download_profile(profile=profile_name, folder_prefix='profiles')

    return redirect('profile', profile_name=profile_name)


def analyze_profile(request, profile_name):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            directory_string = os.path.join('profiles/%s/' % profile_name)

            cursor.execute(database_sql_commands.CREATE_TABLE_IMAGE_LABEL)

            def callback_is_analyzed(filename):
                return cursor.execute(
                    'SELECT COUNT(*) FROM image_label WHERE path_prefix = %s AND filename = %s',
                    (directory_string, filename)).fetchone()[0] > 0

            def callback_store_labels(filename, label_annotations):
                for label_annotation in label_annotations:
                    cursor.execute(
                        'INSERT INTO image_label (`path_prefix`, `filename`, `label`, `score`) VALUES (%s, %s, %s, %s)',
                        (directory_string,
                         filename,
                         label_annotation.description,
                         label_annotation.score))

            vision_image_analyzer.annotate_images(directory_string, callback_is_analyzed, callback_store_labels)

    return redirect('profile', profile_name=profile_name)


def recommendations(request, profile_name):
    directory_string = os.path.join('candidates/%s/' % profile_name)
    directory = os.fsencode(directory_string)
    try:
        images_count = len(os.listdir(directory))
    except FileNotFoundError:
        images_count = 0

    analyzed_count = 0
    # with connection.cursor() as cursor:
    #     cursor.execute(database_sql_commands.CREATE_TABLE_IMAGE_LABEL)
    #
    #     analyzed_count = cursor.execute(
    #         'SELECT COUNT(*) FROM (SELECT DISTINCT path_prefix, filename FROM image_label WHERE path_prefix = %s)',
    #         (directory_string,)).fetchone()[0]

    return render(request, 'recommendations.html', context={
        'profile_name': profile_name,
        'images_count': images_count,
        'analyzed_count': analyzed_count
    })