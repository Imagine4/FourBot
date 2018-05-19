import json
import discord
import Go
from Go import *
import re

prefix = "4test."
gogames = {}


def readjson(path):
    with open(path) as fil:
        return json.load(fil)


def isupdate(msg):
    return msg.content == prefix + "update" and msg.author.id in (212350439532789760, 136611352692129792)


def isowner(msg):
    return msg.author.id in (212350439532789760, 136611352692129792)


# Below is the code that runs every time a message is sent, handles commands
async def process(msg, client):
    print(msg.content)
    if msg.content[:len(prefix)] == prefix:
        arr = msg.content[len(prefix):].split(" ")
        # Arr is short for argument. Milo's idea for coding commands

        if arr[0] == "help":
            await msg.channel.send(format("""
            
```{0}help: pulls up this menu 
 
Go commands: 
    {0}go create <@player> (board size) (game name): creates a game with you and player with the name "gamename"
    {0}go <gamename> <move>: makes a move in the game "gamename" (ex: 4.go mygame k10), if move is skip, skips turn
    {0}go delete <game name>: deletes the game "gamename"
    {0}go board <gamename>: says the current board of the game and who's turn it is
 
{0}source: links FourBot's GitHub page```

""".format(prefix)))

        elif arr[0] == "update" and isowner(msg):
            await msg.channel.send("Updated")

        elif arr[0] == "source":
            await msg.channel.send("https://github.com/Imagine4/FourBot/")

        elif arr[0] == "listgames":
            message = "Go Games:\n"
            for game in gogames.keys():
                theboard = gogames[game].board
                message += (game + " - " + str(theboard)) + "\n"
            await msg.channel.send(message)

        elif arr[0] == "go":
            if arr[1] == "create":

                p1 = msg.author.id

                try:
                    match = re.search(r'<@(?:!?)([0-9]{,18})>', arr[2])
                except IndexError:
                    await msg.channel.send("Where is player 2?")
                    return

                try:
                    gamenameinput = arr[4]
                except IndexError:
                    gamenameinput = msg.author.name

                for gamenames in gogames.keys():

                    if gamenames == gamenameinput:
                        await msg.channel.send("A game already exists under this name, pick a new one.")
                        return

                if gamenameinput in ("create", "delete", "end", "board"):
                    await msg.channel.send("That name is reserved for commands")
                    return
                else:
                    gamename = gamenameinput

                if match is None:
                    await msg.channel.send("Why isn't player 2 pinged?")
                    return

                elif match is not "":
                    p2 = int(match.group(1))
                    print(p1)
                    print(p2)

                    try:
                        gogames[gamename] = GoGame(int(arr[3]), p1, p2)
                    except IndexError or ValueError:
                        gogames[gamename] = GoGame(19, p1, p2)

                    await msg.channel.send("Game created under the name " + gamename)
                    await msg.channel.send("```"
                                           + gogames[gamename].printboard(gogames[gamename].board)
                                           + "```")
                    await msg.channel.send("<@" + str(p1) + "> is black. <@" + str(p2) + "> is white.\nBlack's turn")


            elif arr[1] == "delete":

                try:
                    game = gogames[arr[2]]
                except IndexError:
                    await msg.channel.send("What game am I supposed to delete..?")
                    return
                except KeyError:
                    await msg.channel.send("I can't find the game you mentioned.")
                    return

                if msg.author.id == game.p1 or msg.author.id == game.p2:
                    gogames.pop(arr[2])
                    await msg.channel.send("The game " + arr[2] + " no longer exists :thumbsup:")
                else:
                    await msg.channel.send("Hey, that's not your game!")


            elif arr[1] == "end":

                try:
                    gamename = arr[2]
                    game = gogames[gamename]
                except IndexError:
                    await msg.channel.send("You didn't specifiy the game!")
                    return
                except KeyError:
                    await msg.channel.send("I can't find the game you mentioned.")
                    return

                if game.gamenotfinished:
                    await msg.channel.send("You game isn't done!")
                    return
                else:

                    whiteterritory = game.whiteterritory
                    blackterritory = game.blackterritory
                    whitecaptures = game.whitecaptures
                    blackcaptures = game.blackcaptures

                    await msg.channel.send("Black's captures: " + str(blackcaptures) + "\n"
                                           + "Black's territory: " + str(blackterritory) + "\n"
                                           + "White's captures: " + str(whitecaptures) + "\n"
                                           + "White's territory: " + str(whiteterritory))

                    blackscores = blackcaptures + blackterritory
                    whitescores = (whitecaptures + whiteterritory) + 6.5

                    if blackscores > whitescores:
                        await msg.channel.send("Winner: Black by " + str(blackscores - whitescores) + " points")
                    else:
                        await msg.channel.send("Winner: White by " + str(whitescores - blackscores) + " points")

                    gogames.pop(arr[1])

                    return


            elif arr[1] == "board":
                try:
                    game = gogames[arr[2]]
                except IndexError:
                    await msg.channel.send("You didn't specifiy the game!")
                    return
                except KeyError:
                    await msg.channel.send("I can't find the game you mentioned.")
                    return

                await msg.channel.send("```"
                                       + game.printboard(game.board)
                                       + "```")

                if game.gamenotfinished:
                    if game.turn == Go.black:
                        await msg.channel.send("Black's turn")
                    else:
                        await msg.channel.send("White's turn")
                    return


            else:

                try:
                    game = gogames[arr[1]]
                except KeyError:
                    await msg.channel.send("There's no Go command like that")
                    return

                if msg.author.id not in (game.p1, game.p2):
                    await msg.channel.send("You're not in a game!")
                    return

                if game.gamenotfinished:

                    if not ((game.p1 == msg.author.id and game.turn == black) or
                            (game.p2 == msg.author.id and game.turn == white)):
                        await msg.channel.send("It's not your turn!")
                        return

                    try:
                        game.nextmove(game.turn, arr[2])
                    except IndexError or ValueError:
                        await msg.channel.send("Um... you didn't enter a valid move...")
                        return

                    if not game.gamenotfinished:
                        await msg.channel.send("You can remove dead stones if both players move on the same location of the stone. \n"
                                               "Say 4.go <end> <game name> when done.")

                    if game.previousturn == game.turn:
                        await msg.channel.send("That was an invalid move, try again")
                        return

                    await msg.channel.send("```"
                                           + game.printboard(game.board)
                                           + "```")

                    if game.gamenotfinished:
                        if game.turn == Go.black:
                            await msg.channel.send("Black's turn")
                        else:
                            await msg.channel.send("White's turn")
                        return

                else:
                    try:
                        if arr[2] in game.potentialremoves:
                            game.remstones(game.processcoords(arr[2]))
                            await msg.channel.send("```" + game.printboard(game.board) + "``` \n Removed " + arr[2])
                        else:
                            game.potentialremoves.append(arr[2])
                            await msg.channel.send("Remove " + arr[2] + "?")

                    except IndexError or ValueError:
                        await msg.channel.send("Um... you didn't enter a valid move...")
                        return
