from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from crop import*
#from camera_decoding import closest_color
import numpy as np

# decode_box takes a box, which is made up of paritions, and
# returns the average (R, G, B) vector for each partition.
def decode_box(image, box, n_tones):
    n_box = len(box)
    
    tone_list = []
    for (top, bottom) in box:
        mean_tone = np.array([0, 0, 0])
        normalise = 1.0 / ((bottom[1] - top[1]) * (bottom[0] - top[0])) *1.0
        for i in range(top[1], bottom[1]):
            for j in range(top[0], bottom[0]):
                mean_tone += image[i][j]

        #tone_list.append(closest_color(mean_tone, n_tones))
        tone_list.append(mean_tone * normalise)

    return tone_list


# decode_image takes a list of boxes and returns the corresponding 
# decode_box for each box
def decode_image(image, boxes, n_tones):
    box_tone_list = []

    for box in boxes:
        box_tone_list.append(decode_box(image, box, n_tones))
    return box_tone_list


# A simple example of usage


# Image with 4 colors for edge detection
file_name = "/Users/aleman/GDrive/EPFL/ba3/pdc/PDC/Captures/shots1/pic2.png"

# Image with some message (i.e. screen partition encodings)
file_name2 = "/Users/aleman/GDrive/EPFL/ba3/pdc/PDC/Captures/shots1/pic12.png"

img = Image.open(file_name)
img2 = Image.open(file_name2)

# Output values
output_name = "crop_output_test1.png"
corner_output="corner_output"


arr = np.array(img)
dim = arr.shape;

arr2 = np.array(img2)


source_img = img.convert("RGBA")
draw = ImageDraw.Draw(source_img)

v_part, h_part = 3, 5

partitions = get_unit_crop_coorinates(arr, dim, v_part, h_part)
ans = decode_image(arr2, partitions, 2)

for (a, b) in zip(ans[2], ans[1]):
    print(a - b)

