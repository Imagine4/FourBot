boardsize = int(input("Enter board size: "))
board = [""] * boardsize
blank = "-"  # "🔵"
black = "b"  # "⚫"
white = "w"  # "⚪"
gamenotfinished = True
previousmove = ""
whitecaptures = 0
blackcaptures = 0

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


def getcolor(coords):
    if 0 <= coords[0] < boardsize and 0 <= coords[1] < boardsize:
        return board[coords[1]][coords[0]]
    else:
        return player
    # Edge-case handling. Counts edges as a stone of current player
    # Useful for handling captures.


def placedown(rawcoords, player):
        coords = processcoords(rawcoords)
        color = getcolor(coords)

        if color == blank or player == blank:
            board[coords[1]][coords[0]] = player

        return coords


def findadjacent(coords):
    adjacents = []

    for xdirection in (-1, 1):
        adjacents.append((coords[0] + xdirection, coords[1]))

    for ydirection in (-1, 1):
        adjacents.append((coords[0], coords[1] + ydirection))

    return adjacents


def checkifcaptured(vulnerableplace):

    megastone.add(vulnerableplace)
    currentstone = vulnerableplace
    stonestocheck = [vulnerableplace]

    while len(stonestocheck) > 0:

        stonestocheck.remove(currentstone)
        adjacents = findadjacent(currentstone)

        for adjplace in adjacents:
            color = getcolor(adjplace)

            if color == blank:
                return False

            if color == opposite(player):
                if adjplace not in megastone:
                    megastone.add(adjplace)
                    stonestocheck.append(adjplace)

        if len(stonestocheck) != 0:
            currentstone = stonestocheck[0]  # stacks?

    else:
        return True


printboard(board)

while gamenotfinished:
    for player in (black, white):

        oppositeplayer = opposite(player)
        megastone = set()

        if player == black:
            print("Black's turn")
        else:
            print("White's turn")

        moveinput = input('Enter your move, or "skip" to skip turn: ')

        if not moveinput == "skip":

            # Updates board to have piece while assigning coords
            move = placedown(moveinput, player)

            for adjcoords in findadjacent(move):
                adjcolor = getcolor(adjcoords)
                if adjcolor == oppositeplayer:
                    megastone.clear()
                    if checkifcaptured(adjcoords):
                        for stone in megastone:
                            if player == black:
                                blackcaptures += 1
                            if player == white:
                                whitecaptures += 1
                            placedown(stone, blank)
                        break

        # Ends turn
        if previousmove == "skip" and moveinput == "skip":
            print()
            gamenotfinished = False

            print("Black's captures: " + str(blackcaptures))
            print("White's captures: " + str(whitecaptures))

            

            if blackcaptures > whitecaptures:
                print("Winner: Black")
            elif blackcaptures < whitecaptures:
                print("Winner: White")
            else:
                print("Tie")
            break

        previousmove = moveinput

        printboard(board)
