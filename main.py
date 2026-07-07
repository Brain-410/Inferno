import pygame
import Backend.connection as connection

running = True
pygame.init()
screen = pygame.display.set_mode((0, 0))
clock = pygame.time.Clock()

while running == True:
    dt = clock.tick(60)/1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
    connection.background(screen, dt) #temporary
    offset = connection.player(screen, dt)
    connection.objects(screen, dt, offset)
    #connection.entities(screen, dt, offset)

    pygame.display.flip()

pygame.quit()