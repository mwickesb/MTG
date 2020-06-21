from Core.CardClasses import *
from Core.Zones import *
from Core.GameState import *
from Core.SimulationEngine import *
from Strategy.MulliganStrategy import *

EXPERIMENT_DIR = "1"
NUM_GAMES = 500

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

    # Update Creatures turncount to remove summoning sickness
    for card in gamestate.battlefield.card_list:
        if card.card_type == "Creature":
            card.turns += 1

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

def playGame(gamestate, playTurn):

    # We'll play 3 turns per game and see how quickly we combo with Incinerator
    for turncount in range(1,4):
        playTurn(gamestate, turncount)

runSimulations(EXPERIMENT_DIR, typesNeededList, NUM_GAMES, takeTurn, playGame)