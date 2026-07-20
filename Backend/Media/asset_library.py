import pygame

pygame.init()
#Must use primitive datatypes (integers) for optimisation, so descriptions are placed as commas
asset_library = { 
    4: pygame.Surface((1, 1)),
    3: pygame.Surface((1, 5)),
    2: pygame.image.load("Backend\\Media\\Assets\\Grass.png"),
    1: pygame.image.load("Backend\\Media\\Assets\\Dirt.png"), # Floor
    0: pygame.Surface((0, 0)), #Blank area (i.e. void)
    -1.1: pygame.image.load("Backend\\Media\\Assets\\Player_Back.png"),
    -1.2: pygame.image.load("Backend\\Media\\Assets\\Player_Left.png"), #Character sprite: Left (a)
    -1.3: pygame.image.load("Backend\\Media\\Assets\\Player_Forward.png"), #Character sprite: Down (s)
    -1.4: pygame.image.load("Backend\\Media\\Assets\\Player_Right.png"), #Character sprite: Right (d)
    -2: pygame.Surface((16, 16)),
    -3: pygame.Surface((24, 24)),
    -4: pygame.image.load("Backend\\Media\\Assets\\holy-ray.png"),
    -10: pygame.image.load("Backend\\Media\\Assets\\Inferno_backdrop.png")
}


tile_assets = {}

for i in range(1, 99):
    tile_assets[i] = pygame.image.load(f"Backend\\Media\\Assets\\Tileset\\Tile_{i:02d}.png")

fonts = {
    "title_screen font": pygame.font.Font("Backend\\Media\\Assets\\Font.ttf", 96),
    "level name font": pygame.font.Font("Backend\\Media\\Assets\\Font.ttf", 60),
    "large font": pygame.font.Font("Backend\\Media\\Assets\\Font.ttf", 48),
    "small font": pygame.font.Font("Backend\\Media\\Assets\\Font.ttf", 16)}

#temporary, will remove when proper assets are made
asset_library[4].fill((0, 255, 0))
asset_library[3].fill((0, 255, 255))
asset_library[-2].fill((255, 0, 0))

collision_tiles = [2]
new_level = [30, 31, 32, 33, 34, 35, 36, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 67, 68, 69, 86, 87, 89, 90]