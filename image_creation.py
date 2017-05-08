# PDC Project
# Authors: Thierry B., Niroshan V., Ignacio A.

import math
import random
from bitstring import BitArray
import zlib
import pygame
from pygame.locals import *

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
    return text
    
def display(text, rows=3, columns=5, n_tons=2, cross_size=30):
    pygame.init()
    pygame.mouse.set_visible(False)

    # total screen size
    SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)

    # separating cross width
    CROSS_SIZE = cross_size
    QUADRANT_SIZE = ((SIZE[0]-CROSS_SIZE)/2, (SIZE[1]-CROSS_SIZE)/2)
    # quadrant offsets
    W_OFFSET = QUADRANT_SIZE[0] + CROSS_SIZE
    H_OFFSET = QUADRANT_SIZE[1] + CROSS_SIZE
    QUADRANT_OFFSETS = [(0, 0), (W_OFFSET, 0), (0, H_OFFSET), (W_OFFSET, H_OFFSET)]
    
    # number of tiles per quadrant
    N_TILES = rows*columns
    TILE_SIZE = (QUADRANT_SIZE[0]//columns, QUADRANT_SIZE[1]//rows)
    TILE_OFFSETS = []
    for r in range(rows):
        for c in range(columns):
            TILE_OFFSETS.append((c*TILE_SIZE[0], r*TILE_SIZE[1]))

    # number of possible levels for each color
    N_TONS = n_tons
    # number of colors
    N_COLORS = N_TONS**3

    # fill the color array
    COLOR = color_creation(N_TONS)

    # select indexes of the 4 most distanced colors (red, green, blue, white)
    MOST_DISTANCES = []
    for i in range(3):
        MOST_DISTANCES.append((N_TONS**i)*(N_TONS-1))
    MOST_DISTANCES.append(N_COLORS-1)
    
    color_message = text_to_colors(text, N_TONS)
    
    #number of colors not used at the end of the message
    n_colors_last_quadrant = len(color_message) % N_TILES
    remaining_colors = (N_TILES - n_colors_last_quadrant) if n_colors_last_quadrant else 0
    #number of quadrants needed for the message
    n_quadrants = len(color_message) // N_TILES + (remaining_colors != 0)
    
    #fill a color matrix where each row is a quadrant
    quadrants_colors = [color_message[N_TILES*y:N_TILES*(y+1)] for y in range(n_quadrants)]
    
    print("-> Verification text (reverse):\n", colors_to_text(color_message, N_TONS))
    print("-> Number of quadrants:", n_quadrants)
    print("-> Remaining colors:", remaining_colors)
    print("-> Colors of the message:\n", quadrants_colors)
    
    # create particular quadrants : 4 starting quadrants (red, green, blue, white) plus the black one
    particular_quadrants = [pygame.surface.Surface(QUADRANT_SIZE) for i in range(5)]
    for i in range(4):
        particular_quadrants[i].fill(COLOR[MOST_DISTANCES[i]])
    particular_quadrants[4].fill(COLOR[0])

    
    # create every quadrants for the message
    quadrants = [pygame.surface.Surface(QUADRANT_SIZE) for i in range(n_quadrants)]
    for q in range(len(quadrants)):
        for c in range(len(quadrants_colors[q])):
            color = COLOR[quadrants_colors[q][c]]
            rect = pygame.Rect(TILE_OFFSETS[c], TILE_SIZE)
            quadrants[q].fill(color, rect)
    
    # set the display to the entire screen
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)#, max(math.ceil(math.log(7**3, 2)), 8))
    for i in range(4):
        display.blit(particular_quadrants[i], QUADRANT_OFFSETS[i])


    # run with the following scheme:
    
    ###############################
    ##### 1 ###### 2 ###### 3 #####
    ###       ##       ##       ###
    ###  D A  ##  B D  ##  C C  ###
    ###  A A  ##  B B  ##  D C  ###
    ###       ##       ##       ###
    ###############################
    ###############################
    
    run = True
    current_quadrant = 0
    pygame.display.flip()
    while run:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_s:
                if(current_quadrant >= n_quadrants):
                    run = False
                    break
                config = current_quadrant%4
                if config == 0:
                    for i in (1,2,3):
                        display.blit(quadrants[current_quadrant], QUADRANT_OFFSETS[i])
                    if(current_quadrant+3 < n_quadrants):
                        display.blit(quadrants[current_quadrant+3], QUADRANT_OFFSETS[0])
                    else:
                        #fill in black if nothin to display
                        display.blit(particular_quadrants[4], QUADRANT_OFFSETS[0])
                elif config == 1:
                    for i in (0,2,3):
                        display.blit(quadrants[current_quadrant], QUADRANT_OFFSETS[i])
                    if(current_quadrant+2 < n_quadrants):
                        display.blit(quadrants[current_quadrant+2], QUADRANT_OFFSETS[1])
                    else:
                        #fill in black if nothin to display
                        display.blit(particular_quadrants[4], QUADRANT_OFFSETS[1])
                elif config == 2:
                    for i in (0,1,3):
                        display.blit(quadrants[current_quadrant], QUADRANT_OFFSETS[i])
                    if(current_quadrant+1 < n_quadrants):
                        display.blit(quadrants[current_quadrant+1], QUADRANT_OFFSETS[2])
                    else:
                        #fill in black if nothin to display
                        display.blit(particular_quadrants[4], QUADRANT_OFFSETS[2])
                    # at config 2, one more increment to skip the D
                    current_quadrant += 1
                else:
                    print("ERROR: didn't skip a fourth screen of cycle")
                  
                pygame.display.flip()
                current_quadrant += 1
            if event.type == KEYDOWN and event.key == K_q:
                run = False

    pygame.quit()
    return

text200 = """In the midst of the Great Desert lived two tribes of people.
Both were nomadic in nature and continuously traveled across the arid landscape,
from oasis to oasis. Although each tribe considered themselves..."""
text1000 = """In the midst of the Great Desert lived two tribes of people.
Both were nomadic in nature and continuously traveled across the arid landscape,
from oasis to oasis. Although each tribe considered themselves nomads, it was in 
truth not by choice. For you see, each oasis was very fragile because the waters 
in each were limited. Thus, instead of living at an oasis until it ran dry, thus 
destroying it as a place of shelter for the future, in their wisdom they would move on.
Yet, it was forever the quest of each tribe to find an oasis that could sustain them 
over many years, without the threat that the waters would run dry.
Then one day the tribe that claimed to be the oldest, the first, came upon an oasis
 large enough to hold a thousand tribes, full of tall fruit-bearing trees, where 
 colored birds sang sweetly in their boughs, and beasts lay quietly in their shade.
And there in the middle flowed a deep spring of crystalline waters.
When the sultan of the tribe beheld this jewel of the..."""

#(text, rows=3, columns=5, n_tons=2, cross_size=30)
display(text200, 3, 5, 3)
