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


# turns a sequence of colors into estimated alphabet letters.
def estimateLettersFromQuadrantColors(quadColorSequence, alphabet):
    estimatesColorSquence = []

    for detected_color in quadColorSequence:
        estimatesColorSquence.append(closestColor(detected_color, alphabet))

    return estimatesColorSquence

# turns a list of quadrants into a list, where each element corresponds to a sequence
# of letters estimated from the corresponding quadrant.
def estimateLettersFromQuadrantColorList(quadColorSequenceList, alphabet):
    estimatesColorSquenceList = []

    for quadColorSequence in quadColorSequenceList:
        estimatesColorSquenceList.append(estimateLettersFromQuadrantColors(quadColorSequence, alphabet))

    return estimatesColorSquenceList


def colorSequenceToLetterSequence(colorSequence):
    letterSequence = []

    for detected_color in colorSequence:
        letterSequence.append(closestColor(detected_color, alphabet))

    return letterSequence


# Take a quadColorSequence corresponding to the alphabet
def getAlphabet(quadColorSequence):
    alphabet = []
    for color in quadColorSequence:
        alphabet.append(color)

    return alphabet

