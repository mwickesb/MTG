import uuid

class Card(object):  # superclass of "Card" - every card inherits these attributes

    def __init__(self, name, card_type, mana_cost):
        self.name = name  # Spell Name
        self.card_type = card_type  # Card Type - initialized in subclass
        self.mana_cost = mana_cost  # Converted mana cost
        self.UUID = uuid.uuid4()  # Create unique card ID

    def __str__(self):
        return "%s, %s, %s, %s" % (self.name, self.card_type, self.mana_cost, self.UUID)


class Land(Card):  # subclass "Land"

    def __init__(self, name, mana_out):
        Card.__init__(self, name, "Land", 0)  # initializes it as a "Card"
        self.mana_out = mana_out  # mana_out represents the amount of mana produced


class Creature(Card):  # subclass "Creature"

    def __init__(self, name, mana_cost, power, toughness, abilities, haste=False):
        Card.__init__(self, name, "Creature", mana_cost)
        self.abilities = buildAbility(abilities)
        self.power = power
        self.toughness = toughness
        self.haste = haste
        if haste:
            self.turns = 1  # self.turns = # of turns the creature in play. set to 1 for creatures with haste
        else:
            self.turns = 0  # and 0 for creatures without haste. the attack function will check this


class Instant(
    Card):  # subclass "Instant" - maybe we should change this to 'spell' - no need to differentiate instants and sorceries

    def __init__(self, name, mana_cost, ability):
        Card.__init__(self, name, "Instant", mana_cost)
        self.ability = buildAbility(ability)  #


class Artifact(Card):  # subclass "Artifact"

    def __init__(self, name, mana_cost, abilities):
        Card.__init__(self, name, "Artifact", mana_cost)
        self.abilities = buildAbility(abilities)


class Ability(object):
    def __init__(self, ability, value, cost):
        self.ability = ability
        self.value = value
        self.cost = cost

    def __str__(self):
        return "%s : %s %s" % (self.cost, self.ability, self.value)

def buildAbility(string):
    if string != '':
        abil = string.strip().split(':')
        return Ability(abil[1], int(abil[2]), abil[0])
    else:
        return None