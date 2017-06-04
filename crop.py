from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from tools import*
import math
import numpy as np

idealRatio = 1280 / 720

emptyQuad = (-1, -1)

# Dark room with lights
#threshQ1 = np.array([50, 150, 230]) # Blue
#threshQ2 = np.array([100, 180, 140]) # Green
#threshQ3 = np.array([170, 50, 40]) # Red 
#threshQ4 = np.array([155, 175, 120]) # Yellow

# HighLum
threshQ1 = np.array([65, 150, 230]) # Blue
threshQ2 = np.array([100, 200, 140]) # Green
threshQ3 = np.array([190, 50, 40]) # Red 
threshQ4 = np.array([200, 200, 110]) # Yellow

#threshQ1 = np.array([50, 150, 230]) # Blue
#threshQ2 = np.array([80, 180, 110]) # Green
#threshQ3 = np.array([170, 50, 40]) # Red 
#threshQ4 = np.array([155, 175, 120]) # Yellow

def isQ1(color):
    return color[0] < threshQ1[0] and color[1] < threshQ1[1] and color[2] > threshQ1[2]

def isQ2(color):
    return color[0] < threshQ2[0] and color[1] > threshQ2[1] and color[2] < threshQ2[2]

def isQ3(color):
    return color[0] > threshQ3[0] and color[1] < threshQ3[1] and color[2] < threshQ3[2]

def isQ4(color):
    return color[0] > threshQ4[0] and color[1] > threshQ4[1] and color[2] < threshQ4[2]

# get_color_positions returns a list of pairs, where each pair corresponds to the 
# coordinate of a one of the main colors (Q1, Q2, Q3, Q4). (They are returned
# in this order). Using get_corner we can hence find the edges needed for
# croping the subscreens Q1, Q2, Q3 and Q4.
# 
    #####################   Q1, Q2, Q3, Q4 correspond to the main screen areas
    ###  Q1   ##  Q2   ##   
    #####################  
    ###  Q4   ##  Q3   ##   
    #####################
#
# Note that testing is needed to find good thresholds that gaurantee that we
# our color positions are indeed the subscreens.
def get_color_positions(arr, dim):
    jump = 5
    locQ1, locQ2, locQ3, locQ4 = emptyQuad, emptyQuad, emptyQuad, emptyQuad

    foundQ1, foundQ2, foundQ3, foundQ4 = False, False, False, False

    colorQ1, colorQ2, colorQ3, colorQ4 = 0, 0, 0, 0
    nbrCornersFound = 0

    for i in range(dim[0]):
        for j in range(dim[1]):

            if (not foundQ1) and isQ1(arr[i][j]):
                locQ1 = (i+jump, j)
                colorQ1 = arr[i+jump][j]
                foundQ1 = True
                nbrCornersFound+=1

            elif (not foundQ2) and isQ2(arr[i][j]):
                locQ2 = (i+jump, j)
                colorQ2 = arr[i+jump][j]
                foundQ2 = True
                nbrCornersFound+=1
            
            elif ((not foundQ3) and isQ3(arr[i][j])):
                locQ3 = (i+jump, j)
                colorQ3 = arr[i+jump][j]
                foundQ3 = True
                nbrCornersFound+=1

            elif ((not foundQ4) and isQ4(arr[i][j])):
                locQ4 = (i+jump, j)
                colorQ4 = arr[i+jump][j]
                foundQ4 = True
                nbrCornersFound+=1

    return [[locQ1, locQ2, locQ3, locQ4], [colorQ1, colorQ2, colorQ3, colorQ4]]


def is_edge(color, quadrant, color_source):

    #HighLum
    threshQ1 = color_source[2]-40
    threshQ2 = color_source[1]-25
    threshQ3 = color_source[0]-50
    threshQ4 = int(color_source[0])+int(color_source[1])-60

    #threshQ1 = color_source[2]-40
    #threshQ2 = color_source[1]-15
    #threshQ3 = color_source[0]-25
    #threshQ4 = int(color_source[0])+int(color_source[1])-40#28

    if (quadrant == 'Q1'):
        return color[2] < threshQ1
    elif (quadrant == 'Q2'):
        return color[1] < threshQ2
    elif (quadrant == 'Q3'):
        return color[0] < threshQ3
    elif (quadrant == 'Q4'):
        return int(color[0])+int(color[1]) < threshQ4
    else:
        return False


