import pygame, Backend.connection as connection, Backend.Media.asset_library as asset_library

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

    for asset in asset_library.asset_library.values():
        asset.convert_alpha()
    for asset in asset_library.tile_assets.values():
        asset.convert_alpha()
    connection.run_screen(screen)
    attributes = connection.player_data(screen, dt)
    connection.objects(screen, attributes)
    connection.attacks(dt)
    connection.enemies(screen, dt, attributes)
    connection.player_render(attributes)
    connection.summon_enemy(attributes)
    connection.user_interface(screen, attributes)

    pygame.display.flip()

pygame.quit()

#