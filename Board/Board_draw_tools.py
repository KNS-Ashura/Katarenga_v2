import pygame
import sys

class Board_draw_tools:
        
    def draw_all_corners(self,size):
        
            #DRAW CORNER

            self.draw_corner_top_left(size)
            self.draw_corner_top_right(size)
            self.draw_corner_bot_left(size)
            self.draw_corner_bot_right(size)
            
            #DRAW RECTANGLE

            self.draw_rectangle_left(size)
            self.draw_rectangle_right(size)
            self.draw_rectangle_top(size)
            self.draw_rectangle_bot(size)
    
    def draw_corner_top_left(self,size):
        rect = pygame.Rect(
            20,  # x = collé à gauche
            20,  # y = collé en haut
            60,  # largeur
            60   # hauteur
        )
        pygame.draw.rect(size, (255, 165, 0), rect) 
        pygame.draw.rect(size, (255, 255, 255), rect, 1)  

    def draw_corner_top_right(self,size):
        rect = pygame.Rect(
            560,  
            20,  
            60,  
            60   
        )
        pygame.draw.rect(size, (255, 165, 0), rect)  
        pygame.draw.rect(size, (255, 255, 255), rect, 1)  

    def draw_corner_bot_left(self,size):
        rect = pygame.Rect(
            20,  
            560, 
            60,  
            60   
        )
        pygame.draw.rect(size, (255, 165, 0), rect)  
        pygame.draw.rect(size, (255, 255, 255), rect, 1)  

    def draw_corner_bot_right(self,size):
        rect = pygame.Rect(
            560,  
            560,  
            60,  
            60   
        )

        pygame.draw.rect(size, (255, 165, 0), rect)  
        pygame.draw.rect(size, (255, 255, 255), rect, 1)  

        
    #DRAW RECTANGLE DESIGN KATARENGA

    def draw_rectangle_left(self,size):
        rect = pygame.Rect(
            20, # x = collé à gauche
            80, # y = collé en haut
            60, # largeur
            480 # hauteur
        )

        pygame.draw.rect(size, (100, 65, 0), rect)  
        pygame.draw.rect(size, (255, 255, 255), rect, 1)  

    def draw_rectangle_right(self,size):
        rect = pygame.Rect(
            560,  
            80,  
            60,  
            480 
        )

        pygame.draw.rect(size, (100, 65, 0), rect)  
        pygame.draw.rect(size, (255, 255, 255), rect, 1) 

    def draw_rectangle_top(self,size):
        rect = pygame.Rect(
            80, 
            20, 
            480, 
            60 
        )

        pygame.draw.rect(size, (100, 65, 0), rect)  
        pygame.draw.rect(size, (255, 255, 255), rect, 1) 

    def draw_rectangle_bot(self,size):
        rect = pygame.Rect(
            80, 
            560,  
            480,  
            60 
        )

        pygame.draw.rect(size, (100, 65, 0), rect)  
        pygame.draw.rect(size, (255, 255, 255), rect, 1)  

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
        
