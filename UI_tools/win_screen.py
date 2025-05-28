import tkinter as tk
from tkinter import messagebox
from UI_tools.BaseUi import BaseUI

import pygame
import sys

class WinScreen(BaseUI):
    def __init__(self, player_name):
        super().__init__(title="Victoire")
        self.__player = player_name

        self.button_font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72)
        self.text_font = pygame.font.SysFont(None, 48)

        self.buttons = {
            "menu": pygame.Rect(self.get_width() // 2 - 100, self.get_height() // 2 + 50, 200, 50),
            "quit": pygame.Rect(self.get_width() // 2 - 100, self.get_height() // 2 + 120, 200, 50),
        }

        self.mainloop()

    def draw(self):
        screen = self.get_screen()
        screen.fill((212, 237, 218))

        title_surf = self.title_font.render("Victoire", True, (21, 87, 36))
        screen.blit(title_surf, (self.get_width() // 2 - title_surf.get_width() // 2, 100))

        winner_text = f"Le gagnant est : {self.__player}"
        winner_surf = self.text_font.render(winner_text, True, (21, 87, 36))
        screen.blit(winner_surf, (self.get_width() // 2 - winner_surf.get_width() // 2, 200))

        for key, rect in self.buttons.items():
            pygame.draw.rect(screen, (255, 255, 255), rect)
            pygame.draw.rect(screen, (21, 87, 36), rect, 2)

            text = "Retour au menu" if key == "menu" else "Quitter le jeu"
            text_surf = self.button_font.render(text, True, (21, 87, 36))
            screen.blit(
                text_surf,
                (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2)
            )

        pygame.display.flip()

    def mainloop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.buttons["menu"].collidepoint(mouse_pos):
                        print("Retour au menu...")
                        self.running = False
                    elif self.buttons["quit"].collidepoint(mouse_pos):
                        print("Jeu quitté.")
                        pygame.quit()
                        sys.exit()

            self.draw()
            self.clock.tick(60)