from random import shuffle, random
import collections
import statistics
import uuid
import re

class Card(object): #superclass of "Card" - every card inherits these attributes

    def __init__(self, name, card_type, mana_cost):

        self.name = name    # Spell Name
        self.card_type = card_type 	# Card Type - initialized in subclass
        self.mana_cost = mana_cost    # Converted mana cost
        self.UUID      = uuid.uuid4() # Create unique card ID
        

    def __str__(self):
        return "%s, %s, %s" % (self.name, self.card_type, self.mana_cost)

class Land(Card): #subclass "Land"

    def __init__(self, name, mana_out):
        Card.__init__(self, name, "Land", 0) #initializes it as a "Card"
        self.mana_out = mana_out # mana_out represents the amount of mana produced

class Creature(Card): #subclass "Creature"

    def __init__(self, name, mana_cost, power, toughness, abilities, haste = False):
        Card.__init__(self, name, "Creature", mana_cost)
        self.abilities = buildAbility(abilities)
        self.power = power
        self.toughness = toughness
        self.haste = haste
        if haste:
            self.turns = 1 #self.turns = # of turns the creature in play. set to 1 for creatures with haste
        else:
            self.turns = 0 # and 0 for creatures without haste. the attack function will check this

class Instant(Card): #subclass "Instant" - maybe we should change this to 'spell' - no need to differentiate instants and sorceries

    def __init__(self, name, mana_cost, ability):
        Card.__init__(self, name, "Instant", mana_cost)
        self.ability = buildAbility(ability) #

class Artifact(Card): # subclass "Artifact"

    def __init__(self, name, mana_cost, abilities):
        Card.__init__(self, name, "Artifact", mana_cost)
        self.abilities = buildAbility(abilities)

class Ability(object):
    def __init__(self, ability, value, cost):
        self.ability = ability
        self.value = value
        self.cost = cost

    def __str__(self):
        return "%s : %s %s" % (self.cost, self.ability, self.value)


class zone: #Library, Hand, Graveyard, Battlefield, etc

    def __init__(self, name):
        self.name = name # The name for this zone
        self.card_list = []

    def addCard(self, card):
        self.card_list.append(card)

    def printCards(self):
        card_index = 1
        print("\nCards in %s zone" % self.name)
        print("---------------------------")
        for card in self.card_list:
            print("#%d.) Card Type: %s\tMana Cost: %d\tUUID: %s" % (card_index, card.card_type, card.mana_cost, card.UUID.hex))
            card_index += 1

    def shuffleCards(self):
        shuffle(self.card_list)

    def addCard(self, card):
        self.card_list.append(card)


def moveCard(source, destination, index):
    card = source.card_list.pop(index)
    destination.addCard(card)



def buildAbility(string):
    if string != '':
        abil = string.strip().split(':')
        return Ability(abil[1], int(abil[2]), abil[0])
    else:
        return None

def importDeck(file_name):
    deckList = []
    deck = open(file_name)
    for line in deck:
        tempLine = line.strip().split(',')
        if tempLine[0] == 'Card Type':
            continue
        if tempLine[0] == 'Creature':
            for i in range(0,int(tempLine[1])):
                deckList.append(Creature(tempLine[2], convertMana(tempLine[3]), int(tempLine[4]), int(tempLine[5]), tempLine[6]))
        if tempLine[0] == 'Instant':
            for i in range(0, int(tempLine[1])):
                deckList.append(Instant(tempLine[2], convertMana(tempLine[3]), tempLine[6]))
        if tempLine[0] == 'Land':
            for i in range(0, int(tempLine[1])):
                deckList.append(Land(tempLine[2], convertMana(tempLine[3])))
        if tempLine[0] == 'Artifact':
            for i in range(0, int(tempLine[1])):
                deckList.append(Artifact(tempLine[2], convertMana(tempLine[3]), tempLine[6]))
    return deckList

def createLookupTable(N_digits):

    # Count from 0 to 2^N in binary
    # Add each of these arrays to the lookup table!
    N_lookups = 2**N_digits
    lookup_table = []
    for n in range(N_lookups):
        bin_str = bin(n).format(N_digits)   # Get a binary representation of an integer (as a string)
        bin_str = bin_str[2:]               # Strip off the leading "0b"
        # Pad front with zeros to get desired number of digits
        while ( len(bin_str) < N_digits ): bin_str = "0" + bin_str
        # Create list from the binary string, and add to table
        lookup_table.append(list(bin_str))

    return lookup_table

def best_play(hand, zone):

    total_mana = len([i for i in zone.card_list if i.card_type == "Land"])
    best_damage = 0
    best_combination = []
    best_mana = 0
    N_cards = len(hand.card_list)
    lookup_table = createLookupTable(N_cards)
    for combination in lookup_table:
        # Compute total cost and damage for this combination
        total_cost = 0
        damage = 0
        for n in range(N_cards):

            # Is the current card at index n not a land? If so, add its casting cost to the totals
            card = hand.card_list[n]
            if ( card.card_type != "Land" ):

                # Add cost to total, and recompute
                # priority for this combination of spells
                current_cost = card.mana_cost
                total_cost += int(combination[n]) * current_cost
                if card.card_type == "Creature":
                    if card.haste: #We should implement a has_haste function to check whether a certain creature's abilities contains haste
                        damage += int(combination[n]) * card.power
                    else:
                        damage += int(combination[n]) * card.power/2
                if card.card_type == "Instant" and card.ability.ability == 'DAM':
                    damage += int(combination[n]) * card.ability.value
