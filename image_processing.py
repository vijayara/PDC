from crop import*
from image_decoding import*
from tools import *
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance


## # # CODE FOR TESTING
#
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
    for (top, bottom) in bordersOfSubQuadrant[0]:

        if itr % 2 == 0:
            draw.rectangle((top, bottom), fill="white")
        else:
            draw.rectangle((top, bottom), fill="red")
        itr = itr + 1
    source_img.save('partitionTest' + str(num) + '.png', "PNG")




  


# Images 

file_path = 'testsmay19/good1/pic'
extension = '.png'
start_seq = 21
end_seq = 119
images = []

for index in range(start_seq, end_seq + 1):
    filename = file_path + str(index) + extension

    images.append(file_path + str(index) + extension)
 





#decodedMesage = decodeImage(images, alphabetLength)
#print(decodedMesage)


# # # Crop and Partition Tests


#testFile = 'night_test/lum5.png'
testFile= images[0]

img = Image.open(testFile)
arr = np.array(img)
dim = arr.shape
#
borders = getAllBorders(arr, dim)

#
#
testCrop(testFile, borders, 1)
#partitionTest(images[0], borders, 1)


