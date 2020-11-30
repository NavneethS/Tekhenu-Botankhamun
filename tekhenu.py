import random

"""
9
7 8
4 5 6
0 1 2 3

TODO:
- Cleanup spacing and prompts
- Print the dice better, and on every turn
- Comments
- Move dice init to use add_dice
- One line commands 
- Bot god actions

WORKS:
- Base board state storage
- Setup
- Player prompts for turn and state changes
- Bot action selection loop
- Rotation, Maat, Scoring and End
"""

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
POSSIBLE_BOT_ACTIONS = [
    [0,1,2,3], [0,1,2,6], [0,1,5,6], [0,1,5,8],
    [0,4,5,6], [0,4,5,8], [0,4,7,8], [0,4,7,9],
]


class Game(object):
    def __init__(self, difficulty, horus_order, first_sunny, starting_dice):
        
        self.horus_order = horus_order #1..6
        self.first_sunny = first_sunny
        self.starting_dice = starting_dice
        self.available_dice = self.assign_polarity()
       
        self.built_statues = {
            "Horus": None, "Ra": "Player", 
            "Hathor": None, "Bastet": None, 
            "Thoth": "Bot", "Osiris": "Bot",
            "Papyrus_Bread": None, "Limestone_Granite": "Player",
            "Temple_Horizontal": "Player", "Temple_Vertical": None
        } #{None, Bot, Player}

        self.built_osiris_buildings = {
            "Papyrus": [None, None, None, None, None, None], #{None, Bot, Player}
            "Bread": [None, None, None, None, None, "Player"],
            "Limestone": [None, None, "Player", None, None, "Player"],
            "Granite": [None, None, None, None, None, None],
        }

        self.built_temple_buildings = {
            "Horizontal": [None, "Player", "Player", None, None], #{None, Bot, Player}
            "Vertical": ["Player", None, "Bot", None, None] #{None, Bot, Player}
        }

        self.built_temple_pillars = [
            [None, "Player", None, None, None], #{None, Bot, Player)}
            [None, "Player", "Bot", None, None],
            ["Player", "Player", None, None, None],
            [None, None, None, None, None],
            ["Player", None, None, None, None],
        ]
        
        self.vps = 0
        self.scribes = 0
        self.number_built_buildings = 1
        self.number_built_pillars = 1
        self.number_built_statues = 2
        self.happiness = 18
        self.population = 21
        self.blessings = 4
        self.technologies = 2
        self.decrees = 12
        self.player_order = ["Bot", "Player"]
        
        print("Bot starts with {} Destiny Card\n".format(random.choice(["Gold", "Scribe"])))
        
        self.build_statue(1)
        
        if difficulty=="Medium":
            self.build_osiris_building(5, "Bread")
            self.build_osiris_building(5, "Granite")
            self.build_pillar(None, setup=True)     
        
        self.bot_pyramid = random.sample(BOT_BASE_ACTIONS, 10)
        print("Bot action pyramid is:\n {}\n{}\n{}\n{}".format(
            [self.bot_pyramid[9]], self.bot_pyramid[7:9], self.bot_pyramid[4:7], self.bot_pyramid[0:4]
            )
        )
        self.bot_actions = random.choice(POSSIBLE_BOT_ACTIONS)
        print("Debug. Bot actions order {}".format(self.bot_actions))
            
    
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
        
    def assign_polarity(self):
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
                    
    def player_turn(self, round_number):
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
                    
                    god_pos = self.horus_order.index(god)
                    # 01 23 45
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
  
    def do_bot_action(self, activated_god):
        #TODO
        pass

    def bot_turn(self, round_number):
        print("Round {}, Bot turn".format(round_number))
        print("Available dice:")
        self.print_dice()

        action_number = self.bot_actions[(round_number-1)%4]
        action = self.bot_pyramid[action_number]

        def god_die_pick(god):
            # pick highest pure/tainted
            candidates = {polarity:dice for polarity,dice in self.available_dice[action].items() if polarity!="Forbidden"}
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
            while True:
                polarity, die_pick = god_die_pick(action)
                if die_pick:
                    activated_god = action
                    break
                else:         
                    current = GOD_ORDER.index(action)
                    action = GOD_ORDER[(current-1)%6]
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
        self.do_bot_action(activated_god)

    def osiris_building_scoring(self, region):
        statue = [self.built_statues[r] for r in self.built_statues if region in r]
        pieces = statue + self.built_osiris_buildings[region]
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
            
        if winner=="Player":
            print("Player has {} pieces, Bot has {} in Osiris {}. Player scores 3 VPs".format(player_count, bot_count, region))
        elif winner=="Bot":
            print("Player has {} pieces, Bot has {} in Osiris {}. Bot scores 3 VPs".format(player_count, bot_count, region))    
            self.vps += 3
        else:
            assert player_count == 0
            assert bot_count == 0
            print("Player has {} pieces, Bot has {} in Osiris {}. Nobody scores 3 VPs".format(player_count, bot_count, region))    

    def temple_scoring(self):
        pieces = self.built_temple_buildings["Horizontal"] + self.built_temple_buildings["Vertical"] + [self.built_statues["Temple_Horizontal"], self.built_statues["Temple_Vertical"]]
        bot_count, player_count = pieces.count("Bot"), pieces.count("Player")
        self.vps += bot_count
        print("Player scores {} VPs. Bot scores {} VPs for Temple Buildings".format(player_count, bot_count))

        def pillar_scoring(who):
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
        statue_vps = int((self.number_built_statues * (1+self.number_built_statues))/2)
        self.vps += statue_vps
        print("Bot scores {} VPs for Statues".format(statue_vps))

    def happiness_scoring(self):
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
        blessing_vps, tech_vps = 2*self.blessings, 2*self.technologies
        self.vps += blessing_vps+tech_vps
        self.blessings = 0
        print("Bot scored {} VPs for Blessings and {} VPs for Techs".format(blessing_vps, tech_vps))

    def print_dice(self):
        base = ""
        for god in self.available_dice:
            base += "{}\n".format(god)
            for polarity in self.available_dice[god]:
                base += "\t{}\t{}\n".format(polarity[:7], self.available_dice[god][polarity])
        print(base)

    def game_loop(self):
        
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
                    print("Maat Phase #{}".format(round_number/4))

                    # Check balance, assign turn order
                    player_balance = int(input("What is the absolute value of Player balance?: "))
                    bot_balance = max(4-(round_number/4), 1)
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
                            self.osiris_building_scoring(region)
                        self.temple_scoring()
                        self.statue_scoring()     
                        self.happiness_scoring()                   
                        self.card_scoring()
                        print("Scoring summary: Bot scored {} VPs".format(self.vps))

                        if round_number%16==0:
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
    horus_order=['Horus', 'Ra', 'Hathor', 'Bastet', 'Thoth', 'Osiris'],
    first_sunny="Horus",
    starting_dice={
        'Horus': [("Granite",5), ("Limestone",5), ("Limestone",3)], 
        'Ra': [("Gray",1), ("Granite",2), ("Papyrus",3)], 
        'Hathor': [("Bread",3), ("Papyrus",3), ("Limestone",5 ) ], 
        'Bastet':[("Bread",2), ("Papyrus",2), ("Gray",5)], 
        'Thoth':[("Limestone",5 ), ("Granite",4) , ("Gray",3 )], 
        'Osiris':[("Gray",3 ), ("Gray",6 ), ("Granite",5 ) ]
    }
)
game.game_loop()