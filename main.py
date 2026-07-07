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
    attributes = connection.player(screen, dt)
    connection.objects(screen, attributes)
    #connection.entities(screen, dt, attributes)

    pygame.display.flip()

pygame.quit()