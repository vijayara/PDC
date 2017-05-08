import math
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

def text_to_colors(text, n_colors):
    #encode the text with compression
    encoded = encode(text)
    #takes the bits of the message
    bits = BitArray(encoded).bin
    #makes the bits as an array
    bits_array = list(map(int, bits))    
    #change the input bits in our "colors-base"
    colors = base_change(bits_array, 2, n_colors)
    return colors

def colors_to_text(colors, n_colors):
    bits_array = base_change(colors, n_colors, 2)    
    bit_string = ''.join(map(str, bits_array))
    bits = BitArray('0b' + bit_string)
    encoded = bits.tobytes()
    text = decode(encoded)
    return text
    
def display(text, cross_size=30, rows=3, columns=3, n_tons=2):
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
    TILE_SIZE = (QUADRANT_SIZE[0]/columns, QUADRANT_SIZE[1]/rows)
    TILE_OFFSETS = []
    for c in range(columns):
        for r in range(rows):
            TILE_OFFSETS.append((r*TILE_SIZE[0], c*TILE_SIZE[1]))

    # number of possible levels for each color
    N_TONS = n_tons
    TON = [(i)*255/(N_TONS-1) for i in range(N_TONS)]
    # number of colors
    N_COLORS = N_TONS**3

    # fill the color array
    COLOR = []
    for i in range(N_TONS):
        for j in range(N_TONS):
            for k in range (N_TONS):
                color = ((TON[i], TON[j], TON[k]))
                COLOR.append(color)

    # select indexes of 4 most distances colors (red, green, blue, white)
    MOST_DISTANCES = []
    for i in range (0, 3):
        MOST_DISTANCES.append((N_TONS**i)*(N_TONS-1))
    MOST_DISTANCES.append(N_COLORS-1)
    
    color_message = text_to_colors(text, N_COLORS)
    print("verification text (reverse):", colors_to_text(color_message, N_COLORS))
    
    #number of colors not used at the end of the message
    remaining_colors = N_TILES - (len(color_message) % N_TILES)
    #number of quadrants needed for the message
    n_quadrants = len(color_message) // N_TILES + (remaining_colors != 0)
    print("number of quadrants:", n_quadrants)
    
    #fill a color matrix where each row is a quadrant
    quadrants_colors = [color_message[N_TILES*y:N_TILES*(y+1)] for y in range(n_quadrants)]
    print(quadrants_colors)
    
    #create every quadrants for the message
    quadrants = [pygame.surface.Surface(QUADRANT_SIZE) for i in range(n_quadrants)]
    for q in range(len(quadrants)):
        for c in range(len(quadrants_colors[q])):
            color = COLOR[quadrants_colors[q][c]]
            rect = pygame.Rect(TILE_OFFSETS[c], TILE_SIZE)
            quadrants[q].fill(color, rect)
    
    # set the display to the entire screen
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)#, max(math.ceil(math.log(7**3, 2)), 8))
    
    for i in range(4):
        display.blit(quadrants[i], QUADRANT_OFFSETS[i])

    capture = True
    while capture:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_q:
                capture = False

    pygame.quit()
    return

display("Salut, comment vas-tu ?")
