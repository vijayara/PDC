import math
import pygame
from pygame.locals import *


def camstream():
    pygame.init()
    pygame.mouse.set_visible(False)
    
    # total screen size
    SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    
    # [TO PLAY WITH] separating cross width
    CROSS_SIZE = 30
    QUADRANT_SIZE = ((SIZE[0]-CROSS_SIZE)/2, (SIZE[1]-CROSS_SIZE)/2)
    # quadrant offsets
    W_OFFSET = QUADRANT_SIZE[0] + CROSS_SIZE
    H_OFFSET = QUADRANT_SIZE[1] + CROSS_SIZE
    
    # [TO PLAY WITH] number of lines and columns per quadrant
    LINE = 3
    COLUMN = 3
    
    # [TO PLAY WITH] number of possible levels for each color
    N_TONS = 2
    TON = [(i)*255/(N_TONS-1) for i in range(0, N_TONS)]
    
    COMBINATIONS = N_TONS**(3*LINE*COLUMN)
    BITS_BY_QUADRAND = math.log(COMBINATIONS, 2)
    
    
    # number of colors
    N_COLORS = N_TONS**3
    
    # fill the color array
    COLOR = []
    for i in range(0, N_TONS):
        for j in range(0, N_TONS):
            for k in range (0, N_TONS):
                color = ((TON[i], TON[j], TON[k]))
                COLOR.append(color)
    
    # select indexes of 4 most distances colors (red, green, blue, white)
    MOST_DISTANCES = []
    for i in range (0, 3):
        MOST_DISTANCES.append((N_TONS**i)*(N_TONS-1))
    MOST_DISTANCES.append(N_COLORS-1)
        
    display = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
    screen = [pygame.surface.Surface(QUADRANT_SIZE, 0, display)]*4
    
    for i in range(0, 4):
        screen[i].fill(COLOR[MOST_DISTANCES[i]])
        display.blit(screen[i], (((i%2)*W_OFFSET), (i//2)*H_OFFSET))
    
    capture = True
    while capture:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                capture = False
    pygame.quit()
    return

camstream()
