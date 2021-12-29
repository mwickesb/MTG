import json
from Core.Zones import *
from Core.CardClasses import *
from Strategy.MulliganStrategy import *
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

        # Fields that govern simulating a game
        self.simTurns = 3


        # Place to record miscellaneous information about the game
        self.scratchpad = {}

    def __str__(self):
        return "Our Life Total to Opponents:\t%d to %d" % (self.ourLife, self.opponentsLife)

    # Functions that are typically overriden by simulation scripts
    def playTurn(self, turnCount):
        return None

    # Default number of turns is self.simTurns
    def playGame(self, numTurns=-1):

        if numTurns >= 0:
            self.simTurns = numTurns
        if numTurns > 20:
            self.simTurns = 20

        # We'll keep playing until the GameState tells us not to or we hit our limit
        for turn in range(1, (self.simTurns + 1)):
            keepPlaying = self.playTurn(turn)

            if not keepPlaying:
                break

    # def resolveMulligans(self, typesNeeded, mulliganStrategy=mullToNeededTypes):
    def resolveMulligans(self, typesNeeded, mulliganStrategy=mullToNeededDetails):
        return mulliganStrategy(self, typesNeeded)

    # Create a game state from a Deck definition file
    @classmethod
    def createFromExperiment(cls, exp_file_name):

        library = Zone("library")

        # Load your deck, save it as a Library, and shuffle it up
        expObject = json.load(open(exp_file_name))
        decklist = expObject["decklist"]
        for k, v in decklist.items():
            for n in range(v["num"]):
                card = Card(k, v["properties"]["type"], v["properties"]["mana"], v["properties"])
                library.addCard(card)

        gamestate = cls()
        gamestate.library = library

        return (gamestate, expObject["config"])

def moveCard(source, destination, index):
    card = source.card_list.pop(index)
    destination.addCard(card)