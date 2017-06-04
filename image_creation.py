# PDC Project
# Authors: Thierry B., Niroshan V., Ignacio A.

from tools import *
import pygame
from pygame.locals import *

def display(text, rows=4, columns=6, n_tons=2, refresh_interval=110, coding=0, cross_size=30):
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
    
    color_message = text_to_colors(text, N_TONS, coding)
    
    # number of colors not used at the end of the message
    n_colors_last_quadrant = len(color_message) % N_TILES
    remaining_colors = (N_TILES - n_colors_last_quadrant) if n_colors_last_quadrant else 0
    # number of quadrants needed for the message
    n_message_quadrants = len(color_message) // N_TILES + (remaining_colors != 0)
    
    # fill a color matrix where each row is a quadrant
    quadrants_colors = [color_message[N_TILES*y:N_TILES*(y+1)] for y in range(n_message_quadrants)]
    
    # create particular quadrants : 4 starting quadrants (red, green, blue)
    # plus yellow to avoid white plus the black one
    particular_quadrants = [pygame.surface.Surface(QUADRANT_SIZE) for i in range(5)]
    for i in range(3):
        particular_quadrants[i].fill(COLOR[MOST_DISTANCES[i]])
    yellow_index = (N_TONS**2)*(N_TONS-1)+(N_TONS)*(N_TONS-1)
    particular_quadrants[3].fill(COLOR[yellow_index]) #yellow
    particular_quadrants[4].fill(COLOR[0]) #black
    
    # creation of the dictionnary and padding quadrant with the colors, and the number of remaining colors after
    
    N_TILES_FOR_PADDING_INFO = 2
    
    # number of tiles and quadrants needed for dictionnary and padding
    # DPQ : Dictionary and Padding quadrant
    N_TILES_FOR_DPQ = N_COLORS + N_TILES_FOR_PADDING_INFO
    N_DPQ = N_TILES_FOR_DPQ // N_TILES + ((N_TILES_FOR_DPQ%N_TILES) != 0)
    
    # sequence of colors to send the number of padding colors
    colors_for_padding = [0, 0] if not remaining_colors else base_change([remaining_colors], 10, N_COLORS)

    if(len(colors_for_padding) != 2):
        if (len(colors_for_padding) == 1):
            colors_for_padding = [0] + colors_for_padding
        else:
            print("error in padding colors")
    
    # sequence of colors for the dictionnary and padding
    colors_for_dictionnary_padding = list(range(N_COLORS)) + colors_for_padding
    
    # creates the dictionnary padding quadrants and fill the in black
    dictionnary_padding_quadrants = [pygame.surface.Surface(QUADRANT_SIZE) for i in range(N_DPQ)]
    for i in range(N_DPQ):
        dictionnary_padding_quadrants[i].fill(COLOR[0])
    
    # fill the dictionnary padding quadrants with the needed colors
    for c in range(N_TILES_FOR_DPQ):
        quadrant_index = c // N_TILES
        tile_index = c % N_TILES
        color = COLOR[colors_for_dictionnary_padding[c]]
        rect = pygame.Rect(TILE_OFFSETS[tile_index], TILE_SIZE)
        dictionnary_padding_quadrants[quadrant_index].fill(color, rect)

    # create every quadrants for the message
    message_quadrants = [pygame.surface.Surface(QUADRANT_SIZE) for i in range(n_message_quadrants)]
    for q in range(len(message_quadrants)):
        for c in range(len(quadrants_colors[q])):
            color = COLOR[quadrants_colors[q][c]]
            rect = pygame.Rect(TILE_OFFSETS[c], TILE_SIZE)
            message_quadrants[q].fill(color, rect)
            
    # put the dictionnary_padding as the first quadrant of the message
    n_quadrants = N_DPQ + n_message_quadrants
    quadrants = dictionnary_padding_quadrants + message_quadrants
    
    # set the display to the entire screen
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    for i in range(4):
        display.blit(particular_quadrants[i], QUADRANT_OFFSETS[i])
    
    
    # Printing informations ----------------------------------------------------------
    # print("-> Colors of the message:\n", quadrants_colors)
    # print("-> Verification text (reverse):\n", colors_to_text(color_message, N_TONS, coding))
    # print("-> Number of quadrants:", n_quadrants)
    # print("-> Padding:", remaining_colors)
    # print("-> Padding info:", colors_for_padding)
    # print("-> Number of quadrants for dictionnary and padding:", N_DPQ)
    # --------------------------------------------------------------------------------


    # run with the following scheme:
    
    ###############################
    ##### 1 ###### 2 ###### 3 #####
    ###       ##       ##       ###
    ###  D A  ##  B D  ##  C C  ###
    ###  A A  ##  B B  ##  C D  ###
    ###       ##       ##       ###
    ###############################
    ###############################
    
    run = True
    current_quadrant = 0
    pygame.display.flip()
    while run:
        for event in pygame.event.get():
            # START with key S
            if event.type == KEYDOWN and event.key == K_s:
                # wait 3 secs more for the  first screen (to go to start decoder and remove your hands)
                pygame.time.delay(3000)
                pygame.time.set_timer(USEREVENT, refresh_interval)
            # Loop and refresh screen
            if event.type == USEREVENT:
                if(current_quadrant >= n_quadrants):
                    # fill everything in green at the end
                    for i in range(4):
                        display.blit(particular_quadrants[1], QUADRANT_OFFSETS[i])
                    pygame.display.flip()
                    break
                config = current_quadrant%4
                if config == 0:
                    for i in (1,2,3):
                        display.blit(quadrants[current_quadrant], QUADRANT_OFFSETS[i])
                    if(current_quadrant+3 < n_quadrants):
                        display.blit(quadrants[current_quadrant+3], QUADRANT_OFFSETS[0])
                    else:
                        # fill in green if nothin to display
                        display.blit(particular_quadrants[1], QUADRANT_OFFSETS[0])
                elif config == 1:
                    for i in (0,2,3):
                        display.blit(quadrants[current_quadrant], QUADRANT_OFFSETS[i])
                    if(current_quadrant+2 < n_quadrants):
                        display.blit(quadrants[current_quadrant+2], QUADRANT_OFFSETS[1])
                    else:
                        # fill in green if nothin to display
                        display.blit(particular_quadrants[1], QUADRANT_OFFSETS[1])
                elif config == 2:
                    for i in (0,1,2):
                        display.blit(quadrants[current_quadrant], QUADRANT_OFFSETS[i])
                    if(current_quadrant+1 < n_quadrants):
                        display.blit(quadrants[current_quadrant+1], QUADRANT_OFFSETS[3])
                    else:
                        # fill in green if nothin to display
                        display.blit(particular_quadrants[1], QUADRANT_OFFSETS[3])
                    # at config 2, one more increment to skip the D
                    current_quadrant += 1
                else:
                    print("ERROR: didn't skip a fourth screen of cycle")
                  
                pygame.display.flip()
                current_quadrant += 1
            # QUIT with key Q
            if event.type == KEYDOWN and event.key == K_q:
                run = False

    pygame.quit()
    return

with open('text.txt', 'r') as myfile:
    text = myfile.read()

config_safe = (text, 3, 5, 2, 3*110, 30)
config_speed = (text, 4, 6, 2, 3*40, 30)
config_test = (text, 4, 6, 2, 4*42, 30)

# def display(text, rows=4, columns=6, n_tons=2, refresh_interval=110, coding=0, cross_size=30):
display(*config_speed)
