from Core.CardClasses import *
from Core.Zones import *
from Core.GameState import *
from Core.ScoreResults import *
from Core.SimulationEngine import *
from Strategy.MulliganStrategy import *

EXPERIMENT_DIR = "Throes Combo - Omniscience"
NUM_GAMES = 1000
NUM_TURNS = 5

MULL_COUNT = "MULL_COUNT"
COMBO_TURN = "COMBO_TURN"
COMBO_TYPE = "COMBO_TYPE"

# Define mulligan rules
detailsNeededList = [
    # 7-6 card mulligan rule, find a Throes plus lands
    {
        "details": [{"type": "land"}, {"name": "Throes of Chaos"}],
        "numNeeded": [[2,7], [1,4]]
    },
    {
        "details": [{"type": "land"}, {"name": "Throes of Chaos"}],
        "numNeeded": [[2,7], [1,4]]
    },

    # 5-3 card mulligan rule, look for Throes and at least a land
    {
        "details": [{"type": "land"}, {"name": "Throes of Chaos"}],
        "numNeeded": [[1,7], [1,4]]
    },
    {
        "details": [{"type": "land"}, {"name": "Throes of Chaos"}],
        "numNeeded": [[1,7], [1,4]]
    },
    {
        "details": [{"type": "land"}, {"name": "Throes of Chaos"}],
        "numNeeded": [[1,7], [1,4]]
    },

    # 2-1 card mulligan rule, just look for Throes
    {
        "details": [{"name": "Throes of Chaos"}],
        "numNeeded": [[1, 4]]
    },

    # Range is "[0-4]" since we'll favor keeping Throes but will keep anything
    {
        "details": [{"name": "Throes of Chaos"}],
        "numNeeded": [[0, 4]]
    }]

