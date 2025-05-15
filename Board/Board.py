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

        self.__square_list = {}

        self.__board = {}

        self.__default_board = [[0 for _ in range(8)] for _ in range(8)]

        self.__default_square = [[0 for _ in range(4)] for _ in range(4)]

        self.__corners = [0 for _ in range(4)]


    #saves the board in a json file
    def save_to_file(self, filename: str):
        # Charger les anciennes données s’il y en a
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, "r") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        # On récupère la partie "square" existante, ou on part d’un dict vide
        existing_square = existing_data.get("square", {})

        # Mise à jour des données (merge, remplace si même clé)
        for k, v in self.__square_list.items():
            existing_square[k] = v

        # Construction des données à sauvegarder
        data_to_save = {
            "square": existing_square
        }

        # Sauvegarde dans le fichier (en écrasant le fichier, mais avec fusion des anciennes + nouvelles données)
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




   

    
