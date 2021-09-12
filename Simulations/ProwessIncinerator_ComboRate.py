from Core.CardClasses import *
from Core.Zones import *
from Core.GameState import *
from Core.ScoreResults import *
from Core.SimulationEngine import *
from Strategy.MulliganStrategy import *

EXPERIMENT_DIR = "3"
NUM_GAMES = 1000

MULL_COUNT = "MULL_COUNT"
COMBO_TURN = "COMBO_TURN"
COMBO_TYPE = "COMBO_TYPE"
TOTAL_DAMAGE = "TOTAL_DAMAGE"

# Define mulligan rules
typesNeededList = [
    # 7 card mulligan rule
    {
        "land" : [2,3],
    },

    # 6 card mulligan rule, keep anything after 2 mulligans
    {
        "land": [1, 3],
    }]

class ProwessGame(GameState):  # subclass "GameState"

    def __init__(self):
        GameState.__init__(self)

    # Returns if landfall triggers from fetch lands
    def tapLands(self, n, priortizeLandfall=False):
        untappedNonFetchLands = [i for i in self.battlefield.card_list if i.card_type == "land" and (not i.tapped) and (not i.fetch)]
        untappedFetchLands = [i for i in self.battlefield.card_list if i.card_type == "land" and (not i.tapped) and i.fetch]
        nNonFetch = len(untappedNonFetchLands)
        nFetch = len(untappedFetchLands)

        landfall = False
        if not priortizeLandfall:
            for i in range(0,min(nNonFetch,n)):
                untappedNonFetchLands[i].tapped = True
                n -= 1
            for i in range(0,min(nFetch,n)):
                untappedFetchLands[i].tapped = True
                untappedFetchLands[i].fetch = False
                n -= 1
                landfall = True
        else:
            for i in range(0,min(nFetch,n)):
                untappedFetchLands[i].tapped = True
                n -= 1
                landfall = True
            for i in range(0, min(nNonFetch, n)):
                untappedNonFetchLands[i].tapped = True
                n -= 1

        return landfall

    def untapLands(self):
        lands = [i for i in self.battlefield.card_list if i.card_type == "land"]

        for i in range(len(lands)):
            lands[i].tapped = False

        return None

    def landFallPossible(self):
        return len([i for i in self.battlefield.card_list if i.card_type == "Land" and (not i.tapped) and i.fetch]) > 0

    def playTurn(self, turncount):

        totalBurn = 0
        totalDamage = 0
        comboType = "No Combo"
        preMainProwess = 0
        postMainProwess = 0

        # Untap Phase
        self.untapLands()

        # Draw Phase
        didMiracle = False
        if (turncount != 1) or (self.onThePlay != 1):
            moveCard(self.library, self.hand, 0)

        # Resolve Rift Bolts
        for i, card in enumerate(self.exile.card_list):
            if card.name == "Rift Bolt":
                totalBurn += 3
                preMainProwess += 1
                moveCard(self.exile, self.graveyard, i)

        # Play your land if possible and update your available mana.  Prioritize non-fetches to save cracking for blaze
        playedLand = False
        if self.hand.containsCard("Non Fetch Land"):
            playedLand = self.hand.removeCardName("Non Fetch Land")
            playedLand.fetch = False
            playedLand.tapped = False
            self.battlefield.addCard(playedLand)
            playedLand = True
        if (not playedLand) and self.hand.containsCard("Fetch Land"):
            playedLand = self.hand.removeCardName("Fetch Land")
            playedLand.fetch = True
            playedLand.tapped = False
            self.battlefield.addCard(playedLand)
            playedLand = True
        totalMana = len([i for i in self.battlefield.card_list if i.card_type == "land"])

        # Update Creatures turncount to remove summoning sickness
        for card in self.battlefield.card_list:
            if card.card_type == "creature":
                card.turns += 1

        if (turncount == 1):
            if (totalMana >= 1) and self.hand.containsCard("Rift Bolt"):
                exiledRiftBolt = self.hand.removeCardName("Rift Bolt")
                self.exile.addCard(exiledRiftBolt)
                totalMana -= 1
                self.tapLands(1)
            elif (totalMana >= 1) and self.hand.containsCard("Monastery Swiftspear"):
                swifty = self.hand.removeCardName("Monastery Swiftspear")
                swifty.turns = 0
                self.battlefield.addCard(swifty)
                totalMana -= 1
                self.tapLands(1)
            elif (totalMana >= 1) and self.hand.containsCard("Bolt Burn"):
                bolt = self.hand.removeCardName("Bolt Burn")
                self.graveyard.addCard(bolt)
                totalMana -= 1
                totalBurn += 3
                postMainProwess += 1
                self.tapLands(1)
        else:

            # Attempt to execute combo sequences with Incinerator
            if totalBurn >= 2 and self.hand.containsCard("Bolt Burn") and self.hand.containsCard("Chandras Incinerator") and totalMana >= 2:
                playedBolt = self.hand.removeCardName("Bolt Burn")
                self.graveyard.addCard(playedBolt)
                playedIncinerator = self.hand.removeCardName("Chandras Incinerator")
                playedIncinerator.turns = 0
                self.battlefield.addCard(playedIncinerator)
                self.tapLands(2)
                totalMana -= 2
                totalBurn += 3
                postMainProwess += 1
                if "comboTurn" not in self.scratchpad:
                    self.scratchpad["comboTurn"] = turncount
                    self.scratchpad["comboType"] = "Delayed Burn"
            if totalBurn >= 2 and self.hand.containsCard("Skull Crack") and self.hand.containsCard("Chandras Incinerator") and totalMana >= 3:
                spell = self.hand.removeCardName("Skull Crack")
                self.graveyard.addCard(spell)
                playedIncinerator = self.hand.removeCardName("Chandras Incinerator")
                playedIncinerator.turns = 0
                self.battlefield.addCard(playedIncinerator)
                self.tapLands(3)
                totalMana -= 3
                totalBurn += 3
                postMainProwess += 1
                if "comboTurn" not in self.scratchpad:
                    self.scratchpad["comboTurn"] = turncount
                    self.scratchpad["comboType"] = "Direct Burn"
            if totalBurn >= 2 and self.hand.containsCard("Searing Blaze") and self.hand.containsCard("Chandras Incinerator") and (self.landFallPossible() or playedLand) and totalMana >= 3:
                spell = self.hand.removeCardName("Searing Blaze")
                self.graveyard.addCard(spell)
                playedIncinerator = self.hand.removeCardName("Chandras Incinerator")
                playedIncinerator.turns = 0
                self.battlefield.addCard(playedIncinerator)
                self.tapLands(3, True)
                totalMana -= 3
                totalBurn += 3
                postMainProwess += 1
                if "comboTurn" not in self.scratchpad:
                    self.scratchpad["comboTurn"] = turncount
                    self.scratchpad["comboType"] = "Direct Burn"
            if (self.hand.containsCard("Bolt Burn") >= 2) and self.hand.containsCard("Chandras Incinerator") and totalMana >= 3:
                playedBolt = self.hand.removeCardName("Bolt Burn")
                self.graveyard.addCard(playedBolt)
                playedBolt = self.hand.removeCardName("Bolt Burn")
                self.graveyard.addCard(playedBolt)
                playedIncinerator = self.hand.removeCardName("Chandras Incinerator")
                playedIncinerator.turns = 0
                self.battlefield.addCard(playedIncinerator)
                self.tapLands(3)
                totalMana -= 3
                totalBurn += 6
                postMainProwess += 2
                if "comboTurn" not in self.scratchpad:
                    self.scratchpad["comboTurn"] = turncount
                    self.scratchpad["comboType"] = "Direct Burn"
            if totalBurn >= 2 and self.hand.containsCard("Shard Valley") and self.hand.containsCard("Chandras Incinerator") and totalMana >= 2:
                spell = self.hand.removeCardName("Shard Valley")
                self.graveyard.addCard(spell)
                playedIncinerator = self.hand.removeCardName("Chandras Incinerator")
                playedIncinerator.turns = 0
                self.battlefield.addCard(playedIncinerator)
                self.tapLands(2)
                land = self.battlefield.removeCardType("land")
                self.graveyard.addCard(land)
                totalMana -= 2
                totalBurn += 3
                postMainProwess += 1
                if "comboTurn" not in self.scratchpad:
                    self.scratchpad["comboTurn"] = turncount
                    self.scratchpad["comboType"] = "Direct Burn"

            # Use up the rest of your mana. Prioritize Rift > Swift > Landfall Blaze > Bolt > Crack > Shard Valley
            while totalMana > 0:
                if self.hand.containsCard("Rift Bolt"):
                    spell = self.hand.removeCardName("Rift Bolt")
                    self.exile.addCard(spell)
                    playedLand = self.tapLands(1) or playedLand
                    totalMana -= 1
                    continue
                elif self.hand.containsCard("Monastery Swiftspear"):
                    swifty = self.hand.removeCardName("Monastery Swiftspear")
                    swifty.turns = 0
                    self.battlefield.addCard(swifty)
                    playedLand = self.tapLands(1) or playedLand
                    totalMana -= 1
                    continue
                elif self.hand.containsCard("Searing Blaze") and (self.landFallPossible() or playedLand) and totalMana >= 2:
                    spell = self.hand.removeCardName("Searing Blaze")
                    self.graveyard.addCard(spell)
                    self.tapLands(2, True)
                    totalMana -= 2
                    totalBurn += 3
                    postMainProwess += 1
                    continue
                elif self.hand.containsCard("Bolt Burn"):
                    spell = self.hand.removeCardName("Bolt Burn")
                    self.graveyard.addCard(spell)
                    playedLand = self.tapLands(1) or playedLand
                    totalMana -= 1
                    totalBurn += 3
                    postMainProwess += 1
                    continue
                elif self.hand.containsCard("Skull Crack"):
                    spell = self.hand.removeCardName("Skull Crack")
                    self.battlefield.addCard(spell)
                    playedLand = self.tapLands(2) or playedLand
                    totalMana -= 2
                    totalBurn += 3
                    postMainProwess += 1
                    continue
                elif self.hand.containsCard("Shard Valley"):
                    spell = self.hand.removeCardName("Shard Valley")
                    self.battlefield.addCard(spell)
                    playedLand = self.tapLands(1) or playedLand
                    land = self.battlefield.removeCardType("land")
                    self.graveyard.addCard(land)
                    totalMana -= 1
                    totalBurn += 3
                    postMainProwess += 1
                    continue
                else:
                    break


        # Attack!
        for card in self.battlefield.card_list:
            if card.card_type == "creature":
                if card.turns == 0 and ("haste" in card.properties["abilities"]):
                    totalDamage += card.properties["power"] + postMainProwess
                elif card.turns > 0:
                    totalDamage += card.properties["power"] + preMainProwess + postMainProwess

        totalDamage += totalBurn
        self.opponentsLife -= totalDamage

        # Discard Phase
        # We're burn, assume we never discard

        return comboType

    def recordGameResult(self):
        # Record the results
        result = {}
        if "comboTurn" in self.scratchpad:
            result[COMBO_TURN] = self.scratchpad["comboTurn"]
            result[COMBO_TYPE] = self.scratchpad["comboType"]
        else:
            result[COMBO_TURN] = 0
            result[COMBO_TYPE] = "No Combo"

        return result

    def recordSimulationSummary(self, game_results, numGames):
        # Calculate result summary statistics
        countKeeps = sum(map(lambda result: result[MULL_COUNT] == 0, game_results))
        count1Mull = sum(map(lambda result: result[MULL_COUNT] == 1, game_results))
        count2Mull = sum(map(lambda result: result[MULL_COUNT] == 2, game_results))
        countT2Combo = sum(map(lambda result: result[COMBO_TURN] == 2, game_results))
        countT3Combo = sum(map(lambda result: result[COMBO_TURN] == 3, game_results))
        countCT_Miracle = sum(map(lambda result: result[COMBO_TYPE] == "Miracle", game_results))
        countCT_DelayedBurn = sum(map(lambda result: result[COMBO_TYPE] == "Delayed Burn", game_results))
        countCT_DirectBurn = sum(map(lambda result: result[COMBO_TYPE] == "Direct Burn", game_results))
        totalCombos = countCT_Miracle + countCT_DelayedBurn + countCT_DirectBurn
        avgDamage = sum(map(lambda result: result[TOTAL_DAMAGE], game_results))
        resultsSummary = {
            "WinningTurn": -1,
            "ComboTurn": [0, round(countT2Combo / numGames, 3), round(countT3Combo / numGames, 3)],
            "mulligans": [round(countKeeps / numGames, 3), round(count1Mull / numGames, 3),
                          round(count2Mull / numGames, 3)],
            "Damage over 3 Turns": round(avgDamage / numGames, 3),
            "comboType": {
                "Miracle": round(countCT_Miracle / totalCombos, 3),
                "Delayed Burn": round(countCT_DelayedBurn / totalCombos, 3),
                "Direct Burn": round(countCT_DirectBurn / totalCombos, 3)
            }
        }

        return resultsSummary