class ThroesGame(GameState):  # subclass "GameState"

    def __init__(self):
        self.treasure = 0
        self.numLands = 0
        self.cardCastByThroes = None
        self.didCastThroes = False
        self.wasThroesCastWithTreasure = False
        GameState.__init__(self)

    def untapLands(self):
        lands = [i for i in self.battlefield.card_list if i.card_type == "Land"]

        for i in range(len(lands)):
            lands[i].tapped = False

        return None

    # Cast throes to see if/what you combo into
    # Step 1, find a trickery, Step 2 cast trickery
    # We'll ignore the random milling when you cast trickery since it has a negligible effect
    def throesCombo(self):
        chaosCard = self.hand.removeCardName("Throes of Chaos")
        self.graveyard.addCard(chaosCard)
        self.didCastThroes = True

        didCastTrickery = False

        for i, c in enumerate(self.library.card_list):
            if didCastTrickery == False:
                if c.name == "Tibalt's Trickery":
                    trickeryCard = self.library.card_list.pop(i)
                    self.graveyard.addCard(trickeryCard)
                    didCastTrickery = True

                    self.library.shuffleCards()
                    break

        if didCastTrickery == False:
            return False

        for i, c in enumerate(self.library.card_list):
            if c.card_type != "land" and c.name != "Throes of Chaos":
                self.cardCastByThroes = c
                return True

        return False

    def playTurn(self, turncount):

        comboType = "No Combo"

        # Untap Phase
        self.untapLands()

        # Draw Phase
        if (turncount != 1) or (self.onThePlay != 1):
            moveCard(self.library, self.hand, 0)

        # Play lands to optimize the chance for treasure creation and fast Throes of Chaos casting.
        # Technically sometimes you don't want to optimize treasure creation in situations you'd want
        # to cast Throes two turns in a row.  We'll ignore this scenario for now
        #
        # Red / Blue sources allow for  treasure creation, prioritize those lands first and ETB lands in turn 1
        # playedLand = False

        if (self.numLands == 0):
            landToPlay = self.hand.removeCardByDetails([{"type": "land", "mana": "U", "tapped": 1}, {"type": "land", "mana": "R", "tapped": 1}])
            if landToPlay == None:
                landToPlay = self.hand.removeCardByDetails([{"type": "land", "mana": "U"}, {"type": "land", "mana": "R"}])
            if landToPlay == None:
                landToPlay = self.hand.removeCardByDetails([{"type": "land", "tapped": 1}])
            if landToPlay == None:
                landToPlay = self.hand.removeCardType("land")
            if landToPlay != None:
                self.battlefield.addCard(landToPlay)
                self.numLands += 1

        elif (self.numLands == 1):

            landToPlay = None

            # Make a treasure if you can to setup a turn 3 combo
            if self.hand.containsCard("Treasure Maker") and self.battlefield.containsCardByDetails([{"type": "land", "mana": "R"}, {"type": "land", "mana": "U"}]) and self.hand.containsCardByDetails([{"type": "land", "mana": "R", "tapped": 0}, {"type": "land", "mana": "U", "tapped": 0}]):
                landToPlay = self.hand.removeCardByDetails([{"type": "land", "mana": "R", "tapped": 0}, {"type": "land", "mana": "U", "tapped": 0}])
                self.battlefield.addCard(landToPlay)
                self.numLands += 1

                treasureCard = self.hand.removeCardName("Treasure Maker")
                self.graveyard.addCard(treasureCard)
                self.treasure += 1

            # Otherwise play tapped lands
            if landToPlay == None:
                landToPlay = self.hand.removeCardByDetails([{"type": "land", "mana": "U", "tapped": 1}, {"type": "land", "mana": "R", "tapped": 1}])
                if landToPlay == None:
                    landToPlay = self.hand.removeCardByDetails([{"type": "land", "tapped": 1}])
                if landToPlay == None:
                    landToPlay = self.hand.removeCardByDetails([{"type": "land", "mana": "U"}, {"type": "land", "mana": "R"}])
                if landToPlay == None:
                    landToPlay = self.hand.removeCardType("land")
                if landToPlay != None:
                    self.battlefield.addCard(landToPlay)
                    self.numLands += 1

        elif (self.numLands == 2):

            landToPlay = None

            # Attempt to cast throes if you can
            if (self.treasure > 0) and self.hand.containsCardByDetails([{"tapped": 0}]) and self.battlefield.containsCardByDetails([{"type": "land", "mana": "R"}, {"type": "land", "mana": "U"}]) and self.hand.containsCard("Throes of Chaos"):
                landToPlay = self.hand.removeCardByDetails([{"type": "land", "tapped": 0}])
                self.battlefield.addCard(landToPlay)
                self.numLands += 1

                # Throes Combo Sequence
                self.treasure -= 1
                self.throesCombo()
                self.wasThroesCastWithTreasure = True

            # Otherwise play tapped lands
            if landToPlay == None:
                landToPlay = self.hand.removeCardByDetails([{"type": "land", "mana": "U", "tapped": 1}, {"type": "land", "mana": "R", "tapped": 1}])
                if landToPlay == None:
                    landToPlay = self.hand.removeCardByDetails([{"type": "land", "tapped": 1}])
                if landToPlay == None:
                    landToPlay = self.hand.removeCardByDetails([{"type": "land", "mana": "U"}, {"type": "land", "mana": "R"}])
                if landToPlay == None:
                    landToPlay = self.hand.removeCardType("land")
                if landToPlay != None:
                    self.battlefield.addCard(landToPlay)
                    self.numLands += 1

            # Make a treasure if you can
            # NOTE - This has a known logic issue, we don't count if there's 2 U/R sources, just one
            if self.hand.containsCard("Treasure Maker") and self.battlefield.containsCardByDetails([{"type": "land", "mana": "R"}, {"type": "land", "mana": "U"}]):
                treasureCard = self.hand.removeCardName("Treasure Maker")
                self.graveyard.addCard(treasureCard)
                self.treasure += 1

        else:
            numUntappedLands = self.numLands

            # Play another land
            landToPlay = self.hand.removeCardByDetails([{"type": "land", "mana": "U", "tapped": 0}, {"type": "land", "mana": "R", "tapped": 0}])
            if landToPlay != None:
                numUntappedLands += 1
            if landToPlay == None:
                landToPlay = self.hand.removeCardByDetails([{"type": "land", "mana": "U", "tapped": 1}, {"type": "land", "mana": "R", "tapped": 1}])
            if landToPlay == None:
                landToPlay = self.hand.removeCardByDetails([{"tapped": 1}])
            if landToPlay == None:
                landToPlay = self.hand.removeCardType("land")
                numUntappedLands += 1
            if landToPlay != None:
                self.battlefield.addCard(landToPlay)
                self.numLands += 1

            # Attempt to cast Throes
            if (self.treasure + numUntappedLands >= 4) and self.hand.containsCard("Throes of Chaos"):
                # Throes Combo Sequence
                self.throesCombo()

            # Make a treasure if you can
            # NOTE - This has a known logic issue, we don't count if there's 2 U/R sources, just one
            if self.hand.containsCard("Treasure Maker") and self.battlefield.containsCardByDetails([{"type": "land", "mana": "R"}, {"type": "land", "mana": "U"}]):
                treasureCard = self.hand.removeCardName("Treasure Maker")
                self.graveyard.addCard(treasureCard)
                self.treasure += 1

        # After lands and spells are cast record the results
        if self.didCastThroes == True:

            # No card cast means the cascade fizzled, meaning all Tibalt's Trickery are out of the library
            if self.cardCastByThroes == None:
                comboType = "Fizzle"

            # See if you hit a non-Omniscience bomb
            elif self.cardCastByThroes.name == "Big Bomb":
                comboType = "Big Bomb"
            elif self.cardCastByThroes.name == "Midrange Bomb":
                comboType = "Midrange Card"
            elif self.cardCastByThroes.name == "Treasure Maker":
                comboType = "Midrange Card"
            elif self.cardCastByThroes.name == "Tibalt's Trickery":
                comboType = "Fizzle"

            # Omniscience hits if there's cards in your hand
            elif self.cardCastByThroes.name == "Omniscience":
                if self.hand.containsCard("Big Bomb"):
                    comboType = "Big Bomb"
                elif self.hand.containsCard("Midrange Bomb"):
                    comboType = "Midrange Card"
                elif self.hand.containsCard("Treasure Maker"):
                    comboType = "Midrange Card"
                else:
                    comboType = "Fizzle"

            self.scratchpad["comboTurn"] = turncount
            self.scratchpad["comboType"] = comboType

            # Stop playing after you combo
            return False

        # Discard Phase - Don't care for now, will ignore

        # Keep playing until you combo
        self.scratchpad["comboTurn"] = turncount
        self.scratchpad["comboType"] = comboType
        return True

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
        count3Mull = sum(map(lambda result: result[MULL_COUNT] == 3, game_results))
        count4PlusMull = NUM_GAMES - countKeeps - count1Mull - count2Mull - count3Mull
        countT3Combo = sum(map(lambda result: result[COMBO_TURN] == 3, game_results))
        countT4Combo = sum(map(lambda result: result[COMBO_TURN] == 4, game_results))
        countT5_7Combo = sum(map(lambda result: result[COMBO_TURN] == 5, game_results)) + sum(map(lambda result: result[COMBO_TURN] == 6, game_results)) + sum(map(lambda result: result[COMBO_TURN] == 7, game_results))
        countCT_Bomb = sum(map(lambda result: result[COMBO_TYPE] == "Big Bomb", game_results))
        countCT_Midrange = sum(map(lambda result: result[COMBO_TYPE] == "Midrange Card", game_results))
        countCT_Fizzle = sum(map(lambda result: result[COMBO_TYPE] == "Fizzle", game_results))
        countCT_NoCombo = sum(map(lambda result: result[COMBO_TYPE] == "No Combo", game_results))
        totalCombos = countCT_Bomb + countCT_Midrange + countCT_Fizzle
        resultsSummary = {
            "WinningTurn": -1,
            "ComboTurn": [0, 0, round(countT3Combo / numGames, 3), round(countT4Combo / numGames, 3), round(countT5_7Combo / numGames, 3)],
            "mulligans": [round(countKeeps / numGames, 3), round(count1Mull / numGames, 3),
                          round(count2Mull / numGames, 3), round(count3Mull / numGames, 3),
                          round(count4PlusMull / numGames, 3)],
            }

        if totalCombos != 0:
            resultsSummary["comboType"] = {
                "Big Bomb": round(countCT_Bomb / numGames, 3),
                "Midrange Card": round(countCT_Midrange / numGames, 3),
                "Fizzle": round(countCT_Fizzle / numGames, 3),
                "No Combo": round(countCT_NoCombo / numGames, 3)
            }
        else:
            resultsSummary["comboType"] = {
                "Big Bomb": 0,
                "Midrange Card": 0,
                "Fizzle": 0,
                "No Combo": 1
            }

        return resultsSummary

