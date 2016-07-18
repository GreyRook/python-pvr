import sys

import pvr


def main():
    img = pvr.PVRImage.from_file(sys.argv[1])
    print img
    img.img_a.save(sys.argv[1] + '_a.png')
    img.img_b.save(sys.argv[1] + '_b.png')
    img.img_mod.save(sys.argv[1] + '_mod.png')
