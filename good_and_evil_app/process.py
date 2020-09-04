from PIL import Image, ImageDraw, ImageFont
import numpy
import multiprocessing
import datetime
import functools


def makePixel(xy, SIZE, SSAA, maxdepth, imageOuter, colorLo):
    '''makePixel returns the color value of a single pixel in the resulting image.

    - SSAA (super-sample anti-alias) is applied to avoid jagged edges at color transitions
    - This needs to be a top-level function so it can be parallelized with multiprocessing
    - DEPRECATED in favor of faster makePixelsNumpy'''

    def isOuter(x, y):
        return abs(x) + abs(y) > SIZE/2

    def isInside(x, y):
        return abs(x) > abs(y) and abs(x * y) == x * y or abs(x) < abs(y) and abs(x * y) != x * y

    def pixelFractal(x, y, depth=0):

        if isOuter(x, y) or depth >= maxdepth:
            if imageOuter:
                x_, y_ = x + SIZE/2 - .5, y + SIZE/2 - .5
                # if x_ < 0 or x_ > SIZE - 1 or y_ < 0 or y_ > SIZE - 1:
                #     print('!!!', x_, y_)
                return imageOuter.getpixel((x_, y_))
            else:
                return (255,255,255) if isInside(x, y) else colorLo

        # rotate 45 degrees ccwise and stretch by sqrt(2)
        return pixelFractal(x - y, x + y, depth+1)

    def pixelImage(x, y):
        GRID_SIZE = SSAA  # creates grid of SSAA**2 pixels
        if GRID_SIZE == 1 or (isOuter(x, y) and maxdepth > 0):
            res = numpy.array(numpy.array( [pixelFractal(x, y)] ))
        else:
            x_topleft = x - 1/2 + 1/(2*GRID_SIZE)
            y_topleft = y - 1/2 + 1/(2*GRID_SIZE)
            res = numpy.array([
                numpy.array( pixelFractal(x_topleft + dx/GRID_SIZE, y_topleft + dy/GRID_SIZE) )
                for dx in range(GRID_SIZE) for dy in range(GRID_SIZE)
            ])
        return tuple( (res.sum(axis=0) / len(res)).astype(int) )

    return pixelImage(xy[0], xy[1])


def makePixelsNumpy(SIZE, SSAA, maxdepth, imageOuter, colorLo):
    '''makePixelsNumpy returns the G&E fractal image using efficient numpy code and recursion.
    This does NOT apply text/captions.'''

    def isOuter(x, y):
        return abs(x) + abs(y) > SIZE/2

    def isInside(x, y):
        return ((abs(x) > abs(y)) & (abs(x * y) == x * y)) | ((abs(x) < abs(y)) & (abs(x * y) != x * y))

    def pixelFractal():
        x = numpy.tile(numpy.arange(SIZE), (SIZE, 1)) - SIZE/2 + .5
        y = numpy.tile(numpy.arange(SIZE).reshape(SIZE, 1), SIZE) - SIZE/2 + .5

        for depth in range(maxdepth):
            x, y = numpy.where(~isOuter(x, y), x + y, x), numpy.where(~isOuter(x, y), y - x, y)

        if imageOuter:
            # TODO does this round correctly?
            x_, y_ = x + SIZE/2 - .5, y + SIZE/2 - .5
            return numpy.array(imageOuter)[y_.astype(int), x_.astype(int), :]
        else:
            base = numpy.repeat(isInside(x, y)[:, :, numpy.newaxis], 3, axis=2)
            ret = numpy.where(base, numpy.array([255,255,255])[None, None, :], numpy.array(colorLo)[None, None, :])
            return ret.astype(numpy.uint8)

    return pixelFractal()