runSimulations(EXPERIMENT_DIR, detailsNeededList, NUM_GAMES, NUM_TURNS, ThroesGame)

resultsDir = "../Results/" + EXPERIMENT_DIR
dimensions = ["Land", "Treasure Maker"]

# Visualize the simulations results
def sumComboRate(comboRateByTurn):
    comboRate = 0
    for i in range(0,4):
        comboRate += comboRateByTurn[i]

    return comboRate
overallComboRate = ScoreCriteria(["ComboTurn"], sumComboRate)
visualizeResults(resultsDir, dimensions, overallComboRate, "Overall Combo Rate - Land v Treasure")

# Visualize T3 combo rate
def getT3Combo(comboRateByTurn):
    return comboRateByTurn[2]
t3ComboRate = ScoreCriteria(["ComboTurn"], getT3Combo)
visualizeResults(resultsDir, dimensions, t3ComboRate, "T3 Combo Rate - Land v Treasure")

# Visualize T4 combo rate
def getT4Combo(comboRateByTurn):
    return comboRateByTurn[3]
t4ComboRate = ScoreCriteria(["ComboTurn"], getT4Combo)
visualizeResults(resultsDir, dimensions, t4ComboRate, "T4 Combo Rate - Land v Treasure")

# Visualize Bomb Combo Rate
def getRawScore(score):
    return score
delayedRate = ScoreCriteria(["comboType", "Big Bomb"], getRawScore)
visualizeResults(resultsDir, dimensions, delayedRate, "Bomb Combo Rate - Land v Treasure")

# Visualize Midrange Combo Rate
def getRawScore(score):
    return score
delayedRate = ScoreCriteria(["comboType", "Midrange Card"], getRawScore)
visualizeResults(resultsDir, dimensions, delayedRate, "Midrange Combo Rate - Land v Treasure")

# Visualize Fizzle Rate
def getRawScore(score):
    return score
delayedRate = ScoreCriteria(["comboType", "Fizzle"], getRawScore)
visualizeResults(resultsDir, dimensions, delayedRate, "Fizzle Rate - Land v Treasure")

# Visualize No Combo Rate
def getRawScore(score):
    return score
delayedRate = ScoreCriteria(["comboType", "No Combo"], getRawScore)
visualizeResults(resultsDir, dimensions, delayedRate, "No Combo Rate - Land v Treasure")