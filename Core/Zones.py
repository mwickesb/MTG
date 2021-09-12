from random import shuffle

class Zone: #Library, Hand, Graveyard, Battlefield, etc

    def __init__(self, name):
        self.name = name # The name for this zone
        self.card_list = []

    def addCard(self, card):
        self.card_list.append(card)

    def removeCard(self, index=0):
        return self.card_list.pop(index)

    def removeCardName(self, name):
        for i, c in enumerate(self.card_list):
            if c.name == name:
                return self.card_list.pop(i)

        return None

    def removeCardType(self, cardtype):
        for i, c in enumerate(self.card_list):
            if c.card_type == cardtype:
                return self.card_list.pop(i)

        return None

    # This will search for a card that meets a detailed condition
    # details - An array of dictionary objects.  Each dictionary describes a set AND conditions that must be met to return the card
    #           Each entry in the array describes an OR clause. I.e. if the first dictionary doesn't match any cards then we search by the next dictionary
    def removeCardByDetails(self, detailOptions):
        for details in detailOptions:
            for i, c in enumerate(self.card_list):
                numDetails = len(details)
                for j, d in enumerate(details):

                    # Checks for numbers or booleans
                    if isinstance(details[d], int):
                        if d not in c.properties:
                            break
                        if details[d] != c.properties[d]:
                            break
                        if (j == (numDetails - 1)) and (details[d] == c.properties[d]):
                            return self.card_list.pop(i)

                    # Checks for strings and sets
                    else:
                        if details[d] not in c.properties[d]:
                            break
                        if (j == (numDetails - 1)) and (details[d] in c.properties[d]):
                            return self.card_list.pop(i)

        return None

    def printCards(self):
        card_index = 1
        print("\nCards in %s zone" % self.name)
        print("---------------------------")
        for card in self.card_list:
            print("#%d.) Card Name: %s\t Card Type: %s\tMana Cost: %s" % (card_index, card.name, card.card_type, card.mana_cost))
            card_index += 1

    def shuffleCards(self):
        shuffle(self.card_list)

    def drawCards(self, hand, numCards):
        for i in range(numCards):
            hand.addCard(self.card_list.pop())

    def containsType(self, type, minNumNeeded=1, maxNumNeeded=1000):
        numFound = 0
        for card in self.card_list:
            if type == card.card_type:
                numFound += 1

        return (numFound >= minNumNeeded) and (numFound <= maxNumNeeded)

    def containsCard(self, name):
        numFound = 0
        for card in self.card_list:
            if name == card.name:
                numFound += 1

        return numFound

    # This will search for a card that meets a detailed condition
    # details - An array of dictionary objects.  Each dictionary describes a set AND conditions that must be met to return the card
    #           Each entry in the array describes an OR clause. I.e. if the first dictionary doesn't match any cards then we search by the next dictionary
    def containsCardByDetails(self, detailOptions):
        for details in detailOptions:
            for i, c in enumerate(self.card_list):
                numDetails = len(details)
                for j, d in enumerate(details):

                    # Checks for numbers or booleans
                    if isinstance(details[d], int):
                        if d not in c.properties:
                            break
                        if details[d] != c.properties[d]:
                            break
                        if (j == (numDetails - 1)) and (details[d] == c.properties[d]):
                            return True

                    # Checks for strings and sets
                    else:
                        if details[d] not in c.properties[d]:
                            break
                        if (j == (numDetails - 1)) and (details[d] in c.properties[d]):
                            return True

        return False
