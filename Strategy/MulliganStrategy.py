from Core.Zones import *
from Core.GameState import *
import copy

# gamestate = Will use the game's library for mulligans/shuffling
# typesNeededList = an array of dictionaries, where each dictionary specifies the types needed for a round of mulligans
# The first element is your types needed for the first mulligan check, the second element is for checking if a second
# mulligan is needed, so on and so forth
#
# Returns a completed gamestate, with finished hand, library, battlefield, and GY zones.  Time to battle!
def mullToNeededTypes(gamestate, typesNeededList=[]):

    numMulls = 0

    # Iterate through the mulligan rounds
    for typesNeeded in typesNeededList:
        shuffledLib = copy.deepcopy(gamestate.library)
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

        # Return cards that aren't needed
        # TODO
        hand.removeCard()

    # After all the mulligans finish produce a final gamestate and return it
    gamestate.library = shuffledLib
    gamestate.hand = hand

    return None

# gamestate = Will use the game's library for mulligans/shuffling
# detailsNeededList = An array of mulligan strategies, the first element is your types needed for the first mulligan
#                     check, the second element is for checking if a second mulligan is needed, so on and so fortht is
#                     the strategy for mulling has two dictionary elements to it
# Each strategy element in the detailsNeededList is a dictionary of two items
#       detailsNeededList[0].detail = A dictionary listing the types and attributes of cards you're looking for.
#                                     "name" is a special type that will look for a specific card name
#       detailsNeededList[0].numNeeded = An array of ranges that you need to find
def mullToNeededDetails(gamestate, detailsNeededList=[]):

    numMulls = 0
    cardsToReturnAfterMull = [1, 1, 1, 1, 1, 1, 1]

    # Iterate through the mulligan rounds
    for detailsNeeded in detailsNeededList:
        shuffledLib = copy.deepcopy(gamestate.library)
        shuffledLib.shuffleCards()
        hand = Zone("hand")
        shuffledLib.drawCards(hand, 7)

        numMatchingDetails = [0] * len(detailsNeeded)
        cardsToReturnAfterMull = [1, 1, 1, 1, 1, 1, 1]
        shouldKeep = True

        details = detailsNeeded["details"]
        numNeeded = detailsNeeded["numNeeded"]

        # Count cards that match details in hand
        for i, card in enumerate(hand.card_list):
            for j, d in enumerate(details):

                detailKey = list(d.keys())[0]
                detailValue = list(d.values())[0]

                # If the type to check is "name" look for card names instead
                if "name" == detailKey and detailValue == card.name:
                    cardsToReturnAfterMull[i] = 0
                    numMatchingDetails[j] += 1

                # Checks for strings and sets
                if (detailKey in card.properties) and (detailValue == card.properties[detailKey]):
                    cardsToReturnAfterMull[i] = 0
                    numMatchingDetails[j] += 1

        # Ensure all desired card details were found
        for i in range(len(details)):

            minNeeded = numNeeded[i][0]
            maxNeeded = numNeeded[i][1]

            if (numMatchingDetails[i] < minNeeded) or (numMatchingDetails[i] > maxNeeded):
                shouldKeep = False
                break

        if shouldKeep:
            break

        numMulls += 1

    # After all the mulligans finish produce a final gamestate and return it
    gamestate.library = shuffledLib
    gamestate.hand = hand

    # Return cards that aren't needed
    numMulledSoFar = 0
    for j in range(7):
        if cardsToReturnAfterMull[j] == 1:
            mulledCard = gamestate.hand.card_list.pop(j - numMulledSoFar)
            gamestate.library.card_list.append(mulledCard)
            numMulledSoFar += 1

        if numMulledSoFar == numMulls:
            break

    return numMulls