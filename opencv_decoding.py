from PIL import Image
import textwrap
from image_decoding import *
import pygame, sys
from pygame.locals import *

import cv2


def take_shots(capture_interval=110, n_tons=2, coding=0, rows=3, columns=5):
    N_COLORS = n_tons**3
    pygame.init()
    pygame.mouse.set_visible(False)
    cap = cv2.VideoCapture(0)
    
    RESOLUTION = (1280, 720)
    USABLE_SIZE = (RESOLUTION[0]//3, RESOLUTION[1]//3)
    USABLE_RECT = USABLE_SIZE*2
    CROP = (USABLE_SIZE[1], 2*USABLE_SIZE[1], USABLE_SIZE[0], 2*USABLE_SIZE[0])
        
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    FILENAME = 'shots/pic'
    
    preparation = 1
    run = 1
    grand_final = 1

    images = []
    PIL_images = []
    times = []
    while preparation:
        # Display preview to aim screen
        _,cv2_im = cap.read()
        cv2_im = cv2.cvtColor(cv2_im,cv2.COLOR_BGR2RGB)
        cv2_im = cv2_im[CROP[0]:CROP[1],CROP[2]:CROP[3]]
        PIL_image = Image.fromarray(cv2_im)
        string_image = PIL_image.tobytes("raw", "RGB")
        pygame_image = pygame.image.fromstring(string_image, USABLE_SIZE, "RGB", False)
        display.blit(pygame_image, USABLE_SIZE)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_s:
                pygame.time.delay(1000)# you have 1 sec to remove hands of canal
                pygame.time.set_timer(USEREVENT, capture_interval)
                preparation = 0
                display.fill((0,0,0))
                pygame.display.flip()
            if event.type == KEYDOWN and event.key == K_q:
                preparation = 0
                run = 0
                pygame.quit()
    while run:
        for event in pygame.event.get():
            if event.type == USEREVENT:
                _,cv2_im = cap.read()
                cv2_im = cv2.cvtColor(cv2_im,cv2.COLOR_BGR2RGB)
                cv2_im = cv2_im[CROP[0]:CROP[1],CROP[2]:CROP[3]]

                images.append(cv2_im)
                times.append(pygame.time.get_ticks())
            if (event.type == KEYDOWN):
                run = 0
                # stop cv2 camera if possible
    

    # add every image into a PIL list
    for i in range(1, len(images)):
        PIL_image = Image.fromarray(images[i])
        PIL_images.append(PIL_image)
        PIL_image.save(FILENAME+str(i)+'.png')
    
    # decode the images into a string
    decoded_text = decodeImage(PIL_images, N_COLORS, coding, rows, columns)

    # save the decoded message in a file
    with open("output.txt", "w") as text_file:
        print(decoded_text, text_file)
    
    # print the decoded message in terminal
    print(decoded_text)

    # Display the decoded message in the screen as soon as it is decoded
    text_to_display =  decoded_text.replace('\r', ' ').replace('\n', ' ')
    lines = textwrap.wrap(text_to_display, 100)
    display.fill((255, 255, 255))
    myfont = pygame.font.SysFont("ubuntu", 22, True)
    text_rect = pygame.Rect(50, 50, 50, 1200)
    while lines:
        line = lines[0]
        lines.pop(0)

        label = myfont.render(line, 10, (41, 83, 80))
        display.blit(label, text_rect)
        text_rect.centery += 40
    pygame.display.flip()

    # displays the message until we push on "q"
    while grand_final:
        for event in pygame.event.get():
            if (event.type == KEYDOWN and event.key == K_q):
                grand_final = 0
    
    pygame.quit()
    
                
# def take_shots(capture_interval=110, n_tons=2, coding=0, rows=3, columns=5)      
take_shots(110, 2, 10, 4, 6)