runSimulations(EXPERIMENT_DIR, typesNeededList, NUM_GAMES, ProwessGame)

resultsDir = "../Results/" + EXPERIMENT_DIR
dimensions = ["Shard Valley", "Rift Bolt"]

# Visualize the simulations results
def sumComboRate(comboRateByTurn):
    comboRate = 0
    for i in range(0,len(comboRateByTurn)):
        comboRate += comboRateByTurn[i]

    return comboRate
overallComboRate = ScoreCriteria(["ComboTurn"], sumComboRate)
visualizeResults(resultsDir, dimensions, overallComboRate, "Overall Combo Rate - Shard v Rift")

# Visualize T2 combo rate
def getT2Combo(comboRateByTurn):
    return comboRateByTurn[1]
t2ComboRate = ScoreCriteria(["ComboTurn"], getT2Combo)
visualizeResults(resultsDir, dimensions, t2ComboRate, "T2 Combo Rate - Shard v Rift")

# Visualize T3 combo rate
def getT3Combo(comboRateByTurn):
    return comboRateByTurn[2]
t3ComboRate = ScoreCriteria(["ComboTurn"], getT3Combo)
visualizeResults(resultsDir, dimensions, t3ComboRate, "T3 Combo Rate - Shard v Rift")

# Visualize Delayed Burn Combo Rate
def getRawScore(score):
    return score
delayedRate = ScoreCriteria(["comboType", "Delayed Burn"], getRawScore)
visualizeResults(resultsDir, dimensions, delayedRate, "Delayed Burn Combo Ratio - Shard v Rift")

# Visualize Direct Burn Combo Rate
directRate = ScoreCriteria(["comboType", "Direct Burn"], getRawScore)
visualizeResults(resultsDir, dimensions, directRate, "Direct Burn Combo Ratio - Shard v Rift")

# Visualize Damage Output
damageOutput = ScoreCriteria(["Damage over 3 Turns"], getRawScore)
visualizeResults(resultsDir, dimensions, damageOutput, "Total Damage over 3 Turns - Shard v Rift")