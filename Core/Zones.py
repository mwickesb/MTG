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
