from crop import*
from image_decoding import*
from tools import *
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
n_tones = 2
alphabetLength = 8
paddingSize = 2

avgColorDelta = 3
v_part, h_part = 3, 5
quadSize = v_part * h_part

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

# retuns true if every element of quadColorSequenceList is green
def isAllGreen(quadColorSequenceList, alphabet, green_code=2):

    for color in quadColorSequenceList:
        if (closestColor(color, alphabet) != green_code):
            return False

    return True


# Returns index of the last message in reverse
def findEnd(quadColorSequenceList, alphabet):

    endOfMessageReached = False

    endIndex = len(quadColorSequenceList) - 1

    index = 0
    
    # find other way to loop
    while not endOfMessageReached:

        if quadColorSequenceList[endIndex - index] != -1:
        
#            quadrantColor = sum(quadColorSequenceList[index]) / len(quadColorSequenceList[index])
#
#            if (not isSameScreen(quadrantColor, 0, endScreenColor, 0)):
#                endOfStartingSequenceReached = True
#                return index

            if not isAllGreen(quadColorSequenceList[endIndex - index], alphabet):
                return index

            index = index + 1

    return index

# returns the border, maskCase as well as the image list of
# Alphabet + padding value + Message
# Need to discard green part if it is in same screen as useful quad.
def getBordersMaskImages(images):

    (borders, maskCase, quadColors) = extractStartingScreen(images)

    endOfStartingSequence = findEndOfStartingSequence(images, borders, quadColors[0], quadColors[1])

    #endOfMessage = findEndOfMessage(images, borders)
    #images = images[endOfStartingSequence:endOfMessage + 1]

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


# decodedImage takes an image list (file_names) and an alphabet length
# and returns the decoded message
def decodeImage(images, alphabetLength):

    # Get borders needed to extract visible quads, the mask type (maskCase)
    # and the images without the starting sequence. (i.e. the image set
    # where the first screen contains the alphabet)
    (borders, maskCase, images) = getBordersMaskImages(images)

    # transform the image set into a quadrant list. (i.e. for each image we
    # extract the 2 corresponding quadrants). Note that each quadrant is
    # a list of RGB vectors in sequence.
    quadColorSequenceList = getQuadColorSequenceList(images, borders)

    # We sort the quad list vis a vis the mask type
    sortedQuadColorSequenceList = sortQuadrants(quadColorSequenceList, maskCase)

    # We flatten the quad list into a color sequence
    colorSequence = flatten(sortedQuadColorSequenceList)

    # get the alphabet
    alphabet = colorSequence[:alphabetLength]

    # find the index, starting from the end at which the ending sequence starts
    indexFromEnd = findEnd(sortedQuadColorSequenceList, alphabet) 

    # remove alphabet and ending sequence
    colorSequence = colorSequence[alphabetLength:-indexFromEnd]

    # transform the color sequence to a letter sequence, were a letter resides
    # in n_tone alphabet
    letterSequence = colorSequenceToLetterSequence(colorSequence, alphabet)

    # get the padding length
    padding = base_change(letterSequence[:paddingSize], alphabetLength, 10)

    # turn array number into int value
    padding = int(''.join(map(str,padding)))

    # number of zeroes appended to the alphabet.
    # Is this general enough?
    n_zeros = abs(alphabetLength + paddingSize - quadSize)

    # remove the padding length, the padding at the end, and remember to remove
    # the zeroes appended to the alphabet
    codedMesage = letterSequence[paddingSize + n_zeros:-padding]

    # return decoded message
    return colors_to_text(codedMesage, n_tones)
     


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
  
# # # decoded message

decodedMesage = decodeImage(images, alphabetLength)

print(decodedMesage)



# # # Crop and Partition Tests

#testCrop(images[0], borders, 1)
#partitionTest(images[0], borders, 1)


