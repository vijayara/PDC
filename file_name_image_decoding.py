from PIL import Image
from crop import*
from tools import*
import numpy as np

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
n_tones = 2

n_colors = n_tones**3
alphabetLength = n_colors
paddingSize = 2

green_index = 2

avgColorDelta = 2

# If we have 4 samples of each image, and we want to take each third one:
timingInterpolationStart = 2
timingInterpolationJump = 4

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


def colorSequenceToLetterSequence(colorSequence, alphabet):
    letterSequence = []

    for detected_color in colorSequence:
        letterSequence.append(closestColor(detected_color, alphabet))

    return letterSequence

def sortQuadrants(quadrantList, mask):
    sortedList = []
    size = len(quadrantList)

    if not mask:
        rest = size%12
        padding = (rest!=0)*(12-rest)
        size += padding
        
        toKeep = [1, 4, 8, 11]
        indices = [i for i in range(size) if i%12 in toKeep]
    elif mask == maskUp or mask == maskLeft:
        rest = size%6
        padding = (rest!=0)*(6-rest)
        size += padding
        
        toKeep = [0, 3, 4, 5]
        indices = [i for i in range(size) if i%6 in toKeep]
    elif mask == maskDown or mask == maskRight or mask == maskDownUp:
        rest = size%6
        padding = (rest!=0)*(6-rest)
        size += padding
        
        toKeep = [0, 1, 2, 4]
        indices = [i for i in range(size) if i%6 in toKeep]
        indices[::4], indices[1::4], indices[2::4], indices[3::4] = indices[1::4], indices[2::4], indices[3::4], indices[::4]
    elif mask == maskUpDown:
        rest = size%6
        padding = (rest!=0)*(6-rest)
        size += padding
        
        toKeep = [0, 2, 3, 4]
        indices = [i for i in range(size) if i%6 in toKeep]
        indices[::4], indices[1::4], indices[2::4], indices[3::4] = indices[::4], indices[2::4], indices[3::4], indices[1::4]
    
    quadrantList += [quadrantList[-1]]*padding
    sortedQuadrantList = [quadrantList[i] for i in indices]
    return sortedQuadrantList


# turn border into right format for .crop method
def flattenBorder(border):
    (top, bottom) = border
    return (top[0], top[1], bottom[0], bottom[1])

# Get mask returns the mask type based on the location list (see crop)
def getMaskFromInfo(maskInfo):

    (i1, i2) = maskInfo
    if i1 == 2 and i2 == 3:
        return maskUp
    elif i1 == 0 and i2 == 1:
        return maskDown
    elif i1 == 1 and i2 == 3:
        return maskLeft
    elif i1 == 0 and i2 == 2:
        return maskRight
    elif i1 == 1 and i2 == 2:
        return maskUpDown
    elif i1 == 0 and i2 == 3:
        return maskDownUp
    else:
        return noMask

# returns the mask type as well as the corners associated.
def extractStartingScreen(images):

    img = Image.open(images[0])
    arr = np.array(img)
    dim = arr.shape

    (borders, maskInfo) = get_borders(arr, dim)

    maskCase = getMaskFromInfo(maskInfo)

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

# returns true if the colors passed (c1, and c2) correspon to the 
# starting screen colors 
def isSameScreen(c1, c2, colorFirstQuad, colorSecondQaud):
    delta = 20 # Note from expermiment, same screen seems to the order of 2, while different around 60
    print(distance(c1, colorFirstQuad))
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

# finds the index at which the ending sequence starts
def findEndingIndex(colorSequence, quadSize):
    
    blocks = len(colorSequence) // quadSize # this should always be an int

    for b in range(blocks):
        if all (green_index == color for color in colorSequence[b*quadSize: (b + 1)*quadSize]):
            return b*quadSize

    return -1

# returns the border, maskCase as well as the image list of
# Alphabet + padding value + Message
# Need to discard green part if it is in same screen as useful quad.
def getBordersMaskImages(images):

    (borders, maskCase, quadColors) = extractStartingScreen(images)

    endOfStartingSequence = findEndOfStartingSequence(images, borders, quadColors[0], quadColors[1])

    images = images[endOfStartingSequence:]
    images = images[timingInterpolationStart::timingInterpolationJump]

    return(borders, maskCase, images)

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
def getQuadColorSequenceList(images, borders, v_part, h_part):

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


# decodedImage takes an image list (file_names) and an alphabet length
# and returns the decoded message
def decodeImage(images, alphabetLength, coding, v_part, h_part):
    quadSize = v_part * h_part

    # Get borders needed to extract visible quads, the mask type (maskCase)
    # and the images without the starting sequence. (i.e. the image set
    # where the first screen contains the alphabet)
    (borders, maskCase, images) = getBordersMaskImages(images)

    # transform the image set into a quadrant list. (i.e. for each image we
    # extract the 2 corresponding quadrants). Note that each quadrant is
    # a list of RGB vectors in sequence.
    quadColorSequenceList = getQuadColorSequenceList(images, borders, v_part, h_part)

    # We sort the quad list vis a vis the mask type
    sortedQuadColorSequenceList = sortQuadrants(quadColorSequenceList, maskCase)
    print("MASKCASE",maskCase)

    print(images)

    # We flatten the quad list into a color sequence
    colorSequence = flatten(sortedQuadColorSequenceList)
    
    # get the alphabet
    alphabet = colorSequence[:alphabetLength]

    # remove alphabet from sequence
    colorSequence = colorSequence[alphabetLength:]
    
    # transform the color sequence to a letter sequence, were a letter resides
    # in n_tone alphabet
    letterSequence = colorSequenceToLetterSequence(colorSequence, alphabet)

    # get the padding length
    padding = base_change(letterSequence[:paddingSize], alphabetLength, 10)

    # turn array number into int value
    padding = arrayToNumber(padding)

    # number of zeroes appended to the alphabet.
    n_zeros = quadSize - ((alphabetLength + paddingSize) % quadSize)

    letterSequence = letterSequence[paddingSize + n_zeros:]

    # remove ending sequence (find first green quad)
    endingIndex = findEndingIndex(letterSequence, quadSize)

    # remove ending screen (green)
    letterSequence = letterSequence[:endingIndex]

    # remove padding sequence at the end (black)
    codedMessage = letterSequence[:-padding]
    #print(codedMessage)

    # return decoded message
    return colors_to_text(codedMessage, n_tones, coding)
