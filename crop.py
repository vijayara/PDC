from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import numpy as np

file_name = "/Users/aleman/GDrive/EPFL/ba3/pdc/PDC/Captures/testCol.jpg"
img = Image.open(file_name)

output_name = "crop_output_test.jpg"

# greedy crop
img = img.crop((1280//3, 720//3, (2*1280)//3, (2*720)//3))

arr = np.array(img)
dim = arr.shape;



# getTopCorners returns a list of all the borders, where each border
# correspond to the top left and bottom right corners of the sub screens.
# 
    #####################   A, B, C, D correspond to the sub screens
    ###   A   ##   B   ##   which we can obtain by cropping the image
    #####################   by using the values in the borders.
    ###   D   ##   C   ##   
    #####################
def getTopCorners():

    threshA = np.array([120, 120, 200]) # Blue
    threshB = np.array([120, 160, 120]) # Green
    threshC = np.array([180, 120, 120]) # Red 
    threshD = np.array([200, 200, 120]) # Yellow

    def isA(a):
        return a[0] < threshA[0] and a[1] < threshA[1] and a[2] > threshA[2]

    def isB(a):
        return a[0] < threshB[0] and a[1] > threshB[1] and a[2] < threshB[2]

    def isC(a):
        return a[0] > threshC[0] and a[1] < threshC[1] and a[2] < threshC[2]

    def isD(a):
        return a[0] > threshD[0] and a[1] > threshD[1] and a[2] < threshD[2]


    borderA, borderB, borderC, borderD = [], [], [], []

    foundA, foundB, foundC, foundD = False, False, False, False
    nbrCornersFound = 0

    for i in range(dim[0]):
        for j in range(dim[1]):

            if (not foundA) and isA(arr[i][j]):
                borderA.append((j, i))
                foundA = True
                nbrCornersFound+=1

            elif (not foundB) and isB(arr[i][j]):
                borderB.append((j, i))
                foundB = True
                nbrCornersFound+=1
            
            elif ((not foundC) and isC(arr[i][j])):
                borderC.append((j, i))
                foundC = True
                nbrCornersFound+=1

            elif ((not foundD) and isD(arr[i][j])):
                borderD.append((j, i))
                foundD = True
                nbrCornersFound+=1

            #if (nbrCornersFound >= 2):
            #    return (borderA, borderB, borderC, borderD)


    foundA, foundB, foundC, foundD = False, False, False, False
    nbrCornersFound = 0

    for i in reversed(range(dim[0])):
        for j in reversed(range(dim[1])):

            if (not foundA) and isA(arr[i][j]):
                borderA.append((j, i))
                foundA = True
                nbrCornersFound+=1

            elif (not foundB) and isB(arr[i][j]):
                borderB.append((j, i))
                foundB = True
                nbrCornersFound+=1
            
            elif ((not foundC) and isC(arr[i][j])):
                borderC.append((j, i))
                foundC = True
                nbrCornersFound+=1

            elif ((not foundD) and isD(arr[i][j])):
                borderD.append((j, i))
                foundD = True
                nbrCornersFound+=1

            #if (nbrCornersFound >= 2):
            #    return (borderA, borderB, borderC, borderD)

    return [borderA, borderB, borderC, borderD]


borders = getTopCorners()

source_img = img.convert("RGBA")
draw = ImageDraw.Draw(source_img)


for ba in borders:
    draw.rectangle((ba[0], ba[1]), fill="red")
    

source_img.save(output_name, "JPEG")
