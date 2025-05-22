import json
import os

class Board:
    
    #in the following list:
    #the number 1 = blue
    #the number 2 = green
    #the number 3 = yellow
    #the number 4 = red 
    
    
    #then the second number represent the player 
    #0 if there is no player on the case
    #1 for player 1
    #2 for player 2
    
    #exemple:
    # red case with a pawn of player 1 = 41
    # red case with a pawn of player 2 = 42
    # yellow case with a pawn of player 1 = 31
    # red case with no player = 40
    
    
    #finally
    #the number 5 = a corner
    
    #exemple:
    #a corner with no pawn = 50
    #a corner with a pawn of player 1 = 51
               
    def __init__(self):

        self.__square_list = {
            "default1": [
                [40, 10, 10, 40],
                [10, 10, 40, 30],
                [30, 10, 40, 10],
                [40, 40, 10, 40]
            ],
            "default2": [
                [20, 20, 30, 30],
                [10, 40, 40, 10],
                [10, 30, 20, 20],
                [40, 10, 10, 40]
            ],
            "default3": [
                [10, 10, 10, 10],
                [20, 20, 20, 20],
                [30, 30, 30, 30],
                [40, 40, 40, 40]
            ],
            "default4": [
                [40, 30, 20, 10],
                [10, 20, 30, 40],
                [40, 30, 20, 10],
                [10, 20, 30, 40]
            ]            
        }

        self.final_board = None

        self.__default_board = [[0 for _ in range(8)] for _ in range(8)]

        self.__default_square = [[0 for _ in range(4)] for _ in range(4)]

        self.__corners = [0 for _ in range(4)]


    #saves the board in a json file
    def save_to_file(self, filename: str):
        data_to_save = {
            "square": self.__square_list
        }

        with open(filename, "w") as f:
            json.dump(data_to_save, f, indent=4)

        print(f"Données sauvegardées dans '{filename}'.")

    def check_or_create_file(self, filename: str):
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("")
            print(f"Fichier '{filename}' créé car il n'existait pas.")
            return False

        if os.path.getsize(filename) == 0:
            print(f"Le fichier '{filename}' est vide.")
            return False
        else:
            print(f"Le fichier '{filename}' existe déjà et contient des données.")
            return True
        
    def load_from_file(self, filename: str):
        if not self.check_or_create_file(filename):
            return  # Ne rien faire si le fichier n'existe pas ou est vide

        with open(filename, "r") as f:
            try:
                data = json.load(f)
                self.__square_list = {k: v for k, v in data.get("square", {}).items()}
                self.__board_list = {k: v for k, v in data.get("board", {}).items()}
                print(f"Données chargées depuis '{filename}'.")
            except json.JSONDecodeError:
                print(f"Erreur de lecture : le fichier '{filename}' n'est pas un JSON valide.")
                
    def create_final_board(self, matrix_8x8):
        if len(matrix_8x8) != 8 or any(len(row) != 8 for row in matrix_8x8):
            raise ValueError("Le tableau doit être une matrice 8x8.")

        self.final_board = [row[:] for row in matrix_8x8]
        
        return [row[:] for row in matrix_8x8]
    
    def add_border_and_corners(self,board):
        cols = len(board[0])

        new_board = [[0] + row + [0] for row in board]

        zero_row = [0] * (cols + 2)
        new_board.insert(0, zero_row[:])
        new_board.append(zero_row[:])

        new_board[0][0] = 50                   # top-left
        new_board[0][-1] = 50                  # top-right
        new_board[-1][0] = 60                  # bottom-left
        new_board[-1][-1] = 60                 # bottom-right

        return new_board

    
    

    
    #getter and setter for the board
    def get_default_board(self):
        return self.__default_board
    
    def get_default_square(self):
        return self.__default_square
    
    def set_square_list(self, clef: str, valeur: list):
        if isinstance(clef, str) and isinstance(valeur, list):
            self.__square_list[clef] = valeur
        else:
            print("Erreur : La clé doit être une chaîne de caractères et la valeur une liste.")

    def get_square_list(self):
        return self.__square_list
    
    def rotate_right(self, board):
        return [list(reversed(col)) for col in zip(*board)]
    
    def rotate_left(self, board):
        return [list(col) for col in zip(*board)][::-1]
    
    def flip_horizontal(self, board):
        return [row[::-1] for row in board]
    




   

    
