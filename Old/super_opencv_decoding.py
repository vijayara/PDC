from __future__ import print_function
from imutils.video import WebcamVideoStream
from PIL import Image
import textwrap
from image_decoding import *
import pygame, sys
from pygame.locals import *
import time
import cv2


current_milli_time = lambda: int(round(time.time() * 1000))

def take_shots(capture_interval=110, n_tons=2, coding=0, rows=3, columns=5):
    N_COLORS = n_tons**3
    pygame.init()
    pygame.mouse.set_visible(False)
    
    RESOLUTION = (1280, 720)
    USABLE_SIZE = (RESOLUTION[0]//3, RESOLUTION[1]//3)
    USABLE_RECT = USABLE_SIZE*2
    CROP = (USABLE_SIZE[1], 2*USABLE_SIZE[1], USABLE_SIZE[0], 2*USABLE_SIZE[0])
    
    cap = cv2.VideoCapture(0)
    # 3 and 4 are the constants to access camera width and height
    cap.set(3, RESOLUTION[0])
    cap.set(4, RESOLUTION[1])
    bad_images = 340//capture_interval
 
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    FILENAME = 'shots/pic'
    
    preparation = 1
    run = 1
    grand_final = 1


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
                #pygame.time.set_timer(USEREVENT, capture_interval)
                preparation = 0
                display.fill((0,0,0))
                pygame.display.flip()
            if event.type == KEYDOWN and event.key == K_q:
                preparation = 0
                run = 0
                pygame.quit()

    # quit non threaded camera
    cap.release()

    # Add threaded camera
    vs = WebcamVideoStream(src=0).start()
    previous_time = 0
    frames = []

    #for test
    times = []

    while run:
        current_time = current_milli_time()
        loop_time = current_time % capture_interval

        if loop_time < previous_time:
            frame = vs.read()
            frames.append(frame)
            # for interval test
            times.append(current_time)
        previous_time = loop_time

        for event in pygame.event.get():
            if (event.type == KEYDOWN):
                run = 0
                # stop cv2 camera if possible

    # transform frame into PIL format, skipping the first one
    # for quality reason
    PIL_images = []
    for frame in frames[bad_images:]:
        cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        cv2_im = cv2_im[CROP[0]:CROP[1],CROP[2]:CROP[3]]
        pil_im = Image.fromarray(cv2_im)
        PIL_images.append(pil_im)

    try:
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


    except Exception as e:

        for x in range(1, len(PIL_images)): 
            PIL_images[x].save(FILENAME + str(x) + ".png")
            if (x < len(frames)-1):
                print("Interval", str(x-1)+"-"+str(x)+": "+str(times[x]-times[x-1]))

        print(e)
    pygame.quit()
    
config_safe = (110, 2, 10, 3, 5)
config1 = (110, 2, 30, 4, 6)
config2 = (42, 2, 30, 4, 6)
config_test = (42, 2, 30, 4, 6)

# take_shots(capture_interval=110, n_tons=2, coding=0, rows=3, columns=5)      
take_shots(*config_test)
