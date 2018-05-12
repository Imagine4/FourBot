blank = "+"
black = "⚫"
white = "⚪"

letterorder = ("A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N",
               "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")


class GoGame:

    def __init__(self, size):

        self.boardsize = size
        self.board = [""] * size
        self.clump = set()
        self.previousmove = ""
        self.blackcaptures = 0
        self.whitecaptures = 0
        self.blackterritory = 0
        self.whiteterritory = 0
        self.gamenotfinished = True

        for i in range(size):
            self.board[i] = [blank] * size

    def printboard(self, inputboard):
        counter = 0
        boardtoprint = "   " + " ".join(letterorder[:self.boardsize])

        for row in inputboard:
            counter += 1
            boardtoprint += ("\n" + str(counter)
                             + (" " * (3 - len(str(counter)))) + " ".join(row))
            return boardtoprint

    def opposite(self, currentplayer):
        if currentplayer == black:
            return white
        elif currentplayer == white:
            return black
        else:
            return blank

    def processcoords(self, rawcoords):
        if type(rawcoords) == str:
            return letterorder.index(rawcoords[0].upper()), int(rawcoords[1:]) - 1
        else:
            return rawcoords

    def getcolor(self, coords, outofrange=blank):
        """
        Edge case handling. Counts edges as whatever outofrange is.
        Useful for handling captures.
        """
        if 0 <= coords[0] < self.boardsize and 0 <= coords[1] < self.boardsize:
            return self.board[coords[1]][coords[0]]
        else:
            return outofrange

    def placedown(self, rawcoords, colortoplace):
        coords = self.processcoords(rawcoords)
        color = self.getcolor(coords)

        if color == blank or colortoplace == blank:
            self.board[coords[1]][coords[0]] = colortoplace

        return coords

    def findadjacent(self, coords):
        adjacents = []

        for xdirection in (-1, 1):
            adjacents.append((coords[0] + xdirection, coords[1]))

        for ydirection in (-1, 1):
            adjacents.append((coords[0], coords[1] + ydirection))

        return adjacents

    def checkifsurrounded(self, vulnerableplace, surroundedby):
        """
        vulnerableplace is a location in the area that is being check
        if it is surrounded by the string surroundedby
        """

        self.clump.clear()
        self.clump.add(vulnerableplace)
        placestocheck = [vulnerableplace]

        while len(placestocheck) > 0:

            currentplace = placestocheck[0]  # stacks?
            placestocheck.remove(currentplace)
            adjacents = self.findadjacent(currentplace)

            for adjplace in adjacents:
                color = self.getcolor(adjplace, surroundedby)

                if color != surroundedby and color != self.getcolor(vulnerableplace):
                    self.clump.clear()
                    return False

                if color == self.board[vulnerableplace[1]][vulnerableplace[0]]:
                    if adjplace not in self.clump:
                        self.clump.add(adjplace)
                        placestocheck.append(adjplace)
        else:
            return True

    def nextmove(self, player, moveinput):

        oppositeplayer = self.opposite(player)

        if not moveinput == "skip":
            try:
                move = self.placedown(moveinput, player)

                for adjcoords in self.findadjacent(move):
                    adjcolor = self.getcolor(adjcoords)
                    if adjcolor == oppositeplayer:
                        self.clump.clear()
                        if self.checkifsurrounded(adjcoords, player):
                            for stone in self.clump:
                                if player == black:
                                    self.blackcaptures += 1
                                if player == white:
                                    self.whitecaptures += 1
                                self.placedown(stone, blank)
                            break
            except ValueError:
                pass

        if self.previousmove == "skip" and moveinput == "skip":
            print()
            self.gamenotfinished = False

            checkedblanks = []

            for index0, row in enumerate(self.board):
                for index1, spot in enumerate(row):
                    if spot == blank and (index0, index1) not in checkedblanks:

                        if self.checkifsurrounded((index0, index1), black):
                            for place in self.clump:
                                checkedblanks.append(place)
                            self.blackterritory += len(self.clump)

                        if self.checkifsurrounded((index0, index1), white):
                            for place in self.clump:
                                checkedblanks.append(place)
                            self.whiteterritory += len(self.clump)

        self.previousmove = moveinput

