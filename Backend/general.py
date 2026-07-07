import pygame

class Object:
    def __init__(self, position: pygame.Vector2, dimensions: list, image, colour):
        self.position = position
        self.__dimensions = dimensions
        self.__image = image
        self.__colour = colour
    def display(self, screen):
        if self.__image != None:
            pass
            #self.screen.blit()
        pygame.draw.rect(screen, self.__colour, pygame.rect.Rect(self.position.x, self.position.y, self.__dimensions[0], self.__dimensions[1]))
    def move(self, velocity: pygame.Vector2):
        self.position -= velocity

class Enemy(Object):
    def __init__(self, start_pos, size, colour, max_speed):
        super().__init__(start_pos, size, None, colour)
        self.__max_speed = max_speed
        self.__acceleration = 15
        self.velocity = pygame.Vector2(0, 0)
    def display(self, screen):
        Object.display(self, screen)
    def move(self, target):
        Object.move(self)



class Player(Object):
    def __init__(self, start_pos, size, colour, max_speed):
        super().__init__(start_pos, size, None, colour)
        self.__max_speed = max_speed
        self.__acceleration = 15
        self.velocity = pygame.Vector2(0, 0)
    
    def display(self, screen):
        Object.display(self, screen)
    
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