# get_corner returns the top left corner when way = -1 and
# the bottom right corner when way = 1.
# It does so by getting a coordinate (i, j) which is inside
# a box of color. to find the appropriate corners it goes
# either exploring to the top left, or bottom right accordingly.
# note that it returns (j, i) since using the image.crop function
# uses this same structure.
def get_corner(arr, i, j, way, color, colorQ):
    height = np.shape(arr)[0]
    width = np.shape(arr)[1]

    newI, newJ = i, j

    found, itr = False, 0
    while (not found and newI > 0 and newI < height-1):
        newI += way
        if (is_edge(arr[newI][j], color, colorQ)):
            found = True

    found, itr = False, 0
    while (not found and newJ > 0 and newJ < width-1):
        newJ += way
        if (is_edge(arr[i][newJ], color, colorQ)):
            found = True

    return (newJ, newI)

# get_borders returns all the pairs (top, bottom) for all the colors that it
# can find, where top and bottom are the respective top left and bottom right
# corners which can be used to crop said color screen partitions.
def getAllBorders(arr, dim):
    colors = ['Q1', 'Q2', 'Q3', 'Q4']
    locations = get_color_positions(arr, dim) 

    borders = []
    for itr in range(len(colors)):
        (i, j) = locations[0][itr]
        colorQ = locations[1][itr]
        color = colors[itr]
        if ((i, j) != emptyQuad): 
            borders.append((get_corner(arr, i, j, -1, color, colorQ), get_corner(arr, i, j, 1, color, colorQ)))

    return borders


def getBestBorderPair(borders, quadIndex):

    index = 0
    ratios = []
    for (top, bottom) in borders:
        ratio = (bottom[0] - top[0]) / (bottom[1] - top[1])
        ratios.append(abs(ratio - idealRatio))
    
    borderChoices = [b for b in range(len(borders))]
    bestChoices = [x for (y,x) in sorted(zip(ratios,borderChoices))]
    chosenQuads = sorted((quadIndex[bestChoices[0]], quadIndex[bestChoices[1]]))

    if (quadIndex[bestChoices[0]] < quadIndex[bestChoices[1]]):
        return ([borders[bestChoices[0]], borders[bestChoices[1]]], chosenQuads)
    else:
        return ([borders[bestChoices[1]], borders[bestChoices[0]]], chosenQuads)



def get_borders(arr, dim):
    colors = ['Q1', 'Q2', 'Q3', 'Q4']
    locations = get_color_positions(arr, dim)
    chosenQuads = -1
    nb_quad = 4 - sum([emptyQuad == quad for quad in locations[0]])
    if nb_quad < 2:
        return []

    borders = []
    quadIndex = []
    for itr in range(len(colors)):
        (i, j) = locations[0][itr]
        colorQ = locations[1][itr]
        color = colors[itr]
        if ((i, j) != emptyQuad): 
            borders.append((get_corner(arr, i, j, -1, color, colorQ), get_corner(arr, i, j, 1, color, colorQ)))
            quadIndex.append(itr)


    (borders, chosenQuads) = getBestBorderPair(borders, quadIndex)

    return (borders, chosenQuads)


def partition(border, vertical_partitions=1, horizontal_partitions=1):
    partitions = []
    (top, bottom) = border
    height = bottom[0] - top[0]
    width = bottom[1] - top[1]

    j = top[1]
    for v in range(vertical_partitions):
        i = top[0]
        l = top[1] + int(round((v+1) * width / vertical_partitions))
        for h in range(horizontal_partitions):
            k = top[0] + int(round((h+1) * height / horizontal_partitions))
            partitions.append(((i, j), (k, l)))
            i = k
        j = l
    return partitions

# getBordersOfSubQuadrant returns a list where each element
# contains a list with the borders needed to crop the 
# partitions inside a quadrant
def getBordersOfSubQuadrant(borders, v_part, h_part):

    bordersOfSubQuadrant = []
    for border in borders:
        bordersOfSubQuadrant.append(partition(border, v_part, h_part))

    return bordersOfSubQuadrant
