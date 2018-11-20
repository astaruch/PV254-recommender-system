import argparse
import urllib.request
import os
import random


class DownloadRandomImages(object):
    def __init__(self):
        self.options = self.parse_commandline()

    @staticmethod
    def parse_commandline():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--count', type=int, default=10, required=False,
                            help='How many images should be downloaded.')
        parser.add_argument('--width', type=int, default=800, required=False,
                            help='Width of images.')
        parser.add_argument('--height', type=int, default=600, required=False,
                            help='Height of images.')
        parser.add_argument('--folder', type=str, default='resources/random-images', required=False,
                            help='Folder where images will be stored.')
        return parser.parse_args()

    def run(self):
        if not os.path.exists(self.options.folder):
            os.makedirs(self.options.folder)

        min_id = 0
        max_id = 1084

        for index, image_id in enumerate(random.sample(range(min_id, max_id), self.options.count)):
            image_filename = '%s/%s.jpg' % (self.options.folder, image_id)
            if not os.path.exists(image_filename):
                urllib.request.urlretrieve(
                    'https://picsum.photos/%s/%s?image=%s' % (self.options.width, self.options.height, image_id),
                    image_filename)
                print('%s: Downloaded image.' % (index + 1))
            else:
                print('%s: Image with id %s already exists.' % ((index + 1), image_id))


if __name__ == '__main__':
    download_random_images = DownloadRandomImages()
    download_random_images.run()
