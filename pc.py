from rtcom import RealTimeCommunication
import cv2
import numpy as np
from time import sleep
from utils import write_header, write_line
import pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()


with RealTimeCommunication("pc") as rtcom:
    rtcom.subscribe("duckie","camera") #Request unicast for this specific endpoint.
    #(Too much packet drop on multicast for some reason.)
    print("Press escape to quit.")
    running = True
    last_speed=None
    i=0
    while True:
        i+=1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        try:
            pressed = pygame.key.get_pressed()
            image_data = rtcom["duckie"]["camera"]
            if image_data is not None:
                jpg_data = np.asarray(image_data)
                img = cv2.imdecode(jpg_data, cv2.IMREAD_UNCHANGED)

                write_header(img, "Video Feed")
                data = rtcom["duckie"]["data"]
                for i, name in enumerate(data):
                    write_line(img, i, f"{name} : {data[name][0]:0.1f} {data[name][1]}")                
                #cv2.imshow("preview", img) 
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = np.moveaxis(img,[0,1],[1,0])
                surf = pygame.surfarray.make_surface(img)
                screen.blit(surf, (0, 0))
                pygame.display.update()


            #key = cv2.waitKey(20)
            speed = {}
            speed["left"] = 0 
            speed["right"] = 0

            if pressed[pygame.K_w]:
                speed["left"] = speed["right"] = 0.5
            if pressed[pygame.K_s]:
                speed["left"] = speed["right"] = -0.5
            if pressed[pygame.K_a]:
                speed["right"] += 0.5
            if pressed[pygame.K_d]:
                speed["left"]  += 0.5

            if i%40==0:
                print("speed", speed)
                rtcom.broadcast_endpoint("speed", speed)    

            if speed!=last_speed:
                last_speed=speed

            sleep(0.005)


        except KeyError:
            pass

