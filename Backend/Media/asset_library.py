import pygame

pygame.init()
#Must use primitive datatypes (integers) for optimisation, so descriptions are placed as commas
asset_library = { 
    -1.1: pygame.image.load("Backend/Media/Assets/Player_Back.png"),
    -1.2: pygame.image.load("Backend/Media/Assets/Player_Left.png"), #Character sprite: Left (a)
    -1.3: pygame.image.load("Backend/Media/Assets/Player_Forward.png"), #Character sprite: Down (s)
    -1.4: pygame.image.load("Backend/Media/Assets/Player_Right.png"), #Character sprite: Right (d)
    -2.1: pygame.image.load("Backend/Media/Assets/Enemy_Right.png"),
    -2.2: pygame.image.load("Backend/Media/Assets/Enemy_Left.png"),
    -3.1: pygame.image.load("Backend/Media/Assets/Demon_Right.png"),
    -3.2: pygame.image.load("Backend/Media/Assets/Demon_Left.png"),
    -4: pygame.image.load("Backend/Media/Assets/holy-ray.png"),
    -5: pygame.image.load("Backend/Media/Assets/force.png"),
    -10: pygame.image.load("Backend/Media/Assets/Inferno_Backdrop.png")
}



tile_assets = {}
tile_assets[0] = pygame.surface.Surface((0, 0))

for i in range(1, 120):
    tile_assets[i] = pygame.image.load(f"Backend/Media/Assets/Tileset/Tile_{i:02d}.png")
    tile_assets[i] = pygame.transform.scale(tile_assets[i], (48, 48))


fonts = {
    "title_screen font": pygame.font.Font("Backend/Media/Assets/Font.ttf", 96),
    "victory font": pygame.font.Font("Backend/Media/Assets/Font.ttf", 80),
    "level name font": pygame.font.Font("Backend/Media/Assets/Font.ttf", 60),
    "help screen font": pygame.font.Font("Backend/Media/Assets/Font.ttf", 24),
    "large font": pygame.font.Font("Backend/Media/Assets/Font.ttf", 48),
    "medium font": pygame.font.Font("Backend/Media/Assets/Font.ttf", 32),
    "small font": pygame.font.Font("Backend/Media/Assets/Font.ttf", 16)}

collision_tiles = [0, 30, 31, 32, 33, 34, 35, 36, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 54, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 86, 87, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 101, 102, 103, 104, 105, 106, 107]
level_change_tiles = [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]
damage_tiles = [91, 92, 93, 94, 95, 96, 97, 98, 98]