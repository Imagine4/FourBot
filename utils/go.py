from PIL import Image
import io
from utils import conversions

blank = "·"
black = ":black_circle:"
white = ":white_circle:"

letterorder = ("A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N",
               "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA")


class GoGame:
    def __init__(self, size, p1, p2, name):
        self.size = size
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
        self.name = name
        self.movehistory = []
        self.potentialremoves = {}
        self.gamenotfinished = True

        for i in range(size):
            self.board[i] = [blank] * size

    @staticmethod
    def findadjacent(coords):
        adjacents = []

        for xdirection in (-1, 1):
            adjacents.append((coords[0] + xdirection, coords[1]))

        for ydirection in (-1, 1):
            adjacents.append((coords[0], coords[1] + ydirection))

        return adjacents

    def importgame(self, board, turn, blackcapts, whitecapts):
        self.blackcaptures = blackcapts
        self.whitecaptures = whitecapts
        self.turn = turn
        self.size = len(board)
        self.board = board

    def encodeboard(self):
        return conversions.encodeboard(self.board, self.turn, self.blackcaptures, self.whitecaptures)

    def printboard(self):
        board = self.board
        size = self.size
        margin = 20
        gdim = (size - 1) * 12 + 1
        idim = gdim + 2 * margin

        boardimg = Image.open(f"utils/sprites/boards/board{self.size}.png")
        stones = Image.new("RGBA", (idim, idim))
        bstone = Image.open("utils/sprites/blackstone.png")
        wstone = Image.open("utils/sprites/whitestone.png")

        for i, row in enumerate(board):
            for j, point in enumerate(row):
                if point == white:
                    box = (j * 10 + (margin - 4), i * 10 + (margin - 4))
                    stones.alpha_composite(wstone, box)
                if point == black:
                    box = (j * 10 + (margin - 4), i * 10 + (margin - 4))
                    stones.alpha_composite(bstone, box)

        boardimg.alpha_composite(stones.resize((idim * 4, idim * 4), Image.NEAREST))

        file = io.BytesIO()
        boardimg.save(file, format="PNG")
        file.seek(0)
        return file

    def opposite(self):
        if self.turn == black:
            return white
        elif self.turn == white:
            return black
        else:
            return blank

    def processcoords(self, rawcoords):
        if type(rawcoords) == str:
            return letterorder.index(rawcoords[0].upper()), self.size - int(rawcoords[1:])
        else:
            return rawcoords

    def getcolor(self, coords, board, outofrange=blank):
        """
        Edge case handling. Counts edges as whatever outofrange is.
        Useful for handling captures.
        """
        if 0 <= coords[0] < self.size and 0 <= coords[1] < self.size:
            return board[coords[1]][coords[0]]
        else:
            return outofrange

    def placedown(self, theboard, coords, colortoplace):
        color = self.getcolor(coords, theboard)

        if color == blank or colortoplace == blank:
            theboard[coords[1]][coords[0]] = colortoplace
        else:
            return theboard, False

        return theboard, True

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

    def remstones(self, coords, capture=True):
        self.clump.clear()
        self.clump.add(coords)
        placestocheck = [coords]
        capcolor = self.getcolor(coords, self.board)

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
            if capture:
                if capcolor == black:
                    self.whitecaptures += 1
                if capcolor == white:
                    self.blackcaptures += 1
            self.placedown(self.board, place, blank)

    def calculateterritory(self):
        checkedblanks = []

        for index1, row in enumerate(self.board):
            for index0, spot in enumerate(row):
                if spot == blank and (index0, index1) not in checkedblanks:

                    if self.checkifsurrounded((index0, index1), black, self.board):
                        for place in self.clump:
                            checkedblanks.append(place)
                        self.blackterritory += len(self.clump)

                    if self.checkifsurrounded((index0, index1), white, self.board):
                        for place in self.clump:
                            checkedblanks.append(place)
                        self.whiteterritory += len(self.clump)  # optimize

    def nextmove(self, moveinput):
        player = self.turn
        oppplayer = self.opposite()
        self.previousturn = self.turn

        if moveinput in ["skip", "pass"]:
            self.turn = oppplayer

            if self.previousmove in ["skip", "pass"]:
                self.gamenotfinished = False

            self.previousmove = moveinput

            self.movehistory.append(moveinput)
            return "ok"

        else:
            move = self.processcoords(moveinput)
            if move[0] > self.size or 0 > move[0] or move[1] > self.size or 0 > move[1]:
                return "outofrange"

            tempboard = [i[:] for i in self.board]
            tempboard = self.placedown(tempboard, move, player)

            if tempboard[1] is False:
                return "occupied"

            tempboard = tempboard[0]

            captures = 0

            for adjcoords in self.findadjacent(move):

                adjcolor = self.getcolor(adjcoords, tempboard)
                self.clump.clear()

                if adjcolor == oppplayer:

                    if self.checkifsurrounded(adjcoords, player, tempboard):

                        for stone in self.clump:
                            tempboard = self.placedown(tempboard, stone, blank)[0]
                            captures += 1

            if len(self.clump) == 0:
                if self.checkifsurrounded(move, oppplayer, tempboard):
                    return "suicide"

            if tempboard == self.boardbeforelast:
                return "ko"
            else:
                if player == black:
                    self.blackcaptures += captures
                if player == white:
                    self.whitecaptures += captures

                self.board = tempboard

                self.previousmove = moveinput
                self.turn = self.opposite()

                if self.previousmove not in ["skip", "pass"]:
                    self.boardbeforelast = [i[:] for i in self.previousboard]
                    self.previousboard = [i[:] for i in self.board]

                self.movehistory.append(move)
                return "ok"
