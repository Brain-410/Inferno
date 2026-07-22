import pygame, Backend.Media.asset_library as asset_library
import datetime, copy



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
        self.__small_text = asset_library.fonts["medium font"]
        self.__help_screen_text = asset_library.fonts["help screen font"]
        self.__large_text = asset_library.fonts["level name font"]
        self.__button_colour = "orange2"
        self.__button_colour2 = "orange2"
        self.__text_colour = "grey80"
        self.__text_colour2 = "grey80"
        self.__transition = False

        self.__sub_screen = "Title"

        self.__owner_text = asset_library.fonts["small font"].render("By Baidyn M", True, (220, 220, 220))

        # Title Tab

        self.__play_button = pygame.rect.Rect(self.screen.get_width()//2 - 125, self.screen.get_height()//2 - 50, 250, 100)
        self.__button_surface = pygame.Surface((300 , 150), pygame.SRCALPHA)

        self.__text_surface = self.__text.render("Play", True, self.__text_colour)
        self.__text_rect = self.__text_surface.get_rect()
        self.__text_rect.center = pygame.Vector2(360, 229)

        self.__play_button3 = pygame.rect.Rect(self.screen.get_width()//2 - 80, self.screen.get_height()//2 + 100, 250, 100)
        self.__button_surface3 = pygame.Surface((300 , 150), pygame.SRCALPHA)
        self.__text_surface3 = self.__large_text.render("Help", True, self.__text_colour2)
        self.__text_rect3 = self.__text_surface3.get_rect()
        self.__text_rect3.center = pygame.Vector2(365, 365)

        # Settings Tab
        self.__background_rect = pygame.rect.Rect(00, 00, 700, 428)
        self.__background_surface = pygame.Surface((680, 408), pygame.SRCALPHA)
        self.__background_surface.set_alpha(240)

        self.__back_button = pygame.rect.Rect(0, 0, 100, 50)
        self.__back_button_surface = pygame.Surface((150 , 100), pygame.SRCALPHA)

        self.__text_surface2 = self.__small_text.render("Back", True, self.__text_colour)
        self.__text_rect2 = self.__text_surface2.get_rect()
        self.__text_rect2.topleft = pygame.Vector2(30, 32)

        self.__help_text = "Use WASD keys to move\nUse the left mouse button to shoot a laser\nUse the right mouse button for a melee attack\nPress Tab to heal\nHint 1: look for gates\nHint 2: Use a mouse\nGood Luck!"

        self.__back_colour = "indianred4"

    def buttons(self):
        if self.__sub_screen == "Title":
            pygame.draw.rect(self.__button_surface, self.__button_colour, pygame.rect.Rect(0, 0, 250, 100), border_radius=20)
            super().display(self.__button_surface, self.__play_button)
            super().display(self.__text_surface, self.__text_rect)

            pygame.draw.rect(self.__button_surface3, self.__button_colour2, pygame.rect.Rect(0, 0, 160, 70), border_radius=20)
            super().display(self.__button_surface3, self.__play_button3)
            super().display(self.__text_surface3, self.__text_rect3)



            mouse_pos = pygame.mouse.get_pos()
            if self.__play_button.collidepoint(mouse_pos):
                self.__button_colour = "orange4"
                self.__text_colour = "grey60"
                if pygame.mouse.get_pressed()[0]: #Start Game
                    self.__transition = True
            else:
                if self.__transition == False:
                    self.__button_colour = "orange2"
                    self.__text_colour = "grey80"
            if self.__play_button3.collidepoint(mouse_pos):
                self.__button_colour2 = "orange4"
                self.__text_colour2 = "grey60"
                if pygame.mouse.get_pressed()[0]: #Switch to help tab
                    self.__sub_screen = "Settings"
            else:
                if self.__transition == False:
                    self.__button_colour2 = "orange2"
                    self.__text_colour2 = "grey80"
            
    
        elif self.__sub_screen == "Settings":

            # Overlay
            pygame.draw.rect(self.__background_surface, "indianred", self.__background_rect)
            self.screen.blit(self.__background_surface, (20, 22))

            # Back button
            pygame.draw.rect(self.__back_button_surface, self.__back_colour, pygame.rect.Rect(20, 22, 100, 50), border_radius=20)
            super().display(self.__back_button_surface, self.__back_button)

            super().display(self.__text_surface2, self.__text_rect2)

            self.__location = pygame.rect.Rect(20, 22, 100, 50)


            for i, line in enumerate(self.__help_text.split("\n")):
                surface = self.__help_screen_text.render(line, True, (220, 220, 220))
                current_y = 90 + i * 48

                self.screen.blit(surface, (90, current_y))


            mouse_pos = pygame.mouse.get_pos()
            if self.__location.collidepoint(mouse_pos):
                self.__back_colour = (130, 0, 0)
                if pygame.mouse.get_pressed()[0]:
                    self.__sub_screen = "Title"
            else:
                self.__back_colour = "indianred4"


    def display(self):
        self.__image_rect = self.__image.get_rect()
        super().display(self.__image, self.__image_rect)
        self.screen.blit(self.__owner_text, (590,30))

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
        self.__start_fade_speed = copy.copy(self.fade_speed)

        self.__faded = False
        self.fade_start = datetime.datetime.now()
        self.__text1 = asset_library.fonts["title_screen font"]
        self.__text2 = asset_library.fonts["small font"]

        self.width1 = self.__text1.size("You Died")[0] - 3
        self.height1 = self.__text1.get_ascent()
        self.__text_surface1 = self.__text1.render("You Died", True, "grey90")
        self.__text_rect1 = self.__text_surface1.get_rect()
        self.__text_rect1.topleft = pygame.Vector2(self.screen.get_width() - self.width1, self.screen.get_height() - self.height1 - 250) // 2

        self.width2 = self.__text2.size("(Press anywhere to continue)")[0] - 3
        self.height2 = self.__text2.get_ascent()
        self.__text_surface2 = self.__text2.render("(Press anywhere to continue)", True, "grey90")
        self.__text_rect2 = self.__text_surface2.get_rect()
        self.__text_rect2.topleft = pygame.Vector2(self.screen.get_width() - self.width2, self.screen.get_height() - self.height2 - 100) // 2



    def display(self):
        #super().display(sprite_data, sprite_rect)

        super().display(self.__text_surface1, self.__text_rect1)
        super().display(self.__text_surface2, self.__text_rect2)

    
    def fade(self):
        if self.opacity >= 255:
            self.opacity = 255
            self.__faded = True
        if self.__faded and (pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[1] or pygame.mouse.get_pressed()[2]):
            self.fade_speed = -self.__start_fade_speed
            self.__faded = False
        
        super().fade(-self.fade_speed)
        if self.opacity < 0:
            return True

class Victory_Screen(Screen):
    def __init__(self, screen, opacity, fade_speed):
        super().__init__(screen, opacity, fade_speed)

        self.__start_fade_speed = copy.copy(self.fade_speed)
        self.__faded = False
        self.fade_start = datetime.datetime.now()
        self.__text = asset_library.fonts["victory font"]
        self.__text2 = asset_library.fonts["small font"]

        self.width = self.__text.size("Congratulations")[0] - 3
        self.height = self.__text.get_ascent()
        self.__text_surface = self.__text.render("Congratulations", True, "grey90")
        self.__text_rect = self.__text_surface.get_rect()
        self.__text_rect.topleft = pygame.Vector2(self.screen.get_width() - self.width, self.screen.get_height() - self.height - 250) // 2

        self.width3 = self.__text.size("You win!")[0] - 3
        self.height3 = self.__text.get_ascent()
        self.__text_surface3 = self.__text.render("You win!", True, "grey90")
        self.__text_rect3 = self.__text_surface3.get_rect()
        self.__text_rect3.topleft = pygame.Vector2(self.screen.get_width() - self.width3, self.screen.get_height() - self.height3 - 50) // 2

        self.width2 = self.__text2.size("(Press anywhere to continue)")[0] - 3
        self.height2 = self.__text2.get_ascent()
        self.__text_surface2 = self.__text2.render("(Press anywhere to continue)", True, "grey90")
        self.__text_rect2 = self.__text_surface2.get_rect()
        self.__text_rect2.topleft = pygame.Vector2(self.screen.get_width() - self.width2, self.screen.get_height() - self.height2 + 300) // 2



    def display(self):
        super().display(self.__text_surface, self.__text_rect)
        super().display(self.__text_surface2, self.__text_rect2)
        super().display(self.__text_surface3, self.__text_rect3)

    
    def fade(self):
        if self.opacity >= 255:
            self.opacity = 255
            self.__faded = True
        if self.__faded and (pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[1] or pygame.mouse.get_pressed()[2]):
            self.fade_speed = -self.__start_fade_speed
            self.__faded = False
        
        super().fade(-self.fade_speed)
        if self.opacity < 0:
            return True