import pygame, Backend.Media.asset_library as asset_library
import datetime



class Screen:
    def __init__(self, screen, opacity, fade_speed):
        self.screen = screen
        self.opacity = opacity
        self.fade_speed = fade_speed
    def fade(self, fade_speed):
        self.opacity -= fade_speed
    def display(self, sprite_data, sprite_rect):
        sprite_data.set_alpha(self.opacity)
        self.screen.blit(sprite_data, sprite_rect.topleft)

class Title_Screen(Screen):
    def __init__(self, screen, opacity, fade_speed):
        super().__init__(screen, opacity, fade_speed)
        self.__image = asset_library.asset_library[-10]
        self.__text = asset_library.fonts["title_screen font"]
        self.__button_colour = "orange2"
        self.__text_colour = "grey80"
        self.__transition = False

    def buttons(self):
        self.__play_button = pygame.rect.Rect(self.screen.get_width()//2 - 125, self.screen.get_height()//2 - 50, 250, 100)
        self.__button_surface = pygame.Surface((300 , 150), pygame.SRCALPHA)
        pygame.draw.rect(self.__button_surface, self.__button_colour, pygame.rect.Rect(0, 0, 250, 100), border_radius=20)
        super().display(self.__button_surface, self.__play_button)
        #self.screen.blit(self.__button_surface, (0, 0))


        self.__text_surface = self.__text.render("Play", True, self.__text_colour)
        self.__text_rect = self.__text_surface.get_rect()
        self.__text_rect.center = pygame.Vector2(640, 405)
        super().display(self.__text_surface, self.__text_rect)

        mouse_pos = pygame.mouse.get_pos()
        if self.__play_button.collidepoint(mouse_pos):
            self.__button_colour = "orange4"
            self.__text_colour = "grey60"
            if pygame.mouse.get_pressed()[0]:
                self.__transition = True
        else:
            if self.__transition == False:
                self.__button_colour = "orange2"
                self.__text_colour = "grey80"

    def display(self):
        self.__image_rect = self.__image.get_rect()
        super().display(self.__image, self.__image_rect)

    def fade(self):
        if self.__transition == True:
            super().fade(self.fade_speed)
        if self.opacity <= 0:
            return True
        
        return False

class Connector_Screen(Screen):
    def __init__(self, screen, opacity, fade_speed, level_entering, level_name):
        super().__init__(screen, opacity, fade_speed)
        self.__level_entering = level_entering
        self.__level_entering_name = level_name
        self.__faded = False
        self.fade_start = datetime.datetime.now()
        self.__text1 = asset_library.fonts["title_screen font"]
        self.__text2 = asset_library.fonts["level name font"]

        
        self.width1 = self.__text1.size("Level " + str(self.__level_entering))[0] - 3
        self.height1 = self.__text1.get_ascent()
        self.__text_surface1 = self.__text1.render(f"Level {self.__level_entering}", True, "grey90")
        self.__text_rect1 = self.__text_surface1.get_rect()
        self.__text_rect1.topleft = pygame.Vector2(self.screen.get_width() - self.width1, self.screen.get_height() - self.height1 - 250) // 2


        self.width2 = self.__text2.size(str(self.__level_entering_name))[0] - 3
        self.height2 = self.__text2.get_ascent()
        self.__text_surface2 = self.__text2.render(f"{self.__level_entering_name}", True, "grey60")
        self.__text_rect2 = self.__text_surface2.get_rect()
        self.__text_rect2.topleft = pygame.Vector2(self.screen.get_width() - self.width2, self.screen.get_height() - self.height2 - 50)//2


    def display(self):


        super().display(self.__text_surface1, self.__text_rect1)
        super().display(self.__text_surface2, self.__text_rect2)
        pass
    def fade(self):
        if self.opacity >= 255:
            self.opacity = 255
            self.__faded = True
        if self.__faded and (datetime.datetime.now() - self.fade_start).total_seconds() > 1:   
            self.fade_speed *= -1
            self.__faded = False
        
        super().fade(-self.fade_speed)
        if self.opacity < 0:
            return True

class Death_Screen(Screen):
    def __init__(self, screen, opacity, fade_speed):
        super().__init__(screen, opacity, fade_speed)
        self.__faded = False
        self.fade_start = datetime.datetime.now()
        self.__text = asset_library.fonts["title_screen font"]

        self.width = self.__text.size("You Died")[0] - 3
        self.height = self.__text.get_ascent()
        self.__text_surface = self.__text.render("You Died", True, "grey90")
        self.__text_rect = self.__text_surface.get_rect()
        self.__text_rect.topleft = pygame.Vector2(self.screen.get_width() - self.width, self.screen.get_height() - self.height - 250) // 2


    def display(self):
        #super().display(sprite_data, sprite_rect)

        super().display(self.__text_surface, self.__text_rect)

    
    def fade(self):
        if self.opacity >= 255:
            self.opacity = 255
            self.__faded = True
        if pygame.mouse.get_pressed():
            self.fade_speed *= -1
            self.__faded = False
            print("HO")
        
        super().fade(-self.fade_speed)
        print(self.opacity)
        if self.opacity < 0:
            return True

class Death_Screen(Screen):
    def __init__(self, screen, opacity, fade_speed):
        super().__init__(screen, opacity, fade_speed)
        self.__faded = False
        self.fade_start = datetime.datetime.now()
        self.__text = asset_library.fonts["title_screen font"]

        self.width = self.__text.size("Congratulations")[0] - 3
        self.height = self.__text.get_ascent()
        self.__text_surface = self.__text.render("Congratulations", True, "grey90")
        self.__text_rect = self.__text_surface.get_rect()
        self.__text_rect.topleft = pygame.Vector2(self.screen.get_width() - self.width, self.screen.get_height() - self.height - 250) // 2


    def display(self):
        super().display(self.__text_surface, self.__text_rect)

    
    def fade(self):
        if self.opacity >= 255:
            self.opacity = 255
            self.__faded = True
        if pygame.mouse.get_pressed():
            self.fade_speed *= -1
            self.__faded = False
        
        super().fade(-self.fade_speed)
        print(self.opacity)
        if self.opacity < 0:
            return True