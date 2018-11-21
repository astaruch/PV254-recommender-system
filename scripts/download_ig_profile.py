import argparse

from lib import instagram_downloader


class DownloadIgProfile(object):
    def __init__(self):
        self.options = self.parse_commandline()

    @staticmethod
    def parse_commandline():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--folder', type=str, default='profiles', required=False,
                            help='Folder prefix where to store downloads.')
        parser.add_argument('--profile', type=str, default=None, required=True,
                            help='Instagram profile to be downloaded.')
        return parser.parse_args()

    def run(self):
        instagram_downloader.download_profile(self.options.profile, self.options.folder)


if __name__ == '__main__':
    download_ig_profile = DownloadIgProfile()
    download_ig_profile.run()
