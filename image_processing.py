from crop import*
from image_decoding import*
from image_creation.py import base_change
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance

# dictionnary for mask
noMask = 0
maskUp = 1
maskDown = 2
maskLeft = 3
maskRight = 4
maskUpDown = 5
maskDownUp = 6

mask = (-1, -1)


# Parameters

alphabetLength = 8
paddingSize = 2

avgColorDelta = 3
v_part, h_part = 3, 5

# If we have 4 samples of each image, and we want to take each third one:
timingInterpolationStart = 2 
timingInterpolationJump = 4

# Images 

file_path = 'testsmay19/good1/pic'
extension = '.png'
start_seq = 21
end_seq = 119
images = []

for index in range(start_seq, end_seq + 1):
    images.append(file_path + str(index) + extension)




# Beau code

flatten = lambda l: [item for sublist in l for item in sublist]

# turn border into right format for .crop method
def flattenBorder(border):
    (top, bottom) = border
    return (top[0], top[1], bottom[0], bottom[1])

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
    colorFirstQuad = averageColor(arr1, avgColorDelta)
    colorSecondQaud = averageColor(arr2, avgColorDelta)

    return (borders, maskCase, (colorFirstQuad, colorSecondQaud))


# takes an image and returns the arrays corresponding to the quadrants
def getQuadrants(border,image):
    img = Image.open(image)
    arr1 = np.array(img.crop(flattenBorder(border[0])))
    arr2 = np.array(img.crop(flattenBorder(border[1])))
    return (arr1, arr2)

# Euclidian distance between vector c1 and c2
def distance(c1, c2):
    return np.linalg.norm(c1 - c2) 

# returns true if the colors passed (c1, and c2) correspon to the 
# starting screen colors 
def isSameScreen(c1, c2, colorFirstQuad, colorSecondQaud):
    delta = 5 # Note from expermiment, same screen seems to the order of 2, while different around 60
    return distance(c1, colorFirstQuad) < delta and distance(c2, colorSecondQaud) < delta


# Finds the index after which the last starting screen appears.
def findEndOfStartingSequence(images, borders, colorFirstQuad, colorSecondQaud):

    endOfStartingSequenceReached = False
    
    itr = 1 # 1 since we have extraced the starting sequence already

    while not endOfStartingSequenceReached:
        
        (arr1, arr2) = getQuadrants(borders, images[itr])
        c1 = averageColor(arr1, avgColorDelta)
        c2 = averageColor(arr2, avgColorDelta)

        if (not isSameScreen(c1, c2, colorFirstQuad, colorSecondQaud)):
            endOfStartingSequenceReached = True
            return itr

        itr = itr + 1

    return itr

# Returns index of the last message, s.t. images[:endOfMessage] is the message
# Index is the location of the last image
def findEndOfMessage(images, borders):

    endOfMessageReached = False

    index = len(images) - 1

    (arr1, arr2) = getQuadrants(borders, images[index])
    colorFirstQuad = averageColor(arr1, avgColorDelta)
    colorSecondQaud = averageColor(arr2, avgColorDelta)
    
    while not endOfMessageReached:
        
        index = index - 1

        (arr1, arr2) = getQuadrants(borders, images[index])
        c1 = averageColor(arr1, avgColorDelta)
        c2 = averageColor(arr2, avgColorDelta)

        if (not isSameScreen(c1, c2, colorFirstQuad, colorSecondQaud)):
            endOfStartingSequenceReached = True
            return index

        
    return index

# Returns index of the last message, s.t. images[:endOfMessage] is the message
# Index is the location of the last image
def findEnd(quadColorSequenceList, endScreenColor):

    endOfMessageReached = False

    index = len(quadColorSequenceList) - 1
    
    while not endOfMessageReached:

        if quadColorSequenceList[index] != -1:
        
            quadrantColor = sum(quadColorSequenceList[index]) / len(quadColorSequenceList[index])

            if (not isSameScreen(quadrantColor, 0, endScreenColor, 0)):
                endOfStartingSequenceReached = True
                return index

            index = index - 1
            
    return index

# returns the border, maskCase as well as the image list of
# Alphabet + padding value + Message
# Need to discard green part if it is in same screen as useful quad.
def getBordersMaskImagesAndStartingQuad(images):

    (borders, maskCase, quadColors) = extractStartingScreen(images)

    # Get starting quadrant color (which is the same as the ending one)
    startingQaudrant = quadColors[0]
    
    endOfStartingSequence = findEndOfStartingSequence(images, borders, startingQaudrant, startingQaudrant)

    #endOfMessage = findEndOfMessage(images, borders)
    #images = images[endOfStartingSequence:endOfMessage + 1]

    images = images[endOfStartingSequence:]
    images = images[timingInterpolationStart::timingInterpolationJump]

    return(borders, maskCase, images, startingQaudrant)

