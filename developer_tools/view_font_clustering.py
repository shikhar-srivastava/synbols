"""Tools for visualizing current font clusters.

Usage:
$ cd /where/the/png/will/be/saved
$ synbols view_font_clustering.py
"""

import json
from synbols.generate import basic_attribute_sampler
from synbols.drawing import SolidColor
import numpy as np
from PIL import Image
import sys


def cluster_to_img_grid(font_cluster):
    bg = SolidColor((0, 0, 0))
    fg = SolidColor((1, 1, 1))

    img_grid = []
    for font, _d in font_cluster:
        img_list = []
        for char in 'abcdefghijkl':
            img = basic_attribute_sampler(font=font, char=char, is_bold=False, is_slant=False, scale=1.,
                                          translation=(0, 0),
                                          background=bg, foreground=fg, rotation=0, inverse_color=False,
                                          resolution=(128, 128))()
            img_list.append(img.make_image())

        img_grid.append(np.hstack(img_list))
    return np.vstack(img_grid)


if __name__ == "__main__":

    # print("current number of latin fonts %d" % (len(ALPHABET_MAP['latin'].fonts)))

    with open('./font_clusters.json') as fd:
        clusters = json.load(fd)

    for i, cluster in enumerate(clusters):
        for name, val in cluster:
            print(name, "%.3g" % val)
        print()

        names = [name for name, val in cluster]

        img_grid = cluster_to_img_grid(cluster)

        Image.fromarray(img_grid).save("%s.png" % ('_'.join(names)))
