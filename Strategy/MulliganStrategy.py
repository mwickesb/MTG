# Types needed is a dictionary of card types and the minimum number of cards needed of that type
def mullBasedNeededTypes(hand, typesNeeded):

    typesFound = {}
    shouldKeep = True

    # Count card types in hand
    for card in hand.card_list:
        if card.card_type in typesFound:
            typesFound[card.card_type] += 1
        else:
            typesFound[card.card_type] = 1

    # See if the desired amount of cards was found
    for type, numNeeded in typesNeeded.items():

        minNeeded = numNeeded[0]
        maxNeeded = numNeeded[1]

        if type != "OTHER":
            if type not in typesFound:
                shouldKeep = False
                break
            else:
                if (typesFound[type] < minNeeded) or (typesFound[type] > maxNeeded):
                    shouldKeep = False
                    break
        else:
            #TODO - Implement this check later
            continue

    return not shouldKeep