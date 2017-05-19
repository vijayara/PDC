from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from crop import*
import numpy as np
import os

# return the closest color which is in our color set from a given detected color.
# If 2 tons, use a threshold more accurate than closest_color
def closest_color(detected_color, n_tons, threshold=220):
    delta = 256//(2*(n_tons-1))
    r = detected_color[0] > threshold if n_tons == 2 else ((int(round(detected_color[0]))+delta)*(n_tons-1))//255
    g = detected_color[1] > threshold if n_tons == 2 else ((int(round(detected_color[1]))+delta)*(n_tons-1))//255
    b = detected_color[2] > threshold if n_tons == 2 else ((int(round(detected_color[2])+delta))*(n_tons-1))//255
    
    color_index = r*n_tons**2 + g*n_tons + b
    return color_index

# decode_box takes a box, which is made up of paritions, and
# returns the average (R, G, B) vector for each partition.
def decode_box(image, box, n_tones, delta):
    n_box = len(box)
    
    tone_list = []
    for (top, bottom) in box:
        mean_tone = np.array([0, 0, 0])
        normalise = 1.0 / ((bottom[1] - top[1] - 2*delta) * (bottom[0] - top[0] - 2*delta))
        for i in range(top[1]+delta, bottom[1]-delta):
            for j in range(top[0]+delta, bottom[0]-delta):
                mean_tone += image[i][j]

        tone_list.append(closest_color(mean_tone*normalise, n_tones))
        #tone_list.append(np.rint(mean_tone*normalise))

    return tone_list


# decode_image takes a list of boxes and returns the corresponding
# decode_box for each box
def decode_image(image, boxes, n_tones, delta=0):
    box_tone_list = []

    for box in boxes:
        box_tone_list.append(decode_box(image, box, n_tones, delta))
    return box_tone_list


# A simple example of usage


# Image with 4 colors for edge detection
file_name = os.path.join(os.path.dirname(__file__), 'Captures/shots1/pic2.png')

# Image with some message (i.e. screen partition encodings)
file_name2 = os.path.join(os.path.dirname(__file__), 'Captures/shots1/pic9.png')

img = Image.open(file_name)
img2 = Image.open(file_name2)

# Output values
output_path = os.path.join(os.path.dirname(__file__), 'Captures/shots1/cropped/')

arr = np.array(img)
dim = arr.shape;

arr2 = np.array(img2)

v_part, h_part = 3, 5

partitions = get_unit_crop_coorinates(arr, dim, v_part, h_part)

##### TESTING
for i in range(len(partitions)):
    for j in range(len(partitions[i])):
        left = partitions[i][j][0][0]+3
        upper = partitions[i][j][0][1]+3
        right = partitions[i][j][1][0]-3
        lower = partitions[i][j][1][1]-3
        croped = img2.crop((left, upper, right, lower))
        croped.save(output_path + str(i) + str(j) + ".png")
##### END OF TESTING


decoded = decode_image(arr2, partitions, 2, 3)

for index in decoded:
    print(index)

