from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import math
import numpy as np


#threshQ1 = np.array([170, 170, 253]) # Blue
#threshQ2 = np.array([120, 160, 120]) # Green
#threshQ3 = np.array([180, 120, 120]) # Red 
#threshQ4 = np.array([200, 200, 120]) # Yellow

threshQ1 = np.array([170, 170, 240]) # Blue
threshQ2 = np.array([120, 160, 120]) # Green
threshQ3 = np.array([180, 120, 120]) # Red 
threshQ4 = np.array([200, 200, 120]) # Yellow

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




    locQ1, locQ2, locQ3, locQ4 = (-1, -1), (-1, -1), (-1, -1), (-1, -1)

    foundQ1, foundQ2, foundQ3, foundQ4 = False, False, False, False
    nbrCornersFound = 0

    for i in range(dim[0]):
        for j in range(dim[1]):

            if (not foundQ1) and isQ1(arr[i][j]):
                locQ1 = (i, j)
                foundQ1 = True
                nbrCornersFound+=1

            elif (not foundQ2) and isQ2(arr[i][j]):
                locQ2 = (i, j)
                foundQ2 = True
                nbrCornersFound+=1
            
            elif ((not foundQ3) and isQ3(arr[i][j])):
                locQ3 = (i, j)
                foundQ3 = True
                nbrCornersFound+=1

            elif ((not foundQ4) and isQ4(arr[i][j])):
                locQ4 = (i, j)
                foundQ4 = True
                nbrCornersFound+=1

            #if (nbrCornersFound >= 2):
            #    return [locQ1, locQ2, locQ3, locQ4]
            #print(foundQ1, foundQ2)
    return [locQ1, locQ2, locQ3, locQ4]

# is_edge detects whether c2 is in the edge, current implementation is quite
# simple and dosen't look at the previous neighbour (i.e. c1).
def is_edge(c1, c2, color):

    threshQ1 = 170#np.array([170, 170, 170]) # Q2lue
    threshQ2 = 170#np.array([120, 160, 120]) # Green
    threshQ3 = 170#np.array([180, 120, 120]) # Red 
    threshQ4 = 200#np.array([200, 200, 120]) # Yellow

    if (color == 'Q1'):
        return c2[2] < threshQ1
    elif (color == 'Q2'):
        return c2[1] < threshQ2
    elif (color == 'Q3'):
        return c2[0] < threshQ3
    elif (color == 'Q4'):
        return c2[0] < threshQ4 or c2[1] < threshQ4
    else:
        return False

# get_corner returns the top left corner when way = -1 and
# the bottom right corner when way = 1.
# It does so by getting a coordinate (i, j) which is inside
# a box of color. to find the appropriate corners it goes
# either exploring to the top left, or bottom right accordingly.
# note that it returns (j, i) since using the image.crop function
# uses this same structure.
def get_corner(arr, i, j, way, color):   

    newI, newJ = i, j

    found, itr = False, 0
    while (not found and newI > 0):

        newI += way
        if (is_edge(arr[newI][j], arr[newI + way][j], color)):
            found = True
        if (newI < 0):
            return (0, 0)

    found, itr = False, 0
    while (not found and newJ > 0):

        newJ += way
        if (is_edge(arr[i][newJ], arr[i][newJ + way], color)):
            found = True
        if (newJ < 0):
            return (0, 0)


    return (newJ, newI)

# get_borders returns all the pairs (top, bottom) for all the colors that it
# can find, where top and bottom are the respective top left and bottom right
# corners which can be used to crop said color screen partitions.
def get_borders(arr, dim):
    colors = ['Q1', 'Q2', 'Q3', 'Q4']
    locations = get_color_positions(arr, dim) 
    borders = []
    for ((i, j), color) in zip(locations, colors):
        if ((i, j) != (-1, -1)): 
            borders.append((get_corner(arr, i, j, -1, color), get_corner(arr, i, j, 1, color)))

    return borders

# reverses a pair, (a, b) -> (b, a)
def reverse(pair):
    return tuple(reversed(pair))

# Paritions a screen into vertical_partitions * horizontal_partitions screens
# it returns the set of points needed for the the partitioning.
# note that everything is inverted vis a vis de .crop function. Hence width 
# and height are inverted in
def parition(border, vertical_partitions=1, horizontal_partitions=1):

    if vertical_partitions==1 and horizontal_partitions==1:
        return border

    partitions = []
    (top, bottom) = border
    height = bottom[0] - top[0]
    width = bottom[1] - top[1]

    h_step = math.floor(height / horizontal_partitions)
    v_step = math.floor(width / vertical_partitions)

#   residual_limit is the residual pixels if we go at the previously define steps
#   if the residual is to high, we should take larger steps. Note that this 
#   should depend on the partition size, so we should modify if we change n_tones.

    residual_limit = 2
    if (height - h_step * horizontal_partitions > residual_limit):
        h_step = h_step + 1

    if (width - v_step * vertical_partitions > residual_limit):
        v_step = v_step + 1

    for v in range(vertical_partitions):
        for h in range(horizontal_partitions):

            i = top[0] + h * h_step
            j = top[1] + v * v_step
            partitions.append(((i,j), (i + h_step, j + v_step)))
    
    return partitions

# Thierry version
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
            print(i, j, k, l)
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
