from Core.Zones import *
from Core.GameState import *
import copy

# library - Initial unshuffled library to use through the mulligan process
# typesNeededList - an array of dictionaries, where each dictionary specifies the types needed for a round of mulligans
# The first element is your types needed for the first mulligan check, the second element is for checking if a second
# mulligan is needed, so on and so forth
#
# Returns a completed gamestate, with finished hand, library, battlefield, and GY zones.  Time to battle!
def mullToNeededTypes(library, typesNeededList=[]):

    gamestate = GameState()
    shuffledLib = Zone("Library")
    hand = Zone("Hand")
    numMulls = 0

    # Iterate through the mulligan rounds
    for typesNeeded in typesNeededList:
        shuffledLib = copy.deepcopy(library)
        shuffledLib.shuffleCards()
        hand = Zone("hand")
        shuffledLib.drawCards(hand, 7)

        typesFound = {}
        shouldKeep = True

        # Count card types in hand
        for card in hand.card_list:
            if card.card_type in typesFound:
                typesFound[card.card_type] += 1
            else:
                typesFound[card.card_type] = 1

        # See if the desired amount of cards was found
        for type, numNeeded in typesNeeded.items():

            minNeeded = numNeeded[0]
            maxNeeded = numNeeded[1]

            if type not in typesFound:
                shouldKeep = False
                break
            else:
                if (typesFound[type] < minNeeded) or (typesFound[type] > maxNeeded):
                    shouldKeep = False
                    break

        if shouldKeep:
            break

        numMulls += 1

    # Return cards after a keep
    for i in range(numMulls):
        hand.removeCard()

    # After all the mulligans finish produce a final gamestate and return it
    gamestate.library = shuffledLib
    gamestate.hand = hand

    return gamestate
