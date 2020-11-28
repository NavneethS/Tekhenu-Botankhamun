import random

GOD_ORDER = ['Horus', 'Ra', 'Hathor', 'Bastet', 'Thoth', 'Osiris']
TOTAL_BUILDINGS, TOTAL_PILLARS, TOTAL_STATUES = 10, 8, 6
BOT_BASE_ACTIONS = [
    "Horus", "Ra", "Hathor", "Bastet", "Thoth", "Osiris",
    "Granite/Limestone/Bread/Papyrus", "Papyrus/Bread/Limestone/Granite", 
    "Limestone/Granite/Papyrus/Bread", "Bread/Papyrus/Granite/Limestone"
]
LIGHTING = {
    "Limestone": {"Sunny":"Pure", "Shaded":"Tainted", "Dark":"Forbidden"},
    "Papyrus": {"Sunny":"Tainted", "Shaded":"Pure", "Dark":"Forbidden"},
    "Granite": {"Sunny":"Forbidden", "Shaded":"Tainted", "Dark":"Pure"},
    "Bread": {"Sunny":"Forbidden", "Shaded":"Pure", "Dark":"Tainted"},
    "Gray": {"Sunny":"Tainted", "Shaded":"Tainted", "Dark":"Tainted"},
}

class Game(object):
    def __init__(self, difficulty, horus_order, first_sunny, starting_dice):
        
        self.horus_order = horus_order #1..6
        self.available_dice = self.assign_polarity(starting_dice, first_sunny)
        print("Dice polarity assigned: {}\n".format(self.available_dice))
       
        self.built_statues = {
            "Horus": None, "Ra": None, 
            "Hathor": None, "Bastet": None, 
            "Thoth": None, "Osiris": None,
            "Papyrus_Bread": None, "Limestone_Granite": None,
            "Temple_Horizontal": None, "Temple_Vertical": None
        } #{None, Bot, Player}

        self.possible_bot_actions = [
            [0,1,2,3], [0,1,2,6], [0,1,5,6], [0,1,5,8],
            [0,4,5,6], [0,4,5,8], [0,4,7,8], [0,4,7,9]
        ]

        self.built_osiris_buildings = {
            "Papyrus": [None, None, None, None, None, None], #{None, Bot, Player}
            "Bread": [None, None, None, None, None, None],
            "Limestone": [None, None, None, None, None, None],
            "Granite": [None, None, None, None, None, None],
        }

        self.built_temple_buildings = {
            "Horizontal": [None, None, None, None, None], #{None, Bot, Player}
            "Vertical": [None, None, None, None, None] #{None, Bot, Player}
        }

        self.built_temple_pillars = [
            [None, None, None, None, None], #{None, Bot, Player)}
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
        ]
        
        self.number_built_buildings = 0
        self.number_built_pillars = 0
        self.number_built_statues = 0
        self.happiness = 4
        self.population = 7
        self.player_order = ["Bot", "Player"]
        self.bot_actions = random.choice(self.possible_bot_actions)
        
        self.destiny = random.choice(["Gold", "Scribe"])
        print("Bot starts with {} Destiny Card\n".format(self.destiny))
        
        self.build_statue(1)
        
        if difficulty=="Medium":
            self.build_osiris_building(5, "Bread")
            self.build_osiris_building(5, "Granite")
            self.build_pillar(None, setup=True)     
            
    
    def build_statue(self, value):
        if self.number_built_statues==TOTAL_STATUES:
            print("Cannot build more statues\n")
            return
        
        god = self.horus_order[value-1]
        if not self.built_statues[god]:
            self.built_statues[god] = "Bot"
        else:
            #TODO
            pass

        self.number_built_statues += 1
        print("Bot builds it's {}th statue on {}".format(self.number_built_statues, god))
        print("All statues built are {}\n".format(self.built_statues))
        
        
    def build_osiris_building(self, value, resource=None):
        if self.number_built_buildings==TOTAL_BUILDINGS:
            print("Cannot build more buildings\n")
            return
        
        if resource:
            self.built_osiris_buildings[resource][value-1] = "Bot" #TODO: occupied?
        else:
            #TODO
            pass
        
        self.number_built_buildings += 1
        print("Bot builds it's {}th building on Osiris {}, {}".format(
            self.number_built_buildings, resource, value))
        print("All Osiris buildings built are {}\n".format(self.built_osiris_buildings))
    
              
    def build_pillar(self, value, setup=False):
        if self.number_built_pillars==TOTAL_PILLARS:
            print("Cannot build more pillars\n")
            return
        
        if setup:
            row,col = 2,2
            self.built_temple_pillars[row][col] = "Bot"

        
        self.number_built_pillars += 1
        print("Bot builds it's {}th pillar on {},{}".format(
            self.number_built_pillars,row, col))
        print("All pillars built are {}\n".format(self.built_temple_pillars))
        
    def assign_polarity(self, dice, first_sunny):
        start = GOD_ORDER.index(first_sunny)
        sunny_gods = GOD_ORDER[start%6], GOD_ORDER[(start+1)%6]
        shaded_gods = GOD_ORDER[(start+2)%6], GOD_ORDER[(start+3)%6]
        dark_gods = GOD_ORDER[(start+4)%6], GOD_ORDER[(start+5)%6]
        
        available_dice = {} 
        #Eg: {"Horus": {"Forbidden": [("granite",3)], "Pure": [("gray",6), ("limestone",1)] ... }}}
                       
        for god in dice:
            available_dice[god] = {"Forbidden": [], "Pure": [], "Tainted": []}
            for d in dice[god]:
                if god in sunny_gods:
                    key = "Sunny"
                elif god in shaded_gods:
                    key = "Shaded"
                elif god in dark_gods:
                    key = "Dark"
                
                polarity = LIGHTING[d[0]][key]
                available_dice[god][polarity].append(d)
        return available_dice
                    
        
        

    def player_turn(self, round_number):
        print("Round {}, Player turn".format(round_number))

        # Get dice selection and remove from pool
        while True:    
            dice_selection = tuple(input("Which dice is Player selecting (God Polarity Color Number)?: ").split(" "))
        
            #Delete from selection
    
            try:
                god, polarity, dice = dice_selection[0], dice_selection[1], tuple([dice_selection[2], int(dice_selection[3])])
                self.available_dice[god][polarity].remove(dice)
            except (KeyError, ValueError, IndexError):
                print("Selected dice not available. Try again\n")
                continue
            
            print("Available dice: {}".format(self.available_dice))
            break
    
        # Get input for board state changes
        while True:
            command = input("Which board state changed (Statue / Pillar / Temple_Building / Osiris_Building / Stop)?: ")
            if command=="Stop":
                break

            elif command=="Statue":
                location = input("Where did Player build statue (God / Papyrus_Bread / Limestone_Granite / Temple_Horizontal / Temple_Vertical?: ")
                try:
                    assert not self.built_statues[location]
                    self.built_statues[location] = "Player"
                    print("All statues built are {}\n".format(self.built_statues))
                except (AssertionError, KeyError):
                    print("Statue already exists, or wrong location. Try again\n")
                    continue
            
            elif command=="Pillar":
                location = input("Which row and col did Player build pillar (row col)?: ").split(" ")
                try:
                    row, col = int(location[0]), int(location[1])
                    assert not self.built_temple_pillars[row][col]
                    self.built_temple_pillars[row][col] = "Player"
                    print("All pillars built are {}\n".format(self.built_temple_pillars))
                except (AssertionError, IndexError):
                    print("Pillar already exists, or wrong location. Try again\n")
                    continue
            
            elif command=="Temple_Building":
                location = input("Where did Player build temple building (Horizontal/Vertical row/col)?: ").split(" ")
                try:
                    side, rowcol = location[0], int(location[1])
                    assert not self.built_temple_buildings[side][rowcol]
                    self.built_temple_buildings[side][rowcol] = "Player"
                    print("All temple buildings built are {}\n".format(self.built_temple_buildings))
                except (AssertionError, KeyError, IndexError):
                    print("Building already exists, or wrong location. Try again\n")
                    continue

            elif command=="Osiris_Building":
                location = input("Where did Player build osiris building (Papyrus/Bread/Limestone/Granite 1-6)?: ").split(" ")
                try:
                    resource, row = location[0], int(location[1])-1
                    assert not self.built_osiris_buildings[resource][row]
                    self.built_osiris_buildings[resource][row] = "Player"
                    print("All Osiris buildings built are {}\n".format(self.built_osiris_buildings))
                except (AssertionError, KeyError, IndexError):
                    print("Building already exists, or wrong location. Try again\n")
                    continue

            else:
                print("Wrong board state command. Try again\n")
                continue

        print("Player turn done")


        
    def bot_turn(self, round_number):
        #TODO
        print("Round {}, Bot turn".format(round_number))
        

    def game_loop(self):
        round_number = 1
        while round_number<=16:
            if self.player_order[0] == "Player":
                self.player_turn(round_number)
                self.bot_turn(round_number)
            elif self.player_order[0] == "Bot":
                self.bot_turn(round_number)
                self.player_turn(round_number)
            
            #TODO
            if round_number%2==0:
                # move wheel
                if round_number%4==0:
                    # evaluate balance
                    # reassign turn order
                    if round_number%8==0:
                        # osiris buildings
                        # temple complex
                        # statues
                        # happiness
                        # buildings
                        if round_number%16==0:
                            # decrees
                            # turn order VPs
                            pass
                    # return 8 dice
                    # take destiny card
                    
                # add 4 dice
                # reassign

                
        

            round_number += 1


# Driver loop
game = Game(
    difficulty="Medium", 
    horus_order=['Horus', 'Ra', 'Hathor', 'Bastet', 'Thoth', 'Osiris'],
    first_sunny="Horus",
    starting_dice={
        'Horus': [("Granite",5), ("Limestone",3), ("Limestone",3)], 
        'Ra': [("Gray",1), ("Granite",2), ("Papyrus",3)], 
        'Hathor': [("Bread",3), ("Papyrus",5), ("Granite",4)], 
        'Bastet':[("Bread",2), ("Papyrus",2), ("Gray",5)], 
        'Thoth':[("Limestone",5 ), ("Limestone",5 ), ("Gray",3 )], 
        'Osiris':[("Gray",3 ), ("Gray",6 ), ("Granite",5 ) ]
    }
)
game.game_loop()