def run(SIZE=720, SSAA=2, getId=lambda: 'good_and_evil_' + str(datetime.datetime.now().isoformat()), colorLo=(0,0,0), str1='TALLY', str2='HALL', fontFace="Helvetica-Bold-Font.ttf", fontSize=70):
    '''Does a full run to create a custom image in the style of Tally Hall's 'Good & Evil' album cover

    - Calls to makePixel are parallelized on multi-core CPUs
    - A careful sequence of steps is taken to add antialiasing while avoiding blurring:
        1. Outer layer of the fractal is created WITH anti-aliasing
        2. Font is rendered on outer layer (by its nature this has built-in anti-aliasing!)
        3. Rest of the image is created by recursively going up layers until outer layer is reached
    - Calling this function is ILLEGAL without listening to the album first!'''

    ORIG_SIZE = SIZE
    SIZE = SIZE * SSAA

    def makeImage(SIZE, SSAA, maxdepth, imageOuter, colorLo):
        pixels = makePixelsNumpy(SIZE=SIZE, SSAA=SSAA, maxdepth=maxdepth, imageOuter=imageOuter, colorLo=colorLo)
        return Image.fromarray(pixels, 'RGB')

    def captionOuter(im_outer):
        draw = ImageDraw.Draw(im_outer)
        # font = ImageFont.truetype("LiberationSans-Bold.ttf", 70)
        # font = ImageFont.truetype("NimbusSanL-Bol.otf", 70)
        font = ImageFont.truetype(fontFace, fontSize * SSAA)
        w1, h1 = draw.textsize(str1, font=font)
        w2, h2 = draw.textsize(str2, font=font)
        # https://stackoverflow.com/a/59008967/2111778
        w1 += font.getoffset(str1)[0]
        h1 += font.getoffset(str1)[1]
        w2 += font.getoffset(str2)[0]
        h2 += font.getoffset(str2)[1]

        # TOP SIDE
        draw.text((  SIZE/4-w1/2, SIZE/20-h1/2), str1, font=font, fill=(255,255,255))
        draw.text((3*SIZE/4-w2/2, SIZE/20-h2/2), str2, font=font, fill=colorLo)
        im_outer = im_outer.rotate(90)

        # LEFT SIDE
        im_outer = im_outer.transpose(Image.FLIP_LEFT_RIGHT)
        draw = ImageDraw.Draw(im_outer)
        draw.text((3*SIZE/4-w1/2,   SIZE/20-h1/2), str1, font=font, fill=(255,255,255))
        draw.text((3*SIZE/4-w2/2,19*SIZE/20-h2/2), str2, font=font, fill=colorLo)
        im_outer = im_outer.transpose(Image.FLIP_LEFT_RIGHT)
        # RIGHT SIDE !!!
        draw = ImageDraw.Draw(im_outer)
        draw.text((3*SIZE/4-w1/2,   SIZE/20-h1/2), str1, font=font, fill=colorLo)
        draw.text((3*SIZE/4-w2/2,19*SIZE/20-h2/2), str2, font=font, fill=(255,255,255))
        im_outer = im_outer.rotate(90)

        # BOTTOM SIDE
        im_outer = im_outer.transpose(Image.FLIP_LEFT_RIGHT)
        draw = ImageDraw.Draw(im_outer)
        draw.text((3*SIZE/4-w2/2, SIZE/20-h2/2), str2, font=font, fill=(255,255,255))
        draw.text((  SIZE/4-w1/2, SIZE/20-h1/2), str1, font=font, fill=colorLo)
        im_outer = im_outer.transpose(Image.FLIP_LEFT_RIGHT)
        im_outer = im_outer.rotate(180)

        return im_outer

    runId = getId()
    imageOuter = makeImage(SIZE, SSAA=SSAA, maxdepth=0, imageOuter=None, colorLo=colorLo)
    imageOuter = captionOuter(imageOuter)
    imageOuter.save(runId + '_outer.png')

    image = makeImage(SIZE, SSAA=SSAA, maxdepth=25, imageOuter=imageOuter, colorLo=colorLo)
    image.save(runId + '_SSAA.png')
    image.thumbnail((ORIG_SIZE, ORIG_SIZE))
    image.save(runId + '.png')
    return runId + '.png'

run()
