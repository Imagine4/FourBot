boardsize = int(input("Enter board size: "))
board = [""] * boardsize
blank = "-"  # "🔵"
black = "b"  # "⚫"
white = "w"  # "⚪"
gamenotfinished = True
previousmove = ""
whitecaptures = 0
blackcaptures = 0
whiteterritory = 0
blackterritory = 0

letterorder = ("A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N",
               "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")

for i in range(boardsize):
    board[i] = [blank] * boardsize


def opposite(currentplayer):
    if currentplayer == black:
        return white
    elif currentplayer == white:
        return black
    else:
        return blank


def printboard(inputboard):
    counter = 0
    print("   " + " ".join(letterorder[:boardsize]))

    for row in inputboard:
        counter += 1
        print(str(counter) + (" " * (3 - len(str(counter)))) + " ".join(row))


def processcoords(rawcoords):
    if type(rawcoords) == str:
        return letterorder.index(rawcoords[0].upper()), int(rawcoords[1:]) - 1
    else:
        return rawcoords


def getcolor(coords, outofrange=blank):
    if 0 <= coords[0] < boardsize and 0 <= coords[1] < boardsize:
        return board[coords[1]][coords[0]]
    else:
        return outofrange
    # Edge-case handling. Counts edges as a stone of current player
    # Useful for handling captures.


def placedown(rawcoords, colortoplace):
        coords = processcoords(rawcoords)
        color = getcolor(coords)

        if color == blank or player == blank:
            board[coords[1]][coords[0]] = colortoplace

        return coords


def findadjacent(coords):
    adjacents = []

    for xdirection in (-1, 1):
        adjacents.append((coords[0] + xdirection, coords[1]))

    for ydirection in (-1, 1):
        adjacents.append((coords[0], coords[1] + ydirection))

    return adjacents


def checkifsurrounded(vulnerableplace, surroundedby):

    '''vulnerableplace is a location in the area that is being check
    if it is surrounded by the string "surroundedby"'''

    clump.clear()
    clump.add(vulnerableplace)
    placestocheck = [vulnerableplace]

    while len(placestocheck) > 0:

        currentplace = placestocheck[0]  # stacks?
        placestocheck.remove(currentplace)
        adjacents = findadjacent(currentplace)

        for adjplace in adjacents:
            color = getcolor(adjplace, surroundedby)

            if color != surroundedby and color != getcolor(vulnerableplace):
                clump.clear()
                return False

            if color == board[vulnerableplace[1]][vulnerableplace[0]]:
                if adjplace not in clump:
                    clump.add(adjplace)
                    placestocheck.append(adjplace)
    else:
        return True


printboard(board)


while gamenotfinished:
    for player in (black, white):

        oppositeplayer = opposite(player)
        clump = set()

        if player == black:
            print("Black's turn")
        else:
            print("White's turn")

        moveinput = input('Enter your move, or "skip" to skip turn: ')

        if not moveinput == "skip":

            # Updates board to have piece while assigning coords
            try:
                move = placedown(moveinput, player)

                for adjcoords in findadjacent(move):
                    adjcolor = getcolor(adjcoords)
                    if adjcolor == oppositeplayer:
                        clump.clear()
                        if checkifsurrounded(adjcoords, oppositeplayer):
                            for stone in clump:
                                if player == black:
                                    blackcaptures += 1
                                if player == white:
                                    whitecaptures += 1
                                placedown(stone, blank)
                            break
            except ValueError:
                pass

        # Ends turn
        if previousmove == "skip" and moveinput == "skip":
            print()
            gamenotfinished = False

            checkedblanks = []

            for index0, row in enumerate(board):
                for index1, spot in enumerate(row):
                    if spot == blank and (index0, index1) not in checkedblanks:

                        if checkifsurrounded((index0, index1), black):
                            for place in clump:
                                checkedblanks.append(place)
                            blackterritory += len(clump)

                        if checkifsurrounded((index0, index1), white):
                            for place in clump:
                                checkedblanks.append(place)
                            whiteterritory += len(clump)

            print("Black's captures: " + str(blackcaptures))
            print("Black's territory: " + str(blackterritory))
            print("White's captures: " + str(whitecaptures))
            print("White's territory: " + str(whiteterritory))

            if blackcaptures + blackterritory > whitecaptures + whiteterritory:
                print("Winner: Black")
            elif blackcaptures < whitecaptures:
                print("Winner: White")
            else:
                print("Tie")
            break

        previousmove = moveinput

        printboard(board)
