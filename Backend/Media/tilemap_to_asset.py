import os, pygame

pygame.init()

TILE_SIZE = 30
N = 99

spritesheet = pygame.image.load("Backend\\Media\\Assets\\Tileset.png")
width, height = spritesheet.get_size()
cols = width / TILE_SIZE

count = 0

for i in range(N):
    col = i % cols
    row = i // cols
    rect = pygame.rect.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    tile_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    tile_surf.blit(spritesheet, (0, 0), rect)
    file_name = f"Tile_{(i+1):02d}.png"
    file_path = os.path.join("Backend\\Media\\Assets\\Tileset", file_name)
    pygame.image.save(tile_surf, file_path)

pygame.quit()