from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from crop import*
import numpy as np
import os

# returns the letter with the closest euclidian distance to the detected color.
def closestColor(detected_color, alphabet):
    alphabetLength = len(alphabet)
    estimatedColor = 0
    minColorDistance = np.linalg.norm(detected_color - alphabet[0]) 

    for index in range(1, alphabetLength):
        colorDistance = np.linalg.norm(detected_color - alphabet[index]) 

        if colorDistance < minColorDistance:
            estimatedColor = index
            minColorDistance = colorDistance 
            
    return estimatedColor

# returns the average (R, G, B) vector for the sub array in the arr enclosed by border.
# if border =-1,-1 it will go through the whole array
def averageColor(arr, delta, border=(-1, -1)):
    if (border == (-1, -1)):
        border = ((0, 0), (arr.shape[1], arr.shape[0]))

    (top, bottom) = border 
    mean_tone = np.array([0, 0, 0])
    normalise = 1.0 / ((bottom[1] - top[1] - 2*delta) * (bottom[0] - top[0] - 2*delta))

    for i in range(top[1]+delta, bottom[1]-delta):
        for j in range(top[0]+delta, bottom[0]-delta):
            mean_tone += np.resize(arr[i][j], (3,)) # get rid of alpha component, could this be useful?


    return mean_tone * normalise

def centerPoint(border):
    (top, bottom) = border
    diffX = bottom[0] - top[0]
    diffY = bottom[1] - top[1]
    return (top[0] + diffX//2, top[1] + diffY//2)

# decode_box takes a box, which is made up of paritions, and
# returns the average (R, G, B) vector for each partition.
def decode_box(image, box, n_tones, delta):
    n_box = len(box)
    
    tone_list = []
    for (top, bottom) in box:
        #mean_tone = averageColor(ima)e, 0, (top, bottom))
        (x, y) = centerPoint((top, bottom))
        mean_tone = np.resize(image[y][x], (3,))

        #mean_tone = np.array([0, 0, 0])
        #normalise = 1.0 / ((bottom[1] - top[1] - 2*delta) * (bottom[0] - top[0] - 2*delta))
        #for i in range(top[1]+delta, bottom[1]-delta):
        #    for j in range(top[0]+delta, bottom[0]-delta):
        #        mean_tone += image[i][j]
        # if uncommented remember to normalise the vector

        tone_list.append(mean_tone)

    return tone_list

# turns a sequence of colors into estimated alphabet letters.
def estimateQuadrantColors(quadColorSequence, alphabet):
    estimatesColorSquence = []

    for detected_color in quadColorSequence:
        estimatesColorSquence.append(closestColor(detected_color, alphabet))

    return estimatesColorSquence

def getAlphabet(image, box, alphabetLength):
    n_box = len(box)
    
    tone_list = []
    for (top, bottom) in box:
        mean_tone = averageColor(image, 3, (top, bottom))
        #(x, y) = centerPoint((top, bottom))
        #mean_tone = np.resize(image[y][x], (3,))

        tone_list.append(mean_tone)

    return tone_list[:alphabetLength]



# decode_image takes a list of boxes and returns the corresponding
# decode_box for each box
def decode_image(image, boxes, n_tones, delta=0):
    box_tone_list = []

    for box in boxes:
        box_tone_list.append(decode_box(image, box, n_tones, delta))
    return box_tone_list

#
## A simple example of usage
#
#
## Image with 4 colors for edge detection
#file_name = os.path.join(os.path.dirname(__file__), 'Captures/shots1/pic2.png')
#
## Image with some message (i.e. screen partition encodings)
#file_name2 = os.path.join(os.path.dirname(__file__), 'Captures/shots1/pic9.png')
#
#img = Image.open(file_name)
#img2 = Image.open(file_name2)
#
## Output values
#output_path = os.path.join(os.path.dirname(__file__), 'Captures/shots1/cropped/')
#
#arr = np.array(img)
#dim = arr.shape;
#
#arr2 = np.array(img2)
#
#v_part, h_part = 3, 5
#
#partitions = get_unit_crop_coorinates(arr, dim, v_part, h_part)
#
###### TESTING
#for i in range(len(partitions)):
#    for j in range(len(partitions[i])):
#        left = partitions[i][j][0][0]+3
#        upper = partitions[i][j][0][1]+3
#        right = partitions[i][j][1][0]-3
#        lower = partitions[i][j][1][1]-3
#        croped = img2.crop((left, upper, right, lower))
#        croped.save(output_path + str(i) + str(j) + ".png")
###### END OF TESTING
#
#
#decoded = decode_image(arr2, partitions, 2, 3)
#
#for index in decoded:
#    print(index)
#
