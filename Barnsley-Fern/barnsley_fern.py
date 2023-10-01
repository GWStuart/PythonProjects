import pygame
import random
pygame.init()
 
iteration = 99999
zoom = 60  # Any bigger than 60 and part of the fern will be cut off
 
win = pygame.display.set_mode((610, 610))
pygame.display.set_caption("leaf")
clock = pygame.time.Clock()
 
win.fill((0, 0, 0))
point = (0, 0)
 
for i in range(iteration):
    pygame.draw.circle(win, (0, 200, 0), (point[0] * zoom + 305, point[1] * -zoom + 610), 1)
    num = random.randint(1, 100)
    if num == 1:
        point = (0, 0.16 * point[1])
    elif num <= 86:
        point = (0.85 * point[0] + 0.04 * point[1], -0.04 * point[0] + 0.85 * point[1] + 1.6)
    elif num <= 93:
        point = (0.2 * point[0] - 0.26 * point[1], 0.23 * point[0] + 0.22 * point[1] + 1.6)
    else:
        point = (-0.15 * point[0] + 0.28 * point[1], 0.26 * point[0] + 0.24 * point[1] + 0.44)
 
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
 
    pygame.display.update()
    clock.tick(60)
