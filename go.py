blank = "·"
black = "○"
white = "●"

letterorder = ("A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N",
               "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA")


class GoGame:

    def __init__(self, size, p1, p2):

        self.boardsize = size
        self.board = [""] * size
        self.clump = set()
        self.previousmove = ""
        self.turn = black
        self.previousturn = white
        self.previousboard = []
        self.boardbeforelast = []
        self.blackcaptures = 0
        self.whitecaptures = 0
        self.blackterritory = 0
        self.whiteterritory = 0
        self.p1 = p1
        self.p2 = p2
        self.potentialremoves = []
        self.gamenotfinished = True

        for i in range(size):
            self.board[i] = [blank] * size

    def printboard(self, inputboard=None):
        if inputboard == None: inputboard = self.board
        starpoints = []
        boardcopy = [i[:] for i in inputboard]

        if self.boardsize == 19:
            starpoints = [(3, 3), (3, 9), (3, 15),
                          (9, 3), (9, 9), (9, 15),
                          (15, 3), (15, 9), (15, 15)]
        elif self.boardsize == 13:
            starpoints = [(3, 3), (3, 9),
                          (6, 6),
                          (9, 3), (9, 9)]
        elif self.boardsize == 9:
            starpoints = [(2, 2), (2, 6),
                          (4, 4),
                          (6, 2), (6, 6)]

        if starpoints is not []:
            for point in starpoints:
                boardcopy = self.placedown(boardcopy, point, "+")

        boardtoprint = "   " + " ".join(letterorder[:self.boardsize])
        counter = self.boardsize

        for row in boardcopy:
            boardtoprint += ("\n" + (" " * (2 - len(str(counter))))
                             + str(counter) + " " + " ".join(row))
            counter -= 1

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
            return letterorder.index(rawcoords[0].upper()), self.boardsize - int(rawcoords[1:])
        else:
            return rawcoords

    def getcolor(self, coords, board, outofrange=blank):
        """
        Edge case handling. Counts edges as whatever outofrange is.
        Useful for handling captures.
        """
        if 0 <= coords[0] < self.boardsize and 0 <= coords[1] < self.boardsize:
            return board[coords[1]][coords[0]]
        else:
            return outofrange

    def placedown(self, theboard, coords, colortoplace):
        color = self.getcolor(coords, theboard)

        if color == blank or colortoplace == blank:
            theboard[coords[1]][coords[0]] = colortoplace
        else:
            return False

        return theboard

    def findadjacent(self, coords):
        adjacents = []

        for xdirection in (-1, 1):
            adjacents.append((coords[0] + xdirection, coords[1]))

        for ydirection in (-1, 1):
            adjacents.append((coords[0], coords[1] + ydirection))

        return adjacents

    def checkifsurrounded(self, vulnerableplace, surroundedby, board):
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
                color = self.getcolor(adjplace, board, surroundedby)

                if color != surroundedby and color != self.getcolor(vulnerableplace, board):
                    self.clump.clear()
                    return False

                if color == board[vulnerableplace[1]][vulnerableplace[0]]:
                    if adjplace not in self.clump:
                        self.clump.add(adjplace)
                        placestocheck.append(adjplace)
        else:
            return True

    def remstones(self, coords):

        self.clump.clear()
        self.clump.add(coords)
        placestocheck = [coords]

        while len(placestocheck) > 0:

            currentplace = placestocheck[0]
            placestocheck.remove(currentplace)
            adjacents = self.findadjacent(currentplace)

            for adjplace in adjacents:
                color = self.getcolor(adjplace, self.board)

                if color == self.board[coords[1]][coords[0]]:
                    if adjplace not in self.clump:
                        self.clump.add(adjplace)
                        placestocheck.append(adjplace)

        for place in self.clump:
            self.placedown(self.board, place, blank)

        checkedblanks = []

        for index0, row in enumerate(self.board):
            for index1, spot in enumerate(row):
                if spot == blank and (index0, index1) not in checkedblanks:

                    if self.checkifsurrounded((index0, index1), black, self.board):
                        for place in self.clump:
                            checkedblanks.append(place)
                        self.blackterritory += len(self.clump)

                    if self.checkifsurrounded((index0, index1), white, self.board):
                        for place in self.clump:
                            checkedblanks.append(place)
                        self.whiteterritory += len(self.clump)  # optimize

    def nextmove(self, player, moveinput):

        oppplayer = self.opposite(player)
        self.previousturn = self.turn

        if moveinput == "skip":
            self.turn = oppplayer

            if self.previousmove == "skip":
                self.gamenotfinished = False

            self.previousmove = moveinput

            return "ok"

        else:
            move = self.processcoords(moveinput)
            tempboard = [i[:] for i in self.board]
            tempboard = self.placedown(tempboard, move, player)

            if tempboard is False:
                return "occupied"

            for adjcoords in self.findadjacent(move):
                adjcolor = self.getcolor(adjcoords, tempboard)
                self.clump.clear()

                if adjcolor == oppplayer:

                    if self.checkifsurrounded(adjcoords, player, tempboard):

                        for stone in self.clump:
                            tempboard = self.placedown(tempboard, stone, blank)
            else:

                if self.checkifsurrounded(move, oppplayer, tempboard):
                    return "suicide"

            if tempboard == self.boardbeforelast:
                return "ko"
            else:
                for stone in self.clump:
                    if player == black:
                        self.blackcaptures += 1
                    if player == white:
                        self.whitecaptures += 1

                self.board = tempboard

                self.previousmove = moveinput
                self.turn = self.opposite(self.turn)

                if self.previousmove is not "skip":
                    self.boardbeforelast = [i[:] for i in self.previousboard]
                    self.previousboard = [i[:] for i in self.board]

                return "ok"
