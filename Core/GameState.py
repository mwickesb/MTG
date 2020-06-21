import json
from Core.Zones import *
from Core.CardClasses import *
import random

class GameState: #Library, Hand, Graveyard, Battlefield, etc

    def __init__(self):
        self.library = Zone("Library")
        self.hand = Zone("Hand")
        self.graveyard = Zone("Graveyard")
        self.battlefield = Zone("Battlefield")
        self.exile = Zone("Exile")

        self.opponentsLife = 20
        self.ourLife = 20

        self.onThePlay = random.randint(0,1)

        # Place to record miscellaneous information about the game
        self.scratchpad = {}

    def __str__(self):
        return "Our Life Total to Opponents:\t%d to %d" % (self.ourLife, self.opponentsLife)


def importDeck(file_name):

    library = Zone("library")

    # Load your deck, save it as a Library, and shuffle it up
    decklist = json.load(open(file_name))
    for k, v in decklist.items():
        for n in range(v["num"]):
            type = v["properties"]["type"]
            mana = v["properties"]["mana"]
            card = {}
            if type == "creature":
                card = Creature(k, mana, 1, 1, "")
            elif type == "instant":
                card = Instant(k, mana, "")
            elif type == "land":
                card = Land(k, "R")
            else:
                card = Card(k, "other", mana)
            library.addCard(card)

    return library


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

def moveCard(source, destination, index):
    card = source.card_list.pop(index)
    destination.addCard(card)