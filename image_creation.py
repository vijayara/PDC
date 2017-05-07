import math
from bitstring import BitArray
import zlib
import pygame
from pygame.locals import *

def encode(string):
    in_bytes = string.encode("utf-8")
    compressed = zlib.compress(in_bytes, 9)
    return compressed

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

    # number of rows and columns per quadrant
    ROWS = rows
    COLUMN = columns

    # number of possible levels for each color
    N_TONS = n_tons
    TON = [(i)*255/(N_TONS-1) for i in range(N_TONS)]

    COMBINATIONS = N_TONS**(3*ROWS*COLUMN)
    BITS_BY_QUADRANT = math.floor(math.log(COMBINATIONS, 2))

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
    
    encoded = encode(text)
    bits = BitArray(encoded)
    
    remaining_bits = len(bits) % BITS_BY_QUADRANT
    n_quadrants = len(bits) // BITS_BY_QUADRANT + (remaining_bits != 0)
    print(type(BITS_BY_QUADRANT))
    quadrants_bits = [[False for x in range(BITS_BY_QUADRANT)] for y in range(n_quadrants)] 
    
    for i in range(len(bits)):
        quadrants_bits[i//BITS_BY_QUADRANT][i%BITS_BY_QUADRANT] = bits[i]

    # set the display to the entire screen
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)#, max(math.ceil(math.log(7**3, 2)), 8))
    # set the 4 quadrants with their positions
    screen = [pygame.surface.Surface(QUADRANT_SIZE, 0, display)]*4

    for i in range(4):
        screen[i].fill(COLOR[MOST_DISTANCES[i]])
        display.blit(screen[i], (((i%2)*W_OFFSET), (i//2)*H_OFFSET))

    capture = True
    while capture:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_q:
                capture = False

    pygame.quit()
    return
    
display("salut")
