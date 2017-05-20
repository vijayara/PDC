from crop import*
from image_decoding import*
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

maskUp = 'maskUp'
maskDown = 'maskDown'
maskLeft = 'maskLeft'
maskRight = 'maskRight' 
maskUpDown = 'maskUpDown'
maskDownUp = 'maskDownUp'
noMask = 'noMask'

mask = (-1, -1)


v_part, h_part = 3, 5

def flattenBorder(border):
    (top, bottom) = border
    return (top[0], top[1], bottom[0], bottom[1])


# If we have 4 samples of each image, and we want to take each third one:
timingInterpolationStart = 2 
timingInterpolationJump = 4

# Get mask returns the mask type based on the location list (see crop)
def getMask(location_list):

    [locUL, locUR, locDL, locDR] = location_list

    if locUL == mask and locUR == mask:
        return maskUp
    elif locDL == mask and locDR == mask:
        return maskDown
    elif locUL == mask and locDL == mask:
        return maskLeft
    elif locUR == mask and locDR == mask:
        return maskRight
    elif locUL == mask and locDR == mask:
        return maskUpDown
    elif locDL == mask and locUR == mask:
        return maskDownUp

    return noMask



# returns the mask type as well as the corners associated.
def extractStartingScreen(images):

    img = Image.open(images[0])
    arr = np.array(img)
    dim = arr.shape

    maskCase = getMask(get_color_positions(arr, dim))
    borders = get_borders(arr, dim)

    (arr1, arr2) = getQuadrants(borders, images[0])
    colorFirstQuad = averageColor(arr1, 0)
    colorSecondQaud = averageColor(arr2, 0)

    return (borders, maskCase, (colorFirstQuad, colorSecondQaud))

# takes an image and returns the arrays corresponding to the quadrants
def getQuadrants(border,image):
    img = Image.open(image)
    (top, bottom) = border[0]
    (top2, bottom2) = border[1]
    arr1 = np.array(img.crop((top[0], top[1], bottom[0], bottom[1])))
    arr2 = np.array(img.crop((top2[0], top2[1], bottom2[0], bottom2[1])))
    return (arr1, arr2)

# Euclidian distance between vector c1 and c2
def distance(c1, c2):
    return np.linalg.norm(c1 - c2) 

# returns true if the colors passed (c1, and c2) correspon to the 
# starting screen colors 
def isStartingScreen(c1, c2, colorFirstQuad, colorSecondQaud):
    delta = 5 # Note from expermiment, same screen seems to the order of 2, while different around 60
    return distance(c1, colorFirstQuad) < delta and distance(c2, colorSecondQaud) < delta


# Finds the index after which the last starting screen appears.
def findEndOfStartingSequence(images, borders, colorFirstQuad, colorSecondQaud):

    endOfStartingSequenceReached = False
    
    itr = 1 # 1 since we have extraced the starting sequence already

    while not endOfStartingSequenceReached:
        
        (arr1, arr2) = getQuadrants(borders, images[itr])
        c1 = averageColor(arr1, 0)
        c2 = averageColor(arr2, 0)

        if (not isStartingScreen(c1, c2, colorFirstQuad, colorSecondQaud)):
            endOfStartingSequenceReached = True
            return itr

        itr = itr + 1

    return itr



# Once we have the mask and the beginning of the alphabet, get the proper sequence indexing based
# on actualt order. Go through it to extract the alphabet, and message
  
file_path = 'testsmay19/good1/pic'
extension = '.png'
start_seq = 21
end_seq = 119
images = []

for index in range(start_seq, end_seq + 1):
    images.append(file_path + str(index) + extension)

(borders, maskCase, quadColors) = extractStartingScreen(images)
endOfStartingSequence = findEndOfStartingSequence(images, borders, quadColors[0], quadColors[1])

# Remove Starting sequence and interpolate the images at proper interval.
images = images[endOfStartingSequence:]
images = images[timingInterpolationStart::timingInterpolationJump]

#print(images)


img = Image.open(images[0])
arr = np.array(img)


box = get_unit_crop_coorinates(borders, v_part, h_part)
print(' - - -  ')
print(box[1])
#
#
cols = getAlphabet(arr, box[1], 8)
for c in cols:
    print(c)


#
## Croping test
#img = Image.open('testsmay19/good1/pic22.png')
#source_img = img.convert("RGBA")
#draw = ImageDraw.Draw(source_img)
##
#for (top, bottom) in borders:
#    draw.rectangle((top, bottom), fill="white")
#
#source_img.save('quickTest.png', "PNG")