# transforms a sequence of images into the corresponding quadrant array list
# still needs to be sorted vis a vis message sequence 
def getQuadrantArrayList(images, borders):

    quadrantArrays = []
    
    for image in images:
        (arr1, arr2) = getQuadrants(borders, image)
        quadrantArrays.append(arr1)
        quadrantArrays.append(arr2)
    
    return quadrantArrays

# returns the a list where each element is a sequence of vectors of colors
# corresponding to the quadrant in the screen quadrant space.
def getQuadColorSequenceList(images, borders):

    quadColorSequenceList = []
    bordersOfSubQuadrant = getBordersOfSubQuadrant(borders, v_part, h_part)
    
    for image in images:
        img = Image.open(image)
        arr = np.array(img)
        
        firstQuadColorSequence = []
        for (top, bottom) in bordersOfSubQuadrant[0]:
    
            mean_tone = averageColor(arr, avgColorDelta, (top, bottom))
            firstQuadColorSequence.append(mean_tone)


        secondQuadColorSequence = []
        for (top, bottom) in bordersOfSubQuadrant[1]:

            mean_tone = averageColor(arr, avgColorDelta, (top, bottom))
            secondQuadColorSequence.append(mean_tone)

        quadColorSequenceList.append(firstQuadColorSequence)
        quadColorSequenceList.append(secondQuadColorSequence)

    return quadColorSequenceList


def decodeImage(images, alphabetLength):

    (borders, maskCase, images, startingQaudrant) = getBordersMaskImagesAndStartingQuad(images)

    # excluding starting sequence
    quadColorSequenceList = getQuadColorSequenceList(images, borders)

    # Sort  quadColorSequenceList in function of maskCase
    # Note that quadColorSequenceList[0] should contain the quadrant
    # which includes the starting alphabet.

    sortedQuadColorSequenceList = sortQuadrants(quadColorSequenceList, maskCase)

    endIndex = findEnd(quadColorSequenceList, startingQaudrant)

    sortedQuadColorSequenceList = sortedQuadColorSequenceList[:endIndex + 1]

    colorSequence = flatten(sortedQuadColorSequenceList)

    # partition the sequence
    alphabet = colorSequence[:alphabetLength]

    colorSequence = colorSequence[alphabetLength:endIndex]

    letterSequence = colorSequenceToLetterSequence(colorSequence, alphabet)

    padding = base_change(letterSequence[:paddingSize], alphabetLength, 10)

    message = letterSequence[paddingSize]

    return message



# # # CODE FOR TESTING

def testCrop(file_name, borders, num=0):

    img = Image.open(file_name)
    source_img = img.convert("RGBA")
    draw = ImageDraw.Draw(source_img)

    for (top, bottom) in borders:
        draw.rectangle((top, bottom), fill="white")

    source_img.save('cropTest' + str(num) + '.png', "PNG")

def partitionTest(file_name, borders, num =0):
    img = Image.open(file_name)
    source_img = img.convert("RGBA")
    draw = ImageDraw.Draw(source_img)

    bordersOfSubQuadrant = getBordersOfSubQuadrant(borders, v_part, h_part)
    itr = 0
    for (top, bottom) in bordersOfSubQuadrant[1]:

        if itr % 2 == 0:
            draw.rectangle((top, bottom), fill="white")
        else:
            draw.rectangle((top, bottom), fill="red")
        itr = itr + 1
    source_img.save('partitionTest' + str(num) + '.png', "PNG")




# Once we have the mask and the beginning of the alphabet, get the proper sequence indexing based
# on actualt order. Go through it to extract the alphabet, and message
  

# Get borders, mask and images

(borders, maskCase, images, startingQaudrant) = getBordersMaskImagesAndStartingQuad(images)


# # # Check sequencing/RGB values test

#quadColorSequenceList = getQuadColorSequenceList(images, borders)
#
#alphabet = getAlphabet(quadColorSequenceList[1][:8])
#
#print(' - -  ')
#
#Q = estimateLettersFromQuadrantColorList(quadColorSequenceList, alphabet)
#q1 = Q[0]
#q2 = Q[1]
#
#
#print(' q1 -  ')
#for q in range(len(q1)):
#    print(q1[q])
#
#print(' q2 -  ')
#print(' - -  ')
#for q in range(len(q2)):
#    print(q2[q])




# # # Crop and Partition Tests

testCrop(images[0], borders, 1)
partitionTest(images[0], borders, 1)


