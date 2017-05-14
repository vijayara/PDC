from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import math
import numpy as np



# get_color_positions returns a list of pairs, where each pair corresponds to the 
# coordinate of a one of the main colors (A, B, C, D). (They are returned
# in this order). Using get_corner we can hence find the edges needed for
# croping the subscreens A, B, C and D.
# 
    #####################   A, B, C, D correspond to the main screen areas
    ###   A   ##   B   ##   
    #####################  
    ###   D   ##   C   ##   
    #####################
#
# Note that testing is needed to find good thresholds that gaurantee that we
# our color positions are indeed the subscreens.
def get_color_positions(arr, dim):

    threshA = np.array([170, 170, 253]) # Blue
    threshB = np.array([120, 160, 120]) # Green
    threshC = np.array([180, 120, 120]) # Red 
    threshD = np.array([200, 200, 120]) # Yellow

    def isA(color):
        return color[0] < threshA[0] and color[1] < threshA[1] and color[2] > threshA[2]

    def isB(color):
        return color[0] < threshB[0] and color[1] > threshB[1] and color[2] < threshB[2]

    def isC(color):
        return color[0] > threshC[0] and color[1] < threshC[1] and color[2] < threshC[2]

    def isD(color):
        return color[0] > threshD[0] and color[1] > threshD[1] and color[2] < threshD[2]


    locA, locB, locC, locD = (-1, -1), (-1, -1), (-1, -1), (-1, -1)

    foundA, foundB, foundC, foundD = False, False, False, False
    nbrCornersFound = 0

    for i in range(dim[0]):
        for j in range(dim[1]):

            if (not foundA) and isA(arr[i][j]):
                locA = (i, j)
                foundA = True
                nbrCornersFound+=1

            elif (not foundB) and isB(arr[i][j]):
                locB = (i, j)
                foundB = True
                nbrCornersFound+=1
            
            elif ((not foundC) and isC(arr[i][j])):
                locC = (i, j)
                foundC = True
                nbrCornersFound+=1

            elif ((not foundD) and isD(arr[i][j])):
                locD = (i, j)
                foundD = True
                nbrCornersFound+=1

            #if (nbrCornersFound >= 2):
            #    return [locA, locB, locC, locD]

    return [locA, locB, locC, locD]

# is_edge detects whether c2 is in the edge, current implementation is quite
# simple and dosen't look at the previous neighbour (i.e. c1).
def is_edge(c1, c2, color):

    threshA = 170#np.array([170, 170, 170]) # Blue
    threshB = 170#np.array([120, 160, 120]) # Green
    threshC = 170#np.array([180, 120, 120]) # Red 
    threshD = 200#np.array([200, 200, 120]) # Yellow

    if (color == 'A'):
        return c2[2] < threshA
    elif (color == 'B'):
        return c2[1] < threshB
    elif (color == 'C'):
        return c2[0] < threshC
    elif (color == 'D'):
        return c2[0] < threshD or c2[1] < threshD
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
    colors = ['A', 'B', 'C', 'D']
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

    for v in range(vertical_partitions):
        for h in range(horizontal_partitions):

            i = top[0] + h * h_step
            j = top[1] + v * v_step
            partitions.append(((i,j), (i + h_step, j + v_step)))
    
    return partitions

# get_unit_crop_coordinates returns a list where each element
# contains a list with the coordinates needed to crop the unites.
def get_unit_crop_coorinates(arr, dim, v_part, h_part):

    borders = get_borders(arr, dim)
    unit_crop_coord = []
    for border in borders:
        unit_crop_coord.append(parition(border, v_part, h_part))

    return unit_crop_coord
