from math import log, ceil

alph = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
symbols = {
    '0': '·',
    '1': "○",
    '2': "●"
}
encode_symbols = {v: k for k, v in symbols.items()}


def tobase(num, base):
    if num == 0: return ""
    return tobase(num // base, base) + alph[num % base]  # Milo gave me this. I don't know how it works.


def frombase(string, base):
    if string == "": return 0
    return frombase(string[:-1], base) * base + alph.index(string[-1])   # Milo gave me too electric boogaloo


def encodeboard(board, turn, blackcapts, whitecapts):

    trits = ""

    for row in board:
        for char in row:
            if char in encode_symbols:
                trits += encode_symbols[char]

    if turn == symbols['1']:
        trits += "1"
    else:
        trits += "2"

    trits += tobase(blackcapts, 3).rjust(8, "0")
    trits += tobase(whitecapts, 3).rjust(8, "0")

    dec = int(trits, 3)
    output = tobase(dec, 64)
    length = int(ceil((len(board)**2 + 1 + 2*8) * log(3) / log(64)))

    return output.rjust(length, "0")


def decodeboard(state):

    dec = frombase(state, 64)
    trits = tobase(dec, 3)
    # length = sqrt((len(state) * log(64) / log(3)) - 1 - 2*8)

    size = 1
    encryptsize = ceil((size ** 2 + 1 + 2 * 8) * log(3) / log(64))
    while encryptsize <= len(state):
        if encryptsize == len(state):
            break
        size += 1
        encryptsize = ceil((size ** 2 + 1 + 2 * 8) * log(3) / log(64))

    tritsnew = trits.rjust((size ** 2 + 1 + 2 * 8), "0")

    tritsboard = tritsnew[:size**2]
    tritsturn = tritsnew[size**2]
    tritswhite = tritsnew[size**2 + 1:size**2 + 9]
    tritsblack = tritsnew[size**2 + 9:]

    board = [[None] * size] * size

    for i, start in enumerate(range(0, size ** 2, size)):
        for j, spot in enumerate(tritsboard[start:(start + size)]):
            board[i][j] = symbols.get(spot)

    turn = '●'
    if tritsturn == "1":
        turn = '○'

    return board, turn, int(tritsblack, 3), int(tritswhite, 3)


def fromchat(rawboard, turn=-1, blackcapts=0, whitecapts=0):
    newstring = ""

    for char in rawboard:
        if not char.isalnum():
            newstring += char

    newstring = newstring.splitlines()[2:]
    board = [[None] * len(newstring)] * len(newstring)

    for i, line in enumerate(newstring):
        for j, char in enumerate(line.split()):
            board[i][j] = char

    if turn == -1:
        return board
    else:
        return encodeboard(board, turn, blackcapts, whitecapts)
