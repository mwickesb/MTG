import json

class ScoreCriteria(object):

    # index - list of dictionary keys to traverse in the results.json to get to the value to calculate
    # calcValue - A function that scores the indexed value
    def __init__(self, index, calcValue):
        self.index = index
        self.calcValue = calcValue

    def scoreResultFile(self, resultFilePath):
        result = json.load(open(resultFilePath))
        return self.scoreResult(result)

    def scoreResult(self, result):
        indexedValue = {}
        for resultKey in self.index:
            indexedValue = result[resultKey]

        return self.calcValue(indexedValue)

    def __str__(self):
        return "Scoring via these indices - " + str(self.index)