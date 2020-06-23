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
def runSimulations(experimentDirectory, typesNeeded, numGames, playTurn, playGame, recordGameResult, recordSimulationSummary):
    pathToExperiments = PATH_TO_EXPERIMENTS + "/" + experimentDirectory
    pathToResults = PATH_TO_RESULTS + "/" + experimentDirectory

    # Calculate all permutations of simulations
    # experiments[i][0] - The Decklist of the i'th simulation to run
    # experiments[i][1] - The results of the i'th simulation
    experiments = []
    for root, directories, filenames in os.walk(pathToExperiments):
        for filename in filenames:
            decklistFilePath = root + "/" + filename
            resultsFilePath = decklistFilePath.replace(pathToExperiments,pathToResults)
            experiments.append([decklistFilePath, resultsFilePath])

    # Calculate number of runs to complete 1/10th of a sim
    oneTenthChunk = 10
    if (numGames > 100):
        oneTenthChunk = int(numGames/10)

    # Run a simulation for every experiment decklist in the experiments director
    for expIndex, experiment in enumerate(experiments):

        # Import a Deck and draw a fresh hand
        (library, config) = importDeck(experiment[0])
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

            result = recordGameResult(gamestate)
            result[MULL_COUNT] = numMull
            result[TOTAL_DAMAGE] = 20 - gamestate.opponentsLife
            game_results.append(result)

        print("] -",round((expIndex+1)/len(experiments),3))
        sys.stdout.flush()

        resultsSummary = recordSimulationSummary(game_results, numGames)
        resultsSummary["config"] = config

        # Save results summary to file in a directory structure that mirrors the experiment structure
        resultsFilePath = experiment[1]
        resultsDir = os.path.dirname(resultsFilePath)
        if not os.path.isdir(resultsDir):
            os.makedirs(resultsDir)
        with open(resultsFilePath, "w+") as resultsFile:
            json.dump(resultsSummary, resultsFile)

def visualizeResults(resultsDirectory, dimensions, scoreCriteria, title):

    # Generate scores in a matrix
    # scores[sealDim][wrathDim]
    scores = np.zeros((100, 100))
    dimMin = {}
    dimMax = {}

    # Find all permutations of results to use for the visualization
    scoreRecords = []
    isFirstPass = True
    for root, directories, filenames in os.walk(resultsDirectory):
        for filename in filenames:
            resultPath = root + "/" + filename

            # Associate a score with the requested dimensions, this info is in the config section of the results file
            result = json.load(open(resultPath))

            resultIdx = result["config"]["dimensions"]
            dim1 = resultIdx[dimensions[0]]
            dim2 = resultIdx[dimensions[1]]
            score = round(scoreCriteria.scoreResult(result),3)
            scores[dim1][dim2] = score

            scoreRecords.append({
                "dimensions" : resultIdx,
                "result" : result,
                "score" : score
            })

            if isFirstPass:
                isFirstPass = False
                dimMin[dimensions[0]] = dim1
                dimMin[dimensions[1]] = dim2
                dimMax[dimensions[0]] = dim1
                dimMax[dimensions[1]] = dim2
            else:
                dimMin[dimensions[0]] = min(dimMin[dimensions[0]], dim1)
                dimMin[dimensions[1]] = min(dimMin[dimensions[1]], dim2)
                dimMax[dimensions[0]] = max(dimMax[dimensions[0]], dim1)
                dimMax[dimensions[1]] = max(dimMax[dimensions[1]], dim2)

    # Slice the scores matrix into the proper ranges
    d1Min = dimMin[dimensions[0]]
    d1Max = dimMax[dimensions[0]]
    d2Min = dimMin[dimensions[1]]
    d2Max = dimMax[dimensions[1]]
    scores = scores[d1Min:(d1Max + 1), d2Min:(d2Max + 1)]

    # Construct axis titles
    rowTitles = []
    colTitles = []
    for row in range(d1Min, (d1Max + 1)):
        rowPrefix = dimensions[0].split()[0]
        rowTitles.append(rowPrefix + " = " + str(row))

    for col in range(d2Min, (d2Max + 1)):
        colPrefix = dimensions[1].split()[0]
        colTitles.append(colPrefix + " = " + str(col))

    fig, ax = plt.subplots()
    im = ax.imshow(scores)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(colTitles)))
    ax.set_yticks(np.arange(len(rowTitles)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(colTitles)
    ax.set_yticklabels(rowTitles)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(rowTitles)):
        for j in range(len(colTitles)):
            text = ax.text(j, i, scores[i, j],
                           ha="center", va="center", color="w")

    ax.set_title(title)
    fig.tight_layout()
    plt.show()