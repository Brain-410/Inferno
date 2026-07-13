import pygame
#Must use primitive datatypes (integers) for optimisation, so descriptions are placed as commas
asset_library = { 
    2: pygame.Surface((5, 5)),
    1: pygame.Surface((32, 32)), # Floor
    0: pygame.Surface((0, 0)), #Blank area (i.e. void)
    -1.1: pygame.Surface((48, 48)), #Character sprite: Forward (w)
    -1.2: pygame.Surface((48, 48)), #Character sprite: Left (a)
    -1.3: pygame.Surface((48, 48)), #Character sprite: Down (s)
    -1.4: pygame.Surface((48, 48)), #Character sprite: Right (d)
    -2: pygame.Surface((16, 16)),
    -3: pygame.Surface((24, 24))
}


#temporary, will remove when proper assets are made
asset_library[2].fill((255, 0, 255))
asset_library[1].fill((255, 255, 255))
asset_library[-1.1].fill((0, 0, 255)) 
asset_library[-1.2].fill((0, 0, 220))
asset_library[-1.3].fill((0, 0, 200))
asset_library[-1.4].fill((0, 0, 180))
asset_library[-2].fill((255, 0, 0))

collision_tiles = [2]