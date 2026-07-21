import pygame, Backend.connection as connection, Backend.Media.asset_library as asset_library

running = True
pygame.init()
screen = pygame.display.set_mode((720, 448))
clock = pygame.time.Clock()
for asset in asset_library.asset_library.values():
    asset = asset.convert_alpha()
for asset in asset_library.tile_assets.values():
    asset = asset.convert()

while running == True:
    dt = clock.tick (60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    connection.clear(screen)



        
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