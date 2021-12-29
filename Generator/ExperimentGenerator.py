from Core.CardClasses import *
from Core.CardClasses import *
from Core.Zones import *
from Core.GameState import *

import os
import sys
import json
import itertools

PATH_TO_EXPERIMENT_SEED = "../Decks/Deck_Seed_No Omniscience.json"
WHERE_TO_GENERATE_EXPERIMENTS = "../Experiments/Throes Combo - Omniscience"
NUM_CARDS_IN_DECK = 60

# Read in the starting deck seed
expObject = json.load(open(PATH_TO_EXPERIMENT_SEED))
decklist = expObject["decklist"]
constraints = expObject["config"]["constraints"]

# Grab dimensions to permute, then brute force through every permutation.
# For each permutation that results in a 60 card deck make an experiment file.
bombrange = [* range(constraints["Big Bomb"][0], (constraints["Big Bomb"][1] + 1))]
landrange = [* range(constraints["Land"][0], (constraints["Land"][1] + 1))]
treasurerange = [* range(constraints["Treasure Maker"][0], (constraints["Treasure Maker"][1] + 1))]
permutations = itertools.product(bombrange, landrange, treasurerange)

deckcount = 0
for item in permutations:
    if sum(item) == 53:
        expObject["decklist"]["Big Bomb"]["num"] = item[0]
        expObject["decklist"]["Land"]["num"] = item[1]
        expObject["decklist"]["Treasure Maker"]["num"] = item[2]

        expObject["config"]["dimensions"]["Big Bomb"] = item[0]
        expObject["config"]["dimensions"]["Land"] = item[1]
        expObject["config"]["dimensions"]["Treasure Maker"] = item[2]

        # Save results summary to file in a directory structure that mirrors the experiment structure
        deckcount += 1
        resultsFilePath = WHERE_TO_GENERATE_EXPERIMENTS + "/deck_" + str(deckcount)
        resultsDir = os.path.dirname(resultsFilePath)
        if not os.path.isdir(resultsDir):
            os.makedirs(resultsDir)
        with open(resultsFilePath, "w+") as resultsFile:
            json.dump(expObject, resultsFile, indent=4)