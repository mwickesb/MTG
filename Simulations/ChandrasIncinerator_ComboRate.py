from Core.CardClasses import *
from Core.Zones import *
from Core.GameState import *
from Strategy.MulliganStrategy import *


FILE_NAME = "../Decks/AggroDeck.json"
NUM_GAMES = 10000

# A list of lists with the following structure
# game_results[i] = the i'th simulated game
# game_results[i][0] = Mulligan count
# game_results[i][1] = The combo turn
# game_results[i][2] = The combo type
# game_results[1][3] = Total damage delt in game
game_results = []
MULL_COUNT = "MULL_COUNT"
COMBO_TURN = "COMBO_TURN"
COMBO_TYPE = "COMBO_TYPE"
TOTAL_DAMAGE = "TOTAL_DAMAGE"

# Import a Deck and draw a fresh hand
library = importDeck(FILE_NAME)

# Define mulligan rules
typesNeededList = [
    # 7 card mulligan rule
    {
        "Land" : [2,3],
    },

    # 6 card mulligan rule, keep anything after 2 mulligans
    {
        "Land": [1, 3],
    }]

def takeTurn(gamestate, turncount):

    totalBurn = 0
    totalDamage = 0
    comboType = "No Combo"

    # Draw Phase
    moveCard(gamestate.library, gamestate.hand, 0)

    # Check for a miracle
    didMiracle = gamestate.hand.card_list[0].name == "Thunderous Wrath"

    # Resolve Rift Bolts
    for i, card in enumerate(gamestate.exile.card_list):
        if card.name == "Rift Bolt":
            totalBurn += 3
            moveCard(gamestate.exile, gamestate.graveyard,i)

    # Play your land if possible and update your available mana
    if gamestate.hand.containsCard("Land"):
        playedLand = gamestate.hand.removeCardName("Land")
        gamestate.battlefield.addCard(playedLand)
    totalMana = len([i for i in gamestate.battlefield.card_list if i.card_type == "Land"])

    # Resolve miracles and see if you can combo out Incinerator
    if didMiracle and totalMana >= 1:
        totalMana -= 1
        totalBurn += 5
        moveCard(gamestate.hand, gamestate.graveyard, 0)

        if gamestate.hand.containsCard("Chandras Incinerator") and totalMana >= 1:
            playedIncinerator = gamestate.hand.removeCardName("Chandras Incinerator")
            gamestate.battlefield.addCard(playedIncinerator)
            totalMana -= 1
            if "comboTurn" not in gamestate.scratchpad:
                gamestate.scratchpad["comboTurn"] = turncount
                gamestate.scratchpad["comboType"] = "Miracle"

    # Update Creatures turncount to remove summoning sickness
    for card in gamestate.battlefield.card_list:
        if card.card_type == "Creature":
            card.turns += 1

    # Check to see if you can play Incinerator with burn damage.  If so, execute the sequence
    if totalBurn >= 3 and gamestate.battlefield.containsCard("Seal of Fire") and gamestate.hand.containsCard("Chandras Incinerator") and totalMana >= 1:
        resolvedSeal = gamestate.battlefield.removeCardName("Seal of Fire")
        gamestate.graveyard.addCard(resolvedSeal)
        comboType = "Delayed Burn"
    if totalBurn >= 2 and gamestate.hand.containsCard("Bolt Burn") and gamestate.hand.containsCard("Chandras Incinerator") and totalMana >= 2:
        playedBolt = gamestate.hand.removeCardName("Bolt Burn")
        gamestate.graveyard.addCard(playedBolt)
        totalMana -= 1
        totalBurn += 3
        comboType = "Delayed Burn"
    if (gamestate.hand.containsCard("Bolt Burn") >= 2) and gamestate.hand.containsCard("Chandras Incinerator") and totalMana >= 3:
        playedBolt = gamestate.hand.removeCardName("Bolt Burn")
        gamestate.graveyard.addCard(playedBolt)
        playedBolt = gamestate.hand.removeCardName("Bolt Burn")
        gamestate.graveyard.addCard(playedBolt)
        totalMana -= 2
        totalBurn += 6
        comboType = "Double Bolt Burn"
    if totalBurn >= 5 and gamestate.hand.containsCard("Chandras Incinerator") and totalMana >= 1:
        playedIncinerator = gamestate.hand.removeCardName("Chandras Incinerator")
        gamestate.battlefield.addCard(playedIncinerator)
        totalMana -= 1
        if "comboTurn" not in gamestate.scratchpad:
            gamestate.scratchpad["comboTurn"] = turncount
            gamestate.scratchpad["comboType"] = comboType

    # Use up the rest of your mana. Prioritize Rift Bolt > Seal > Other Burn else don't play a spell
    while totalMana > 0:
        if gamestate.hand.containsCard("Rift Bolt"):
            exiledRiftBolt = gamestate.hand.removeCardName("Rift Bolt")
            gamestate.exile.addCard(exiledRiftBolt)
            totalMana -= 1
            continue
        elif gamestate.hand.containsCard("Seal of Fire"):
            playedSeal = gamestate.hand.removeCardName("Seal of Fire")
            gamestate.battlefield.addCard(playedSeal)
            totalMana -= 1
            continue
        elif gamestate.hand.containsCard("Other Burn"):
            playedOtherBurn = gamestate.hand.removeCardName("Other Burn")
            gamestate.battlefield.addCard(playedOtherBurn)
            totalMana -= 1
            continue
        else:
            break

    # Attack!
    for card in gamestate.battlefield.card_list:
        if card.card_type == "Creature" and (card.turns is not None):
            totalDamage += card.power

    totalDamage += totalBurn
    gamestate.opponentsLife -= totalDamage

    # Discard Phase
    # We're burn, assume we never discard

    return comboType

