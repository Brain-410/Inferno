import pygame, Backend.connection as connection

running = True
pygame.init()
screen = pygame.display.set_mode((0, 0))
clock = pygame.time.Clock()

while running == True:
    dt = clock.tick (60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    connection.clear(screen)
    attributes = connection.player_data(screen, dt)
    connection.objects(screen, attributes)
    connection.attacks(screen, dt)
    connection.entities(screen, dt, attributes)
    connection.player_render()
    connection.summon_entity(attributes)

    pygame.display.flip()

pygame.quit()

#aaad