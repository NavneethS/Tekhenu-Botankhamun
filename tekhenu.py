import math
import random
from itertools import product

"""
TODO:
- Cleanup spacing and prompts
- Print the dice better, and on every turn
- Comments
- Move dice init to use add_dice
- One line commands 

DONE:
- Base board state storage
- Setup
- Player prompts for turn and state changes
- Bot action selection loop
- Rotation, Maat, Scoring and End
- Horus
- Ra
- Hathor
- Bastet
- Thoth
- Osiris
"""

TOTAL_BUILDINGS, TOTAL_PILLARS, TOTAL_STATUES = 10, 8, 6

GOD_ORDER = ['Horus', 'Ra', 'Hathor', 'Bastet', 'Thoth', 'Osiris']

# Pyramid tiles
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

# If pyramid looks like 0123/456/78/9, these are the 4 action orders possible
POSSIBLE_BOT_ACTIONS = [
    [0,1,2,3], [0,1,2,6], [0,1,5,6], [0,1,5,8],
    [0,4,5,6], [0,4,5,8], [0,4,7,8], [0,4,7,9],
]

OSIRIS_ORDER = ['Papyrus', 'Bread', 'Limestone', 'Granite']


class Game(object):
    def __init__(self, difficulty, horus_order, first_sunny, starting_dice):
        """
        Board state setup and bot init
        Params:
          - difficulty (str): {Easy, Medium, Hard}
          - horus_order (list): 6 Gods in order from 1-6 on Horus
          - first_sunny (str): {Horus ... Osiris} starting sunny God
          - starting_dice (dict): {god: [(color, value) ... ] ..} starting dice on the board. 3 per God.
        """
        self.horus_order = horus_order 
        self.first_sunny = first_sunny 
        
        # god: [(color, value) ... ] ..}
        self.starting_dice = starting_dice  

        self.available_dice = self.assign_polarity() 
        # {
        #   god: {
        #     "Forbidden": [(color, value) ... ], 
        #     "Pure": [(color, value) ... ], 
        #     "Tainted": [(color, value) ... ]
        #   } 
        #   ...
        # }
       
        self.built_statues = {
            "Horus": None, "Ra": None, 
            "Hathor": None, "Bastet": None, 
            "Thoth": None, "Osiris": None,
            "Papyrus_Bread": None, "Limestone_Granite": None,
            "Temple_Horizontal": None, "Temple_Vertical": None
        } #One of {None, Bot, Player}

        self.built_osiris_buildings = {
            "Papyrus": [None, None, None, None, None, None], 
            "Bread": [None, None, None, None, None, None],
            "Limestone": [None, None, None, None, None, None],
            "Granite": [None, None, None, None, None, None],
        } #One of {None, Bot, Player}

        self.built_temple_buildings = {
            "Horizontal": [None, None, None, None, None], 
            "Vertical": [None, None, None, None, None], 
        } #One of {None, Bot, Player} 

        self.built_temple_pillars = [
            [None, None, None, None, None], 
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
        ] #One of {None, Bot, Player}
        
        self.vps = 0
        self.scribes = 0
        self.number_built_buildings = 0
        self.number_built_pillars = 0
        self.number_built_statues = 0
        self.happiness = 4
        self.population = 7
        self.blessings = 0
        self.technologies = 0
        self.decrees = 0
        self.player_order = ["Bot", "Player"]
        
        print("Bot starts with {} Destiny Card\n".format(random.choice(["Gold", "Scribe"])))
        
        self.build_statue(1)
        
        if difficulty=="Medium" or difficulty=="Hard":
            self.build_osiris_building(5, "Bread")
            self.build_osiris_building(5, "Granite")
            self.build_pillar(None, setup=True)     
        
        if difficulty=="Hard":
            self.build_statue(4)
        
        self.bot_pyramid = random.sample(BOT_BASE_ACTIONS, 10)
        print("Bot action pyramid is:\n {}\n{}\n{}\n{}".format(
            [self.bot_pyramid[9]], self.bot_pyramid[7:9], self.bot_pyramid[4:7], self.bot_pyramid[0:4]
            )
        )
        self.bot_actions = random.choice(POSSIBLE_BOT_ACTIONS)
        print("Debug. Bot actions order {}".format(self.bot_actions))
            
    def build_statue(self, value):
        """
        Build a statue following Horus action logic with die value.

        Build on God. If occupied, build on biggest impact Osiris. If none, build on Temple with most pillars. Score 3VPs if still not possible.

        Params:
          - value (int): 1-6
        Returns:
          - boolean. True if succesfully built, False otherwise
        """
        if self.number_built_statues==TOTAL_STATUES:
            print("Cannot build more statues\n")
            return False
        
        god = self.horus_order[value-1]
        if self.built_statues[god] == None:
            # If god spot free, build there
            key = god
            self.built_statues[key] = "Bot"
        else:
            # Calculate which Osiris row has most impact in terms of ownership change
            impacts = {}
            for group in random.sample([("Papyrus", "Bread"), ("Limestone", "Granite")], 2):
                impact = 0
                for region in group:
                    statue = [self.built_statues[r] for r in self.built_statues if region in r][0]
                    if statue == None:
                        new_winner, _, _ = self.osiris_building_scoring(region, "Bot")
                        old_winner, _, _ = self.osiris_building_scoring(region, None)
                        if new_winner!=old_winner:
                            impact += 1
                impacts[group] = impact

            if impacts:        
                # Build on spot with max impact. If tied, pick randomly since we randomized the order when examining.             
                best_region = max(impacts, key=lambda x: impacts[x])
                impact = impacts[best_region]
                if impact>0:
                    key = "_".join(best_region)
                    self.built_statues[key] = "Bot"

            if not impacts or impact==0:
                # Either no impact or both Osiris occupied. Look at Temple next.
                horizontal_pillars, vertical_pillars = 0,0 
                if self.built_statues["Temple_Horizontal"] == None:
                    horizontal_pillars = [self.built_temple_pillars[2][x] for x in range(5)].count("Bot")
                if self.built_statues["Temple_Vertical"] == None:
                    vertical_pillars = [self.built_temple_pillars[x][2] for x in range(5)].count("Bot")
                
                # Build on row/col with more pillars. 
                if horizontal_pillars>vertical_pillars:
                    key = "Temple_Horizontal"
                    self.built_statues[key] = "Bot"
                    print("Bot scores {} VPs for Pillars".format(3*horizontal_pillars))
                    self.vps += 3*horizontal_pillars
                elif horizontal_pillars<vertical_pillars:
                    key = "Temple_Vertical"
                    self.built_statues[key] = "Bot"
                    print("Bot scores {} VPs for Pillars".format(3*vertical_pillars))
                    self.vps += 3*vertical_pillars
                    
                # Both equal. Pick randomly
                elif horizontal_pillars!=0:
                    key = random.choice(["Temple_Horizontal", "Temple_Vertical"])
                    self.built_statues[key] = "Bot"
                    vps = 3*horizontal_pillars if key=="Temple_Horizontal" else 3*vertical_pillars
                    print("Bot scores {} VPs for Pillars".format(vps))
                    self.vps += vps
                
                # Both Temple occupied
                else:
                    print("All Statues occupied. Bot scores 3 VP")
                    self.vps += 3
                    return False
                

        self.number_built_statues += 1
        print("Bot builds it's {}th statue on {}".format(self.number_built_statues, key))
        print("All statues built are {}\n".format(self.built_statues))
        return True
               
    def build_osiris_building(self, value, resource=None):
        """
        Build an Osiris Building following Osiris action logic with die value and resource.

        Build on spot referenced by resource, value. If occupied, cycle through resources first and values descending next.

        Params:
          - value (int), resource (str): 1-6, One of {Papyrus, .. Granite}
        Returns:
          - boolean. True if succesfully built, False otherwise
        """

        if self.number_built_buildings==TOTAL_BUILDINGS:
            print("Cannot build more buildings\n")
            return False
        
        start = OSIRIS_ORDER.index(resource)
        resource_order = OSIRIS_ORDER[start:] + OSIRIS_ORDER[:start] #to cycle through the order
        start = list(range(5,-1,-1)).index(value-1)
        value_order = list(range(5,-1,-1))[start:] + list(range(5,-1,-1))[:start]

        for value, resource in product(value_order, resource_order):
            if self.built_osiris_buildings[resource][value] == None:
                break

        self.built_osiris_buildings[resource][value] = "Bot"
        self.number_built_buildings += 1
        print("Bot builds it's {}th building on Osiris {}, {}".format(
            self.number_built_buildings, resource, value+1))
        print("All Osiris buildings built are {}\n".format(self.built_osiris_buildings))
        return True
             
    def build_pillar(self, value, setup=False):
        """
        Build a Pillar following Ra action logic with die value.

        Build on spot with most VPs gain. If multiple, pick most inline with Temple Buildings. Random if still tied.

        Params:
          - value (int), setup (bool): 1-6. Set to true to seed board with pillar on 2,2 without scoring VPs
        Returns:
          - boolean. True if succesfully built, False otherwise
        """

        if self.number_built_pillars==TOTAL_PILLARS:
            print("Cannot build more pillars\n")
            return False
        
        if setup:
            final_row, final_col = 2,2
            max_vps = 0
            self.built_temple_pillars[final_row][final_col] = "Bot"

        else:
            base_vps = math.ceil(value/2)
            possible_vps = {}
            for r in range(5):
                for c in range(5):
                    # Sum up VPs from any buildings and from all neighbors
                    if self.built_temple_pillars[r][c]==None:
                        vps = 0
                        vps += 1 if self.built_temple_buildings["Horizontal"][r] else 0
                        vps += 1 if self.built_temple_buildings["Vertical"][c] else 0
                        
                        def get_neighbors(r,c):
                            top = True if r==0 else bool(self.built_temple_pillars[r-1][c])
                            bottom = True if r==4 else bool(self.built_temple_pillars[r+1][c])
                            left = True if c==0 else bool(self.built_temple_pillars[r][c-1])
                            right = True if c==4 else bool(self.built_temple_pillars[r][c+1])
                            return [top, bottom, left, right].count(True)

                        vps += get_neighbors(r,c)
                        possible_vps[(r,c)] = vps+base_vps
            
            best_spot = max(possible_vps, key=lambda x: possible_vps[x])
            max_vps = possible_vps[best_spot]
            candidates = [(r,c) for r,c in possible_vps if possible_vps[(r,c)]==max_vps]
            # Pick the best VPS
            if len(candidates)==1:
                final_row, final_col = candidates[0]
            else:
                # If multiple max VPs, pick the one with most Bot buildings
                shortlist = [(r,c) for r,c in candidates if self.built_temple_buildings['Horizontal'][r]=="Bot" or self.built_temple_buildings['Vertical'][c]=="Bot"]
                if not shortlist:
                    shortlist = candidates
                if len(candidates)==1:
                    final_row, final_col = shortlist[0]
                else:
                    # If multiple bot buildings, pick the one closer to center:
                    # 0 1 1 1 0
                    # 1 2 3 2 1 
                    # 1 3 4 3 1
                    # 1 2 3 2 1
                    # 0 1 1 1 0
                    center_scores = {}
                    for r,c in shortlist:
                        if r==0 or r==4:
                            score = 0
                        elif r==1 or r==3:
                            score = 1
                        else:
                            score = 2
                        if c==0 or c==4:
                            score += 0
                        elif c==1 or c==3:
                            score += 1
                        else:
                            score += 2
                        center_scores[(r,c)] = score
                    
                    best_spot = max(center_scores, key=lambda x: center_scores[x])
                    max_score = center_scores[best_spot]
                    shorterlist = [(r,c) for r,c in center_scores if center_scores[(r,c)]==max_score]
                    if len(shorterlist)==1:
                        final_row, final_col = shorterlist[0]
                    else:
                        # If multiple closest to center, pick random
                        final_row, final_col = random.choice(shorterlist)

        
        self.built_temple_pillars[final_row][final_col] = "Bot"
        print("Bot scores {} VPs for Pillar".format(max_vps))
        self.vps += max_vps

        self.number_built_pillars += 1
        print("Bot builds it's {}th pillar on {},{}".format(
            self.number_built_pillars, final_row, final_col))
        print("All pillars built are {}\n".format(self.built_temple_pillars))
        return True
        
    def build_temple_building(self, value):
        """
        Build a Temple Building following Hathor action logic with die value.

        Build on spot with most VPs gain. Random if tied.

        Params:
          - value (int): 1-6
        Returns:
          - boolean. True if succesfully built, False otherwise
        """

        if self.number_built_buildings==TOTAL_BUILDINGS:
            print("Cannot build more buildings\n")
            return False

        all_pillars = {}
        # Count number of pillars on Horizontal and Vertical lines for all spots.
        for i in range(5):
            if self.built_temple_buildings["Horizontal"][i] == None:
                num_pillars = [self.built_temple_pillars[i][j] for j in range(5)].count("Bot")
                all_pillars[("Horizontal", i)] = num_pillars
            if self.built_temple_buildings["Vertical"][i] == None:
                num_pillars = [self.built_temple_pillars[j][i] for j in range(5)].count("Bot")
                all_pillars[("Vertical", i)] = num_pillars
        
        max_spot = max(all_pillars, key=lambda x: all_pillars[x])
        most_pillars = all_pillars[max_spot]
        candidates = [x for x in all_pillars if all_pillars[x]==most_pillars]
        if len(candidates)==1:
            position, row = candidates[0]
        else:
            position, row = random.choice(candidates)
        vps = 3*most_pillars

        self.number_built_buildings += 1
        self.population += value
        self.vps += vps
        print("Bot scores {} VPs and gains {} Population".format(vps, value))
        self.built_temple_buildings[position][row] = "Bot"
        print("Bot builds it's {}th building on Temple {}, {}".format(
            self.number_built_buildings, position, row))
        print("All Temple buildings built are {}\n".format(self.built_temple_buildings))
        return True

    def assign_polarity(self):
        """
        Based on lighting condition, classify polarity of self.starting_dice. Called on every Rotation Phase.
        Returns: self.available_dice
        """
        dice = self.starting_dice
        start = GOD_ORDER.index(self.first_sunny)
        sunny_gods = GOD_ORDER[start%6], GOD_ORDER[(start+1)%6]
        shaded_gods = GOD_ORDER[(start+2)%6], GOD_ORDER[(start+5)%6]
        dark_gods = GOD_ORDER[(start+3)%6], GOD_ORDER[(start+4)%6]
        
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
                    
    def statue_bonus(self, god):
        """
        Horus rewards for bot. VP, Scribe or both. Depends on randomized Horus order.
        """
        god_pos = self.horus_order.index(god)
        if 0<=god_pos<=1:
            self.scribes += 1
            print("Bot has statue on {}. Bot collects 1 scribe".format(god))
        elif 2<=god_pos<=3:
            self.vps += 1
            print("Bot has statue on {}. Bot collects 1 VP".format(god))
        elif 4<=god_pos<=5:
            self.scribes += 1
            self.vps += 1
            print("Bot has statue on {}. Bot collects 1 scribe and 1 VP".format(god))
        return 

    def player_turn(self, round_number):
        """
        User input loop to accept die selection, and board state changes. Board state changes loop till "Stop" user input.
        Retry on incorrect input.

        Params:
          - round_number (int): 1-16

        """
        print("Round {}, Player turn".format(round_number))
        print("Available dice:")
        self.print_dice()

        # Get dice selection and remove from pool
        while True:    
            dice_selection = tuple(input("Which dice is Player selecting (God Polarity Color Number)?: ").split(" "))
        
            #Delete from selection
            try:
                god, polarity, dice = dice_selection[0], dice_selection[1], tuple([dice_selection[2], int(dice_selection[3])])
                self.available_dice[god][polarity].remove(dice)
                self.starting_dice[god].remove(dice)
                #Statue bonus check
                if self.built_statues[god]=="Player": 
                    print("Player has statue on {}. Collect bonus.\n".format(god))
                elif self.built_statues[god]=="Bot":
                    self.statue_bonus(god)

            except (KeyError, ValueError, IndexError):
                print("Selected dice not available. Try again\n")
                continue
            
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
        return True
  
    def bot_turn(self, round_number):
        """
        Main bot action selection according to pyramid. 
        
        For god action, evaluate highest available dice. Pure if tied. Random otherwise. Move to next God if None.
        For resource action, evaluate highest dice of that color. Statue if tied. Highest if multuple. Random if no statue. Next color if none.
        
        Params:
          - round_number (int): 1-16
        """

        print("Round {}, Bot turn".format(round_number))
        print("Available dice:")
        self.print_dice()

        action_number = self.bot_actions[(round_number-1)%4]
        action = self.bot_pyramid[action_number]

        def god_die_pick(god):
            # pick highest pure/tainted
            candidates = {polarity:dice for polarity,dice in self.available_dice[god].items() if polarity!="Forbidden"}
            shortlist = {}
            polarity, final_pick = None, None
            maxval = -999
            for polarity, dice in candidates.items():
                for d in dice:
                    maxval = max(maxval, d[1])
            
            for polarity, dice in candidates.items():
                shortlist[polarity] = []
                for d in dice:
                    if d[1]==maxval:
                        shortlist[polarity].append(d)
            
            if shortlist["Pure"]:
                polarity, final_pick = "Pure", random.choice(shortlist["Pure"])
            elif shortlist["Tainted"]:
                polarity, final_pick = "Tainted", random.choice(shortlist["Tainted"])

            return polarity, final_pick

        def color_die_pick(color):
            # pick highest of that color
            maxval = -999
            for god, polarities in self.available_dice.items():
                for polarity, dice in polarities.items():
                    for d in dice:
                        if d[0]==color and polarity!="Forbidden":
                            maxval = max(maxval, d[1])                
            
            candidates = []
            for god, polarities in self.available_dice.items():
                for polarity, dice in polarities.items():
                    for d in dice:
                        if d[0]==color and d[1]==maxval and polarity!="Forbidden":
                            candidates.append((god, polarity, d))
            
            if len(candidates)==1:
                return candidates[0]
            elif len(candidates)==0:
                return None, None, None
            else:
                shortlist = [x for x in candidates if self.built_statues[x[0]]=="Bot"]
                print("SL", shortlist)
                if shortlist:
                    for god in self.horus_order[::-1]:
                        for x in shortlist:
                            if x[0]==god:
                                return x
                else:
                    return random.choice(candidates)

            
        if action in GOD_ORDER:
            activated_god = action
            while True:
                polarity, die_pick = god_die_pick(activated_god)
                if die_pick:
                    break
                else:         
                    current = GOD_ORDER.index(activated_god)
                    activated_god = GOD_ORDER[(current-1)%6]
                    continue

        else:
            colors = action.split('/')
            i=0
            while True:
                activated_god, polarity, die_pick = color_die_pick(colors[i])
                if die_pick:
                    break
                else:
                    i+=1
                    continue

        print("Bot selects action {} :: {} {} {} {}\n".format(action, activated_god, polarity, die_pick[0], die_pick[1]))
        self.available_dice[activated_god][polarity].remove(die_pick)
        self.starting_dice[activated_god].remove(die_pick)
        #Statue bonus check
        if self.built_statues[activated_god]=="Player": 
            print("Player has statue on {}. Collect bonus.\n".format(activated_god))
        elif self.built_statues[activated_god]=="Bot":
            self.statue_bonus(activated_god)

        self.do_bot_action(activated_god, die_pick[0], die_pick[1])

    def do_bot_action(self, activated_god, color, value):
        """
        Evaluate the bot action with the selection
        Params:
          - activated_god (str): {Horus ... Osiris}
          - color (str): {Papyrus ... Granite}
          - value (int): 1-6
        """
        if activated_god == "Horus":
            self.build_statue(value)

        elif activated_god == "Ra":
            self.build_pillar(value)

        elif activated_god == "Hathor":
            self.build_temple_building(value)
        
        elif activated_god == "Bastet":
            if value==1 or value==2:
                scribes_gained = 2
            elif value==3 or value==4:
                scribes_gained = 1
            else:
                scribes_gained = 0
            self.scribes += scribes_gained
            while value:
                if self.happiness<self.population:
                    self.happiness += 1
                else:
                    self.population += 1
                value -= 1
            print("Bot Happiness={}, Population={}, {} Scribes gained".format(self.happiness, self.population, scribes_gained))

        elif activated_god == "Thoth":
            number_cards = math.ceil(value/2)
            if self.happiness<=4:
                zone = "yellow"
                if number_cards==1:
                    dec, tech, bless = 0,1,0
                if number_cards==2:
                    dec, tech, bless = 0,1,1                    
                if number_cards==3:
                    dec, tech, bless = 0,1,2

            elif self.happiness<=8:
                zone = "red"
                if number_cards==1:
                    dec, tech, bless = 0,1,0
                if number_cards==2:
                    dec, tech, bless = 0,2,0                    
                if number_cards==3:
                    dec, tech, bless = 0,2,1

            elif self.happiness<=12:
                zone = "green"
                if number_cards==1:
                    dec, tech, bless = 1,0,0
                if number_cards==2:
                    dec, tech, bless = 1,1,0                    
                if number_cards==3:
                    dec, tech, bless = 1,2,0

            else:
                zone = "blue"
                if number_cards==1:
                    dec, tech, bless = 1,0,0
                if number_cards==2:
                    dec, tech, bless = 2,0,0                    
                if number_cards==3:
                    dec, tech, bless = 2,1,0

            self.decrees += dec
            self.technologies += tech
            self.blessings += bless
            print("Bot takes {} Decrees, {} Tech, {} Blessings from {} zone".format(dec, tech, bless, zone))

        elif activated_god == "Osiris":
            if color == "Gray":
                empty_spots = {region: self.built_osiris_buildings[region].count(None) for region in self.built_osiris_buildings}
                most_empty_region = max(empty_spots, key=lambda x: empty_spots[x])
                most_empty = empty_spots[most_empty_region]
                for region in self.built_osiris_buildings:
                    if empty_spots[region]==most_empty:
                        resource = region
                        break
            else:
                resource = color
            self.build_osiris_building(value, resource)

    def osiris_building_scoring(self, region, statue):
        """
        Select winner of the Osiris region.
        Most pieces. Topmost piece if tied.

        Params:
          - region (str): {Papyrus ... Granite}
          - statue (str): {None, Bot, Player}
        Returns:
          - winner (str): {None, Bot, Player}
          - player_count, bot_count (int): Pieces per player
        """
        pieces = [statue] + self.built_osiris_buildings[region]
        bot_count, player_count = pieces.count("Bot"), pieces.count("Player")
        winner = None

        if player_count>bot_count:
            winner = "Player"
        elif player_count<bot_count:
            winner = "Bot"   
        else:
            for piece in pieces:
                if piece:
                    winner = piece
                    break
            
        if not winner:
            assert player_count == 0
            assert bot_count == 0
        
        return winner, player_count, bot_count

    def temple_scoring(self):
        """
        Calculate VPs scored by Player and Bot for Pillars and Temple Buildings
        """
        pieces = self.built_temple_buildings["Horizontal"] + self.built_temple_buildings["Vertical"] + [self.built_statues["Temple_Horizontal"], self.built_statues["Temple_Vertical"]]
        bot_count, player_count = pieces.count("Bot"), pieces.count("Player")
        self.vps += bot_count
        print("Player scores {} VPs. Bot scores {} VPs for Temple Buildings".format(player_count, bot_count))

        def pillar_scoring(who):
            # pillar VPs for Bot/Player
            vps = 0
            for r in range(5):
                for c in range(5):
                    if self.built_temple_pillars[r][c]==who:
                        vps += 1 if self.built_temple_buildings["Horizontal"][r]==who else 0
                        vps += 1 if self.built_temple_buildings["Vertical"][c]==who else 0
                        if r==2:
                            vps += 1 if self.built_statues["Temple_Horizontal"]==who else 0
                        if c==2:
                            vps += 1 if self.built_statues["Temple_Vertical"]==who else 0
            return vps
        
        bot_count, player_count = pillar_scoring("Bot"), pillar_scoring("Player")
        self.vps += bot_count
        print("Player scores {} VPs. Bot scores {} VPs for Temple Pillars".format(player_count, bot_count))

    def statue_scoring(self):
        """
        Statue VPs for Bot. 1/3/6/10...
        """
        statue_vps = int((self.number_built_statues * (1+self.number_built_statues))/2)
        self.vps += statue_vps
        print("Bot scores {} VPs for Statues".format(statue_vps))

    def happiness_scoring(self):
        """
        Happiness VPs for Bot. 3*triangles reached.
        """
        if self.happiness>=21:
            happy_vps = 15
        elif 19<=self.happiness<21:
            happy_vps = 12
        elif 16<=self.happiness<19:
            happy_vps = 9
        elif 13<=self.happiness<16:
            happy_vps = 6
        elif 9<=self.happiness<13:
            happy_vps = 3
        else:
            happy_vps = 0
        
        self.vps += happy_vps
        print("Bot scores {} VPs for Happinness".format(happy_vps))

    def card_scoring(self):
        """
        Card VPs for Bot. 2 per blessing (discard), 2 per tech (keep)
        """
        blessing_vps, tech_vps = 2*self.blessings, 2*self.technologies
        self.vps += blessing_vps+tech_vps
        self.blessings = 0
        print("Bot scored {} VPs for Blessings and {} VPs for Techs".format(blessing_vps, tech_vps))

    def print_dice(self):
        """
        Helper function to pretty print the available dice
        """
        base = ""
        for god in self.available_dice:
            base += "{}\n".format(god)
            for polarity in self.available_dice[god]:
                base += "\t{}\t{}\n".format(polarity[:7], self.available_dice[god][polarity])
        print(base)

    def game_loop(self):
        """
        Main game flow loop to iterate 1-16 rounds. Turns in player order. Trigger Rotation, Maat, Scoring and End when applicable.
        """
        for round_number in range(1,17):
            
            if self.player_order[0] == "Player":
                self.player_turn(round_number)
                self.bot_turn(round_number)
            elif self.player_order[0] == "Bot":
                self.bot_turn(round_number)
                self.player_turn(round_number)
            
            if round_number%2==0:
                # move wheel
                start = GOD_ORDER.index(self.first_sunny)+1
                self.first_sunny = GOD_ORDER[start%6]
                
                if round_number%4==0:
                    print("Maat Phase #{}".format(round_number//4))

                    # Check balance, assign turn order
                    player_balance = int(input("What is the absolute value of Player balance?: "))
                    bot_balance = max(4-(round_number/4), 1) #3,2,1,1
                    if player_balance<bot_balance:
                        print("Player goes first\n")
                        self.player_order = ["Player", "Bot"]
                    else:
                        print("Bot goes first\n")
                        self.player_order = ["Bot", "Player"]
                        print("Bot starts with {} Destiny Card\n".format(random.choice(["Gold", "Scribe"])))

                    # Remake action pyramid
                    self.bot_pyramid = random.sample(BOT_BASE_ACTIONS, 10)
                    print("Bot action pyramid is:\n {}\n{}\n{}\n{}".format(
                        [self.bot_pyramid[9]], self.bot_pyramid[7:9], self.bot_pyramid[4:7], self.bot_pyramid[0:4]
                        )
                    )
                    self.bot_actions = random.choice(POSSIBLE_BOT_ACTIONS)
                    print("Debug. Bot actions order {}".format(self.bot_actions))


                    if round_number%8==0:
                        print("Scoring Phase")

                        for region in self.built_osiris_buildings:
                            statue = [self.built_statues[r] for r in self.built_statues if region in r][0]
                            winner, player_count, bot_count = self.osiris_building_scoring(region, statue)
                            if winner=="Player":
                                print("Player has {} pieces, Bot has {} in Osiris {}. Player scores 3 VPs".format(player_count, bot_count, region))
                            elif winner=="Bot":
                                self.vps += 3
                                print("Player has {} pieces, Bot has {} in Osiris {}. Bot scores 3 VPs".format(player_count, bot_count, region))    
                            else:
                                print("Player has {} pieces, Bot has {} in Osiris {}. Nobody scores 3 VPs".format(player_count, bot_count, region))  


                        self.temple_scoring()
                        self.statue_scoring()     
                        self.happiness_scoring()                   
                        self.card_scoring()
                        print("Scoring summary: Bot scored {} VPs".format(self.vps))

                        if round_number%16==0:
                            # 3 VPs for being first, 4 per decree, 0.5 per scribe
                            to_vps = 0
                            if self.player_order[0]=="Bot":
                                to_vps = 3                    
                            decree_vps = 4*self.decrees
                            scribe_vps = self.scribes//2

                            self.vps += decree_vps+to_vps+scribe_vps
                            print("Bot scored {} VPs for Decrees, {} for Scribes, and {} for Turn Order.".format(decree_vps, scribe_vps, to_vps))
                            print("\nFinal Bot Score: {} VPs".format(self.vps))
                            return
                            
                    
                def add_dice(region):
                    while True:
                        new_dice = input("Which dice to add dice to {} (Color Number)?: ".format(region)).split(" ")
                        try:
                            c,d = new_dice[0], int(new_dice[1])
                            if c not in LIGHTING or d<1 or d>6:
                                print("Invalid new dice. Try Again.")
                                continue
                            self.starting_dice[region].append((c,d))
                            return 
                        except (IndexError, ValueError):
                            print("Invalid new dice. Try Again.")
                            continue
                        
                        
                for shady in [GOD_ORDER[(start+2)%6]]*2 + [GOD_ORDER[(start+5)%6]]*2:
                    add_dice(shady)
                
                self.available_dice = self.assign_polarity()
                self.print_dice()

                print("Round {} Over. Bot has {} VPs".format(round_number, self.vps))

                
# Driver loop
game = Game(
    difficulty="Medium", 
    horus_order=GOD_ORDER,
    first_sunny="Ra",
    starting_dice={
        'Horus': [("Bread",3), ("Granite",5), ("Limestone",3), ("Granite", 6)], 
        'Ra': [("Gray",1), ("Granite",2)], 
        'Hathor': [("Bread",3)], 
        'Bastet':[("Papyrus",6), ("Papyrus",2), ("Gray",1), ("Limestone",1)], 
        'Thoth':[("Limestone",5), ("Gray",3 )], 
        'Osiris':[("Gray",3), ("Gray",2), ("Granite",5), ("Granite",4)]
    }
)
game.game_loop()