def playGame(gamestate):

    # We'll play 3 turns per game and see how quickly we combo with Incinerator
    for turncount in range(1,4):
        takeTurn(gamestate, turncount)

# Simulation loop
for gamecount in range(NUM_GAMES):
    # Resolve mulligans
    gamestate = mullToNeededTypes(library, typesNeededList)
    numMull = 7 - len(gamestate.hand.card_list)
    playGame(gamestate)

    # Record the results
    result = {}
    result[MULL_COUNT] = numMull
    if "comboTurn" in gamestate.scratchpad:
        result[COMBO_TURN] = gamestate.scratchpad["comboTurn"]
        result[COMBO_TYPE] = gamestate.scratchpad["comboType"]
    else:
        result[COMBO_TURN] = 0
        result[COMBO_TYPE] = "No Combo"
    result[TOTAL_DAMAGE] = 20 - gamestate.opponentsLife
    game_results.append(result)

# Show the results
countKeeps = sum(map(lambda result : result[MULL_COUNT] == 0, game_results))
count1Mull = sum(map(lambda result : result[MULL_COUNT] == 1, game_results))
count2Mull = sum(map(lambda result : result[MULL_COUNT] == 2, game_results))
countT2Combo = sum(map(lambda result : result[COMBO_TURN] == 2, game_results))
countT3Combo = sum(map(lambda result : result[COMBO_TURN] == 3, game_results))
countCT_Miracle = sum(map(lambda result : result[COMBO_TYPE] == "Miracle", game_results))
countCT_DelayedBurn = sum(map(lambda result : result[COMBO_TYPE] == "Delayed Burn", game_results))
countCT_DoubleBolt = sum(map(lambda result : result[COMBO_TYPE] == "Double Bolt Burn", game_results))
totalCombos = countCT_Miracle + countCT_DelayedBurn + countCT_DoubleBolt

print('Percent 7 card hands:\t' + str(round(countKeeps / NUM_GAMES,3)))
print('Percent Mull to 6   :\t' + str(round(count1Mull / NUM_GAMES,3)))
print('Percent Mull to 5   :\t' + str(round(count2Mull / NUM_GAMES,3)))
print('')
print('Percent  T2 Incinerator:\t' + str(round(countT2Combo / NUM_GAMES,3)))
print('Percent  T3 Incinerator:\t' + str(round(countT3Combo / NUM_GAMES,3)))
print('')
print('Total Combos                :\t' + str(totalCombos))
print('Percent  Miracle Combos     :\t' + str(round(countCT_Miracle / totalCombos,3)))
print('Percent  Delayed Burn Combos:\t' + str(round(countCT_DelayedBurn / totalCombos,3)))
print('Percent  Double Bolt Combos :\t' + str(round(countCT_DoubleBolt / totalCombos,3)))