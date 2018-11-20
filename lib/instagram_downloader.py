import instaloader


def download_profile(profile, folder_prefix):
    loader = instaloader.Instaloader(
        dirname_pattern='%s/{target}' % folder_prefix,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern='')

    loader.context.raise_all_errors = True
    loader.download_profile(profile, profile_pic=False, fast_update=True)
