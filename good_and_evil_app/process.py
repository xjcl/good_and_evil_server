from PIL import Image, ImageDraw, ImageFont
import numpy
import datetime


def print_bool_matrix(a: numpy.ndarray):
    """Prints a 2D numpy array as a string of X's and .'s, for documentation"""
    for row in a:
        print("".join("X" if el else "." for el in row))


def run(
    size=720,
    ssaa=2,
    get_id=lambda: "good_and_evil_" + str(datetime.datetime.now().isoformat()),
    color_dark=(0, 0, 0),
    str1="TALLY",
    str2="HALL",
    font_face="Helvetica-Bold-Font.ttf",
    font_size=70,
):
    """
    Function which generates a fractal artwork in the style of Tally Hall's "Good and Evil" album
        cover and stores it in the file system.

    :param size: Width and height of output image in px
    :param ssaa: Super-sampling anti-aliasing as used in video games.
        The artwork is rendered at a multiple (typically 2x) of the original resolution, then down-
        scaled to the originally requested resolution, which reduces aliasing at color boundaries.
    :param get_id: Function which returns path to save output png to
    :param color_dark: Artwork will contain pattern made of white and {color_dark}.
        Triple with values in the range [0, 255]
    :param str1: Top-left string in artwork, defaults to "TALLY"
    :param str2: Top-right string in artwork, defaults to "HALL"
    :param font_face: Font face to use for painting str1 and str2
    :param font_size: Font size to use for painting str1 and str2
    """

    size *= ssaa
    run_id = get_id()

    """
    Create 2D matrix with actual X (Y) coordinate of each pixel
    X(size=8):                                       Y(size=8):
        -3.5 -2.5 -1.5 -0.5 +0.5 +1.5 +2.5 +3.5         -3.5 -3.5 -3.5 -3.5 -3.5 -3.5 -3.5 -3.5 
        -3.5 -2.5 -1.5 -0.5 +0.5 +1.5 +2.5 +3.5         -2.5 -2.5 -2.5 -2.5 -2.5 -2.5 -2.5 -2.5
                          ...                                             ... 
        -3.5 -2.5 -1.5 -0.5 +0.5 +1.5 +2.5 +3.5         +3.5 +3.5 +3.5 +3.5 +3.5 +3.5 +3.5 +3.5 
    """
    x = numpy.tile(numpy.arange(size), (size, 1)) - size / 2 + .5
    y = numpy.tile(numpy.arange(size).reshape(size, 1), size) - size / 2 + .5

    """
    Create the 4 "blades" of the fractal as 2D binary mask (X = True = white color)
       x * y > 0:   abs(x) > abs(y):  mask(size=8):
        XXXX....        ........        ....XXX.
        XXXX....        X......X        X...XX..
        XXXX....        XX....XX        XX..X...
        XXXX....        XXX..XXX        XXX.....
        ....XXXX        XXX..XXX        .....XXX
        ....XXXX        XX....XX        ...X..XX
        ....XXXX        X......X        ..XX...X
        ....XXXX        ........        .XXX....
    """
    mask = ((abs(x) > abs(y)) & (x * y > 0)) | ((abs(x) < abs(y)) & (x * y < 0))

    # True cells -> white pixel (255, 255, 255)   False cells -> {color_dark} pixel
    pixels_outer = numpy.where(
        numpy.repeat(mask[:, :, numpy.newaxis], 3, axis=2),  # repeat 3 times across R/G/B channels
        numpy.array([[[255, 255, 255]]]),
        numpy.array([[color_dark]]),
    ).astype(numpy.uint8)

    """
    Apply the 8 letterings around the rim of the artwork
    image_outer(size=8):
             TOP1  TOP2
              ....XXX.
        UPPER X...XX.. UPPER
        SIDE1 XX..X... SIDE2
              XXX.....
              .....XXX
        LOWER ...X..XX LOWER
        SIDE1 ..XX...X SIDE2
              .XXX....
             BOT1  BOT2
    """

    image_outer = Image.fromarray(pixels_outer, "RGB")
    draw = ImageDraw.Draw(image_outer)
    font = ImageFont.truetype(font_face, font_size * ssaa)

    # https://stackoverflow.com/a/59008967/2111778
    w1 = draw.textsize(str1, font=font)[0] + font.getoffset(str1)[0]
    h1 = draw.textsize(str1, font=font)[1] + font.getoffset(str1)[1]
    w2 = draw.textsize(str2, font=font)[0] + font.getoffset(str2)[0]
    h2 = draw.textsize(str2, font=font)[1] + font.getoffset(str2)[1]

    # TOP
    draw.text((1 * size / 4 - w1 / 2,  1 * size / 20 - h1 / 2), str1, font=font, fill=(255, 255, 255))
    draw.text((3 * size / 4 - w2 / 2,  1 * size / 20 - h2 / 2), str2, font=font, fill=color_dark)

    # UPPER SIDES
    image_outer = image_outer.rotate(90)
    image_outer = image_outer.transpose(Image.FLIP_LEFT_RIGHT)
    draw = ImageDraw.Draw(image_outer)
    draw.text((3 * size / 4 - w1 / 2,  1 * size / 20 - h1 / 2), str1, font=font, fill=(255, 255, 255))
    draw.text((3 * size / 4 - w2 / 2, 19 * size / 20 - h2 / 2), str2, font=font, fill=color_dark)

    # LOWER SIDES
    image_outer = image_outer.transpose(Image.FLIP_LEFT_RIGHT)
    draw = ImageDraw.Draw(image_outer)
    draw.text((3 * size / 4 - w1 / 2,  1 * size / 20 - h1 / 2), str1, font=font, fill=color_dark)
    draw.text((3 * size / 4 - w2 / 2, 19 * size / 20 - h2 / 2), str2, font=font, fill=(255, 255, 255))

    # BOTTOM
    image_outer = image_outer.rotate(90)
    image_outer = image_outer.transpose(Image.FLIP_LEFT_RIGHT)
    draw = ImageDraw.Draw(image_outer)
    draw.text((1 * size / 4 - w1 / 2,  1 * size / 20 - h1 / 2), str1, font=font, fill=color_dark)
    draw.text((3 * size / 4 - w2 / 2,  1 * size / 20 - h2 / 2), str2, font=font, fill=(255, 255, 255))

    # return to original orientation
    image_outer = image_outer.transpose(Image.FLIP_LEFT_RIGHT)
    image_outer = image_outer.rotate(180)

    image_outer.save(run_id + "_outer.png")

    """
    Determine the coordinates which are on the rim and thus form the "base case".
    All other coordinates (. = False = those inside the diamond) require recursion!
    is_outer(size=8):
        XXX..XXX
        XX....XX
        X......X
        ........
        ........
        X......X
        XX....XX
        XXX..XXX

    Recursion:
        Base case: For points on the rim, the pixel data is already accurate.
        Recurse: For points inside the diamond, reach next layer via the operation
            "45 degree counter-clockwise turn + sqrt(2) scaling" (visually obvious)
            Note that we have the y-axis pointing down so positive rotations go CLOCKWISE
                      ^ -y
                      |
                -x <--+--> [+x]
                      |
                      v [+y]
            https://en.wikipedia.org/wiki/Scaling_(geometry)  Scaling matrix
                [sqrt(2)   0    ]
                [  0     sqrt(2)]
            https://en.wikipedia.org/wiki/Rotation_matrix  Rotation matrix
                [cos phi  -sin phi]     [cos -45  -sin -45]     [ 1/sqrt(2)  1/sqrt(2)]
                [sin phi   cos phi]  =  [sin -45   cos -45]  =  [-1/sqrt(2)  1/sqrt(2)]
            If we apply both, we multiply them together
                [sqrt(2)   0    ]  [ 1/sqrt(2)  1/sqrt(2)]     [ 1  1]
                [  0     sqrt(2)]  [-1/sqrt(2)  1/sqrt(2)]  =  [-1  1]
            Thus we transform each inner point as follows
                [ 1  1] [x]     [y+x]
                [-1  1] [y]  =  [y-x]

    Every iteration paints in half of the remaining pixels, so we can either do
        - log2(size * size) iterations
            - size = 720  =>  log2(720 * 720) = 18.98 iterations
        - iterate until x and y no longer change
            - experimentally this was after 18 modifications, so this condition is sound
    """
    num_iterations = int(numpy.log2(size * size)) + 1
    for d in range(num_iterations):
        is_outer = abs(x) + abs(y) > size / 2
        x, y = (
            numpy.where(is_outer, x, y + x),
            numpy.where(is_outer, y, y - x)
        )

    # Map coordinates back from e.g. [-3.5, 3.5] to [0, 7]
    x_, y_ = x + size / 2 - .5, y + size / 2 - .5

    # TODO Maybe use 'round' here instead of 'int'?
    pixels = numpy.array(image_outer)[y_.astype(int), x_.astype(int), :]
    image = Image.fromarray(pixels, "RGB")
    image.save(run_id + "_SSAA.png")
    image = image.resize((size // ssaa, size // ssaa))
    image.save(run_id + ".png")


if __name__ == "__main__":
    run(get_id=lambda: "new_algo")
