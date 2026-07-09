import pygame, Backend.connection as connection

running = True
pygame.init()
screen = pygame.display.set_mode((0, 0))
clock = pygame.time.Clock()

while running == True:
    dt = clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    connection.background(screen)
    attributes = connection.player_data(dt)
    connection.objects(screen, attributes)
    data = connection.attacks(screen, dt)
    connection.entities(screen, dt, attributes, data)
    connection.player_render(screen)
    connection.summon_entity()

    pygame.display.flip()

pygame.quit()