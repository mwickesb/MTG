from Core.CardClasses import *
from Core.Zones import *
from Core.GameState import *
from Strategy.MulliganStrategy import *

import os
import sys
import json

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

PATH_TO_EXPERIMENTS = "../Experiments"
PATH_TO_RESULTS = "../Results"
FILE_NAME = "../Decks/AggroDeck.json"

# A list of lists with the following structure
# game_results[i] = the i'th simulated game
# game_results[i][MULL_COUNT] = Mulligan count
# game_results[i][COMBO_TURN] = The combo turn
# game_results[i][COMBO_TYPE] = The combo type
# game_results[1][TOTAL_DAMAGE] = Total damage dealt in game
game_results = []
MULL_COUNT = "MULL_COUNT"
COMBO_TURN = "COMBO_TURN"
COMBO_TYPE = "COMBO_TYPE"
TOTAL_DAMAGE = "TOTAL_DAMAGE"

# Runs through a directory of simulation experiments and saves results
def runSimulations(experimentDirectory, typesNeeded, numGames, playTurn, playGame):
    pathToExperiments = PATH_TO_EXPERIMENTS + "/" + experimentDirectory
    pathToResults = PATH_TO_RESULTS + "/" + experimentDirectory

    # Calculate all permutations of simulations
    experiments = []
    for root, directories, filenames in os.walk(pathToExperiments):
        for filename in filenames:
            decklistFilePath = root + "/" + filename
            resultsFilePath = decklistFilePath.replace(pathToExperiments,pathToResults)
            experiments.append([decklistFilePath, resultsFilePath])

    oneTenthChunk = 10
    if (numGames > 100):
        oneTenthChunk = int(numGames/10)

    # Run a simulation for every experiment decklist in the experiments director
    for expIndex, experiment in enumerate(experiments):

        # Import a Deck and draw a fresh hand
        library = importDeck(experiment[0])
        game_results = []

        # Simulation loop
        print("Starting Simulation...[", end='')
        sys.stdout.flush()
        for gamecount in range(numGames):

            # Give an update status of simulation in progress
            if gamecount % oneTenthChunk == 0:
                print("#", end='')
                sys.stdout.flush()

            # Resolve mulligans
            gamestate = mullToNeededTypes(library, typesNeeded)
            numMull = 7 - len(gamestate.hand.card_list)
            playGame(gamestate, playTurn)

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
        print("] -",round((expIndex+1)/len(experiments),3))
        sys.stdout.flush()

        # Calculate result summary statistics
        countKeeps = sum(map(lambda result : result[MULL_COUNT] == 0, game_results))
        count1Mull = sum(map(lambda result : result[MULL_COUNT] == 1, game_results))
        count2Mull = sum(map(lambda result : result[MULL_COUNT] == 2, game_results))
        countT2Combo = sum(map(lambda result : result[COMBO_TURN] == 2, game_results))
        countT3Combo = sum(map(lambda result : result[COMBO_TURN] == 3, game_results))
        countCT_Miracle = sum(map(lambda result : result[COMBO_TYPE] == "Miracle", game_results))
        countCT_DelayedBurn = sum(map(lambda result : result[COMBO_TYPE] == "Delayed Burn", game_results))
        countCT_DoubleBolt = sum(map(lambda result : result[COMBO_TYPE] == "Double Bolt Burn", game_results))
        totalCombos = countCT_Miracle + countCT_DelayedBurn + countCT_DoubleBolt
        resultsSummary = {
            "WinningTurn" : -1,
            "ComboTurn" : [0,round(countT2Combo / numGames,3),round(countT3Combo / numGames,3)],
            "mulligans" : [round(countKeeps / numGames,3), round(count1Mull / numGames,3),round(count2Mull / numGames,3)],
            "comboType" : {
                "Miracle" : round(countCT_Miracle / totalCombos,3),
                "Delayed Burn" : round(countCT_DelayedBurn / totalCombos,3),
                "Double Bolt" : round(countCT_DoubleBolt / totalCombos,3)
            }
        }

        # Save results summary to file in a directory structure that mirrors the experiment structure
        resultsFilePath = experiment[1]
        resultsDir = os.path.dirname(resultsFilePath)
        if not os.path.isdir(resultsDir):
            os.makedirs(resultsDir)
        with open(resultsFilePath, "w+") as resultsFile:
            json.dump(resultsSummary, resultsFile)

        # print("")
        # print('Percent 7 card hands:\t' + str(round(countKeeps / numGames,3)))
        # print('Percent Mull to 6   :\t' + str(round(count1Mull / numGames,3)))
        # print('Percent Mull to 5   :\t' + str(round(count2Mull / numGames,3)))
        # print('')
        # print('Percent  T2 Incinerator:\t' + str(round(countT2Combo / numGames,3)))
        # print('Percent  T3 Incinerator:\t' + str(round(countT3Combo / numGames,3)))
        # print('')
        # print('Total Combos                :\t' + str(totalCombos))
        # print('Percent  Miracle Combos     :\t' + str(round(countCT_Miracle / totalCombos,3)))
        # print('Percent  Delayed Burn Combos:\t' + str(round(countCT_DelayedBurn / totalCombos,3)))
        # print('Percent  Double Bolt Combos :\t' + str(round(countCT_DoubleBolt / totalCombos,3)))

def visualizeResults(resultsDirectory, dimensions, scoreCriteria):

    # Generate scores in a matrix
    # scores[sealDim][wrathDim]
    scores = np.zeros((5, 5))

    # Find all permutations of results to use for the visualization
    results = []
    for root, directories, filenames in os.walk(resultsDirectory):
        for filename in filenames:
            resultPath = root + "/" + filename

            #TODO - This is hardcoded to the Chandra's Incinerator experiments, broaden this soon
            tokens = filename.split("_")
            sealDim = int(tokens[1].rsplit(' ',1)[1])
            wrathDim = int(tokens[2].rsplit(' ',1)[1].split(".")[0])
            result = json.load(open(resultPath))

            score = round(scoreCriteria.scoreResult(result),3)
            scores[sealDim][wrathDim] = score

            results.append({
                "dimensions" : {"Seal of Fire": sealDim, "Thunderous Wrath": wrathDim},
                "result" : result,
                "score" : score
            })

    sealTitles = ["Seal = 0", "Seal = 1", "Seal = 2", "Seal = 3",
                  "Seal = 4"]
    wrathTitles = ["Wrath = 0", "Wrath = 1", "Wrath = 2",
               "Wrath = 3", "Wrath = 4"]

    fig, ax = plt.subplots()
    im = ax.imshow(scores)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(wrathTitles)))
    ax.set_yticks(np.arange(len(sealTitles)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(wrathTitles)
    ax.set_yticklabels(sealTitles)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(sealTitles)):
        for j in range(len(wrathTitles)):
            text = ax.text(j, i, scores[i, j],
                           ha="center", va="center", color="w")

    ax.set_title("Combo rate by varying Seals vs Wraths")
    fig.tight_layout()
    plt.show()