#                	if card.has_haste:
#                		damage += 3
#                	if card.has_double:
#               		damage += 4    #Very rough estimates of how much damage haste and double strike can bring. Open to any changes/suggestions



        # Check that the total cost of the chosen spells is under the limit
        # If it is, check to see if this combination beats the highest damage
        if ((total_cost <= total_mana) and (damage > best_damage)):
            best_cost = total_cost
            best_damage = damage
            best_combination = combination

    
    # Now that we have the best combination, determine the corresponding card indices 
    # from the main hand. For example, if best_combination = [0,0,1,1,0], we'd want
    # spell_indices = [2,3]
    spell_indices = []
    for n in range(N_cards -1):
        if ( best_combination[n] == "1" ): spell_indices.append(n)

    return spell_indices #Returns the indexes for card objects that can deal the highest damage

def setupTest(filename, lands):
    deck = importDeck(filename)
    hand = zone('Hand')
    library = zone('Library')
    battle = zone('Battlefield')
    for card in deck:
        library.addCard(card)
    library.shuffleCards()
    for i in range(1,7):
        moveCard(library, hand, 0)
    for i in range(0, lands):
        test = Land('Test', 1)
        battle.addCard(test)
    return hand, library, battle





def playGame(deck):

    # initialize lives, library, hand, graveyard, etc
    enemy_life = 20
    turn_count = 0
    turn_reports = []

    graveyard = zone("Graveyard")
    hand = zone("Hand")
    library = zone("Library")
    battlefield = zone("Battlefield")
    for card in deck: # adds cards from decklist to library
        library.addCard(card)
    library.shuffleCards() # shuffles library
    for i in range(0,7): # draws 7 cards
        moveCard(library, hand, 0)
    gameState = [hand, library, battlefield, graveyard]
    while(enemy_life > 0):
        turn_count += 1
        new_state, turnstat = takeTurn(gameState)
        turn_reports.append(turnstat)
        enemy_life -= turnstat[0]
        gameState = new_state
    return turn_count, turn_reports


def takeTurn(gamestate):
    hand = gamestate[0]
    library = gamestate[1]
    battle = gamestate[2]
    graveyard = gamestate[3]
    lands_played = 0
    dam_dealt = 0
    spells_cast = 0
    creature_cast =0

    #Draw Phase
    moveCard(library, hand, 0)

    #Checks for land to play, and plays first land it finds
    for i in range(0, len(hand.card_list)-1):
        if hand.card_list[i].card_type == 'Land':
            moveCard(hand, battle, i)
            lands_played = 1
            print('Played a Land')
            break

    #Update Creatures turncount for summoning sickness
    for card in battle.card_list:
        print(card.name+" is on the battlefield")
        if card.card_type == "Creature":
            card.turns += 1

    #Cast Spells
    best_spells = best_play(hand, battle)
    N_played = 0
    for i in best_spells:
        if hand.card_list[i - N_played].card_type == "Creature":
            print(hand.card_list[i - N_played].name+" was played")
            moveCard(hand, battle, i - N_played)
            creature_cast += 1
            N_played += 1
        if hand.card_list[i - N_played].card_type == "Instant":
            print(hand.card_list[i - N_played].name+" was played")
            dam_dealt += hand.card_list[i - N_played].ability.value
            spells_cast += 1
            moveCard(hand, graveyard, i - N_played)
            N_played += 1

    #Attack!
    for card in battle.card_list:
        if card.card_type == "Creature" and card.turns > 0:
            print(card.name+" attacks")
            dam_dealt += card.power

    #Discard Phase
    while len(hand.card_list) > 7:
        moveCard(hand, graveyard, randrange(0, len(hand.card_list)))

    gamestate = [hand, library, battle, graveyard]
    turn_stats = [dam_dealt, spells_cast, creature_cast, lands_played]
    print(str(dam_dealt)+" was dealt this turn\n")
    return gamestate, turn_stats












def convertMana(manacost): 

#Converts a string manacost to an integer converted cost
    manacost = re.sub('[()]', ' ', manacost)
    manacost = manacost.replace("P/W", " 1")
    manacost = manacost.replace("P/U", " 1")
    manacost = manacost.replace("P/B", " 1")
    manacost = manacost.replace("P/R", " 1")
    manacost = manacost.replace("P/G", " 1")
    manacost = manacost.replace("W/U", " 1")
    manacost = manacost.replace("W/B", " 1")
    manacost = manacost.replace("U/B", " 1")
    manacost = manacost.replace("U/R", " 1")
    manacost = manacost.replace("B/R", " 1")
    manacost = manacost.replace("B/G", " 1")
    manacost = manacost.replace("R/W", " 1")
    manacost = manacost.replace("R/G", " 1")
    manacost = manacost.replace("G/W", " 1")
    manacost = manacost.replace("G/U", " 1")
    manacost = manacost.replace("2/W", " 2")
    manacost = manacost.replace("2/U", " 2")
    manacost = manacost.replace("2/B", " 2")
    manacost = manacost.replace("2/R", " 2")
    manacost = manacost.replace("2/G", " 2")
    manacost = manacost.replace("W", " 1")
    manacost = manacost.replace("U", " 1")
    manacost = manacost.replace("B", " 1")
    manacost = manacost.replace("R", " 1")
    manacost = manacost.replace("G", " 1")
    manacost = manacost.replace("S", " 1")
    manacost = manacost.replace("C", " 1")
    manacost = manacost.replace("X", " 0")
    manacost = manacost.replace("Y", " 0")
    manacost = manacost.replace("Z", " 0")
    temp = manacost.split()
    temp = list([int(i) for i in temp])
    return sum(temp)




