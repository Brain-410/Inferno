import pygame

asset_library = {
    1: pygame.Surface((32, 32)),
    0: pygame.Surface((0, 0)),
    -1: pygame.Surface((48, 48))
}

class Object:
    def display(self, screen, type, position):
        screen.blit(asset_library[type], position)

    def move(self, velocity: pygame.Vector2):
        self.position -= velocity

class Entity(Object):
    def __init__(self, start_pos, size, max_speed):
        self.__position = start_pos
        self.__max_speed = max_speed
        self.__acceleration = 15
        self.velocity = pygame.Vector2(0, 0)
    def display(self, screen):
        Object.display(self, screen)
    def move(self, target):
        Object.move(self)

class Objects(Object):
    def display(self, screen, type, position):
        Object.display(screen, type, position)
    def move(self, velocity):
        Object.move(self, velocity)
    def collide(self):
        pass


class Player(Object):
    def __init__(self, max_speed):
        self.__max_speed = max_speed
        self.__acceleration = 15
        self.velocity = pygame.Vector2(0, 0)
        self.real_position = pygame.Vector2(100, 100)
    
    def display(self, screen):
        Object.display(self, screen, -1, (screen.get_width() // 2, screen.get_height() // 2))
    
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.velocity.x -= self.__acceleration * self.dt
            if abs(self.velocity.x) >= self.__max_speed:
                self.velocity.x = self.velocity.x/abs(self.velocity.x) * self.__max_speed
        elif keys[pygame.K_d]:
            self.velocity.x += self.__acceleration * self.dt
            if abs(self.velocity.x) >= self.__max_speed:
                self.velocity.x = self.velocity.x/abs(self.velocity.x) * self.__max_speed
        else:
            if self.velocity.x <= 0.5 and self.velocity.x >= -0.5:
                self.velocity.x = 0
            else:
                self.velocity.x *= 0.85
        if keys[pygame.K_w]:
            self.velocity.y -= self.__acceleration * self.dt
            if abs(self.velocity.y) >= self.__max_speed:
                self.velocity.y = self.velocity.y/abs(self.velocity.y) * self.__max_speed
        elif keys[pygame.K_s]:
            self.velocity.y += self.__acceleration * self.dt
            if abs(self.velocity.y) >= self.__max_speed:
                self.velocity.y = self.velocity.y/abs(self.velocity.y) * self.__max_speed
        else:
            if self.velocity.y <= 0.5 and self.velocity.y >= -0.5:
                self.velocity.y = 0
            else:
                self.velocity.y *= 0.85
        self.real_position += self.velocity