import sys

from bitstring import ConstBitStream
import PIL.Image


def scale_to_255(color, size):
    number = float(color) / 2**size
    return int(number * 255)


def compact(x):
    x &= 0x55555555                  # x = -f-e -d-c -b-a -9-8 -7-6 -5-4 -3-2 -1-0
    x = (x ^ (x >> 1)) & 0x33333333  # x = --fe --dc --ba --98 --76 --54 --32 --10
    x = (x ^ (x >> 2)) & 0x0f0f0f0f  # x = ---- fedc ---- ba98 ---- 7654 ---- 3210
    x = (x ^ (x >> 4)) & 0x00ff00ff  # x = ---- ---- fedc ba98 ---- ---- 7654 3210
    x = (x ^ (x >> 8)) & 0x0000ffff
    return x


def decode_morton(i):
    x = compact(i)
    y = compact(i >> 1)
    return x, y


class PVRImage(object):
    def __init__(self):
        self.img_a = None
        self.img_b = None
        self.img_mod = None

    @classmethod
    def from_file(cls, file_path):
        re = cls()

        with open(file_path, 'rb') as f:
            bit_stream = ConstBitStream(f)
            version = bit_stream.read('hex:32')
            print version
            flags = bit_stream.read('uintle:32')
            print flags
            pixel_format = bit_stream.read('uintle:64')
            print pixel_format
            colour_space = bit_stream.read('uintle:32')
            print colour_space
            channel_type = bit_stream.read('uintle:32')
            print channel_type
            height = bit_stream.read('uintle:32')
            print 'Height', height
            width = bit_stream.read('uintle:32')
            print 'Width', width
            depth = bit_stream.read('uintle:32')
            print depth
            num_surfaces = bit_stream.read('uintle:32')
            print num_surfaces
            num_faces = bit_stream.read('uintle:32')
            print num_faces
            mip_map_count = bit_stream.read('uintle:32')
            print mip_map_count
            meta_data_size = bit_stream.read('uintle:32')
            print meta_data_size
            meta_data = bit_stream.read('bytes:{}'.format(meta_data_size))

            # for now not supported:
            # * mip map
            # * multiples surfaces
            # * multiple faces
            assert mip_map_count == 1
            assert num_surfaces == 1
            assert num_faces == 1

            for mip in xrange(mip_map_count):
                for surface in xrange(num_surfaces):
                    for face in xrange(num_faces):
                        for slice in xrange(depth):
                            image_width = width/4/2**(mip)
                            image_height = height/4/2**(mip)

                            img_a = PIL.Image.new('RGBA', (width/4, height/4))
                            img_a_data = img_a.load()
                            img_b = PIL.Image.new('RGBA', (width/4, height/4))
                            img_b_data = img_b.load()
                            img_mod = PIL.Image.new('RGBA', (width, height))
                            img_mod_data = img_mod.load()

                            for i in xrange(image_width * image_height):
                                    pixel, row = decode_morton(i)
                                    modulation_data = bit_stream.read('bits:32')
                                    byte0 = bit_stream.read('bits:8')
                                    byte1 = bit_stream.read('bits:8')
                                    byte2 = bit_stream.read('bits:8')
                                    byte3 = bit_stream.read('bits:8')

                                    color_mode = byte3.read('bool')

                                    r = g = b = a = 255
                                    if color_mode:
                                        r = byte3.read('uint:5')
                                        g = (byte3.read('bits:2') + byte2.read('bits:3')).read('uint:5')
                                        b = byte2.read('uint:5')
                                        r = scale_to_255(r, 5)
                                        g = scale_to_255(g, 5)
                                        b = scale_to_255(b, 5)
                                    else:
                                        a = byte3.read('uint:3')
                                        r = byte3.read('uint:4')
                                        g = byte2.read('uint:4')
                                        b = byte2.read('uint:4')
                                        a = scale_to_255(a, 3)
                                        r = scale_to_255(r, 4)
                                        g = scale_to_255(g, 4)
                                        b = scale_to_255(b, 4)
                                    img_b_data[row, pixel] = (r, g, b, a)

                                    color_mode = byte1.read('bool')


                                    r = g = b = a = 255
                                    if color_mode:
                                        r = byte1.read('uint:5')
                                        g = (byte1.read('bits:2') + byte0.read('bits:3')).read('uint:5')
                                        b = byte0.read('uint:4')
                                        r = scale_to_255(r, 5)
                                        g = scale_to_255(g, 5)
                                        b = scale_to_255(b, 4)
                                    else:
                                        a = byte1.read('uint:3')
                                        r = byte1.read('uint:4')
                                        g = byte0.read('uint:4')
                                        b = byte0.read('uint:3')
                                        a = scale_to_255(a, 3)
                                        r = scale_to_255(r, 4)
                                        g = scale_to_255(g, 4)
                                        b = scale_to_255(b, 3)

                                    img_a_data[row, pixel] = (r, g, b, a)

                                    mode = byte0.read('bool')

                                    for r in xrange(4):
                                        for c in xrange(4):
                                            first = modulation_data.read('uint:1')
                                            last = modulation_data.read('uint:1')
                                            value = 0
                                            if first == 0 and last == 0:
                                                value = 0
                                            elif first == 0 and last == 1:
                                                value = 3
                                            elif first == 1 and last == 0:
                                                value = 5
                                            elif first == 1 and last == 1:
                                                value = 8
                                            texel_row = 3 - r + row*4
                                            texel_col = 3 - c + pixel*4
                                            img_mod_data[texel_row, texel_col] = (0, 0, 0, int(float(value)/8*255))

                            re.img_a = img_a
                            re.img_b = img_b
                            re.img_mod = img_mod # .save('img_mod_{}.png'.format(mip))
                            return re
