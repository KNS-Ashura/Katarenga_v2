import pygame
import sys

class Board_draw_tools:
        
    def draw_all_corners(self, surface):
        
            #DRAW CORNER
        self.draw_corner_top_left(surface)
        self.draw_corner_top_right(surface)
        self.draw_corner_bot_left(surface)
        self.draw_corner_bot_right(surface)

        #DRAW RECTANGLE 
        self.draw_rectangle_left(surface)
        self.draw_rectangle_right(surface)
        self.draw_rectangle_top(surface)
        self.draw_rectangle_bot(surface)
    
    def draw_corner_top_left(self,surface):
        
        rect = pygame.Rect(340, 20, 60, 60)
        pygame.draw.rect(surface, (255, 165, 0), rect)
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)

    def draw_corner_top_right(self,surface):
        rect = pygame.Rect(
            880,  
            20,  
            60,  
            60   
        )
        pygame.draw.rect(surface, (255, 165, 0), rect)  
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)  

    def draw_corner_bot_left(self,surface):
        rect = pygame.Rect(
            340,  
            560, 
            60,  
            60   
        )
        pygame.draw.rect(surface, (255, 165, 0), rect)  
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)  

    def draw_corner_bot_right(self,surface):
        rect = pygame.Rect(
            880,  
            560,  
            60,  
            60   
        )

        pygame.draw.rect(surface, (255, 165, 0), rect)  
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)  

        
    #DRAW RECTANGLE DESIGN KATARENGA

    def draw_rectangle_left(self,surface):
        rect = pygame.Rect(
            340, # x = collé à gauche
            80, # y = collé en haut
            60, # largeur
            480 # hauteur
        )

        pygame.draw.rect(surface, (100, 65, 0), rect)  
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)  

    def draw_rectangle_right(self,surface):
        rect = pygame.Rect(
            880,  
            80,  
            60,  
            480 
        )

        pygame.draw.rect(surface, (100, 65, 0), rect)  
        pygame.draw.rect(surface, (255, 255, 255), rect, 1) 

    def draw_rectangle_top(self,surface):
        rect = pygame.Rect(
            400, 
            20, 
            480, 
            60 
        )

        pygame.draw.rect(surface, (100, 65, 0), rect)  
        pygame.draw.rect(surface, (255, 255, 255), rect, 1) 

    def draw_rectangle_bot(self,surface):
        rect = pygame.Rect(
            400, 
            560,  
            480,  
            60 
        )

        pygame.draw.rect(surface, (100, 65, 0), rect)  
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)  

    def get_color_from_board(self, code):
        if code == 1:
            return (100, 160, 230)  
        elif code == 2:
            return (125, 190, 155)  
        elif code == 3:
            return (240, 200, 80)
        elif code == 4:
            return (235, 115, 115)  
        elif code == 5:
            return (128, 0, 128)
        else:
            return (50, 50, 50) 
        
    def get_colors(self):
        return {
            1: (100, 160, 230),  
            2: (125, 190, 155),  
            3: (240, 200, 80),
            4: (235, 115, 115),  
            5: (128, 0, 128),
            0: (30, 30, 30)
        }
        
