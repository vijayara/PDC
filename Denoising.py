# PDC Project
# Authors: Thierry B., Niroshan V., Ignacio A.
# From a quadran image retrieve the bit color representation array.

# input : a sequence of image with noise. parameter from the initial color tons. 
# output: an array with values that represent the closest color ton.

#  Two parts:
# 	- 	from an initial sequence, produce a way to match
#	-	from the formed mapping, mapp the next comming images.



import math
import random
from bitstring import BitArray
import zlib
import pygame
from pygame.locals import *
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import numpy as np

directory_name = "/Users/Niro/Documents/EPFL/Ecole/Semestre 6/Principles of Digital communication/Projet/PDC/Captures/"
file_name = directory_name + "testCol.jpg"
img = Image.open(file_name)

# greedy crop
img = img.crop((1280//3, 720//3, (2*1280)//3, (2*720)//3))

arr = np.array(img)
dim = arr.shape;

print("succes")


def encode(string):
    #encode the text in bytes
    in_bytes = string.encode("utf-8")
    #compress the bytes
    compressed = zlib.compress(in_bytes, 9)
    return compressed

def decode(compressed):
    #decompress the bytes
    in_bytes = zlib.decompress(compressed)
    #decode the text in bytes
    string = in_bytes.decode("utf-8")
    return string

def color_creation(n_tons):
    #select the different values
    ton = [(i)*255/(n_tons-1) for i in range(n_tons)]
    
    # fill the color array
    colors = []
    for i in range(n_tons):
        for j in range(n_tons):
            for k in range (n_tons):
                color = ((ton[i], ton[j], ton[k]))
                colors.append(color)
    return colors

def base_change(in_array, in_base, out_base):
    starting_zeros = 0
    num = 0
    power = len(in_array)-1
    while in_array[0] == 0:
        in_array = in_array[1:]
        starting_zeros += 1
        power -= 1
    while power >= 0:
        adding = in_array[0]*(in_base**power)
        num += adding
        power -= 1
        in_array = in_array[1:]
    
    new_num_array = []
    current = num
    while current!=0:
        remainder=current%out_base
        new_num_array = [remainder] + new_num_array
        current = current // out_base
    return ([0]*starting_zeros) + new_num_array

def text_to_colors(text, n_tons):
    n_colors = n_tons**3
    
    #encode the text with compression
    encoded = encode(text)
    #takes the bits of the message
    bits = BitArray(encoded).bin
    #makes the bits as an array
    bits_array = list(map(int, bits))    
    #change the input bits in our "colors-base"
    colors = base_change(bits_array, 2, n_colors)
    return colors

def colors_to_text(colors, n_tons):
    n_colors = n_tons**3
    
    bits_array = base_change(colors, n_colors, 2)    
    bit_string = ''.join(map(str, bits_array))
    bits = BitArray('0b' + bit_string)
    encoded = bits.tobytes()
    text = decode(encoded)
    return tex






