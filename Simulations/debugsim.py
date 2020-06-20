from Core.CardClasses import *
from Core.Zones import *
from Core.GameState import *
from Strategy.MulliganStrategy import *


FILE_NAME = "../Decks/AggroDeck.json"

# Import a Deck and draw a fresh hand
hand = Zone("hand")
library = importDeck(FILE_NAME)
library.drawCards(hand, 7)

# 7 card mulligan rule
typesNeeded = {
    "Land" : [2,3],
    "OTHER": [4,5]
}
shouldMull = mullBasedNeededTypes(hand, typesNeeded)
numMull = 0

# 6 card mulligan rule
if shouldMull:
    hand = Zone("hand")
    library = importDeck(FILE_NAME)
    library.drawCards(hand, 6)
    numMull = 1

    typesNeeded = {
        "Land": [1, 3],
        "OTHER": [3, 5]
    }
    shouldMull = mullBasedNeededTypes(hand, typesNeeded)

# 5 card mulligan rule, keep anything
if shouldMull:
    hand = Zone("hand")
    library = importDeck(FILE_NAME)
    library.drawCards(hand, 5)
    numMull = 2

# Print results
if numMull == 0:
    print("Congrats, no need to mulligan")
else:
    print("Shoot, mull to ", (7-numMull))
hand.printCards()