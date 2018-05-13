import json
import discord
import Go
from Go import *
import re

prefix = "4."
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
            await msg.channel.send("```4.help: pulls up this menu \n \n"
                                   "Go commands:"
                                   "    4.go <create> <@player> <board size> : creates a game with you and player \n"
                                   "    4.go move <move>: makes a move if it's your turn (ex: 4.go move k10) \n \n"
                                   "4.source: links FourBot's GitHub page```")

        elif arr[0] == "update" and isowner(msg):
            await msg.channel.send("Updated")

        elif arr[0] == "source":
            await msg.channel.send("https://github.com/Imagine4/FourBot/")

        elif arr[0] == "go":
            if arr[1] == "create":

                for players in gogames.keys():
                    for colornum, player in enumerate(players):
                        if player == msg.author.id:
                            await msg.channel.send("You already have a game!")
                            return

                p1 = msg.author.id
                match = ""

                try:
                    match = re.search(r'<@(?:!?)([0-9]{,18})>', arr[2])
                except IndexError:
                    await msg.channel.send("Where is player 2?")

                if match is None:
                    await msg.channel.send("Why isn't player 2 pinged?")

                elif match is not "":
                    p2 = int(match.group(1))
                    print(p1)
                    print(p2)

                    try:
                        gogames[(p1, p2)] = GoGame(int(arr[3]))
                        print("dbug Game created")
                    except IndexError or ValueError:
                        gogames[(p1, p2)] = GoGame(19)
                        print("dbug Game created")

                    await msg.channel.send("```"
                                           + gogames[(p1, p2)].printboard(gogames[(p1, p2)].board)
                                           + "```")
                    await msg.channel.send("<@" + str(p1) + "> is black. <@" + str(p2) + "> is white.")
                    await msg.channel.send("Black's turn")

            elif arr[1] == "move":
                print(str(gogames))
                for players in gogames.keys():
                    for colornum, player in enumerate(players):
                        if player == msg.author.id:

                            if colornum == 0:
                                color = Go.black
                            else:
                                color = Go.white

                            if color == gogames[players].turn:

                                try:

                                    gogames[players].nextmove(gogames[players].turn, arr[2])

                                    if not gogames[players].gamenotfinished:

                                        whiteterritory = gogames[players].whiteterritory
                                        blackterritory = gogames[players].blackterritory
                                        whitecaptures = gogames[players].whitecaptures
                                        blackcaptures = gogames[players].blackcaptures

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

                                        gogames.pop(players)

                                        return

                                    await msg.channel.send("```"
                                                           + gogames[players].printboard(gogames[players].board)
                                                           + "```")

                                    if gogames[players].previousturn == gogames[players].turn:
                                        await msg.channel.send("That was an invalid move, try again")

                                    if gogames[players].turn == Go.black:
                                        await msg.channel.send("Black's turn")
                                    else:
                                        await msg.channel.send("White's turn")
                                    return

                                except IndexError:
                                    await msg.channel.send("Um... you didn't enter a move...")
                                    return
                    else:
                        await msg.channel.send("It's not your turn!")
                        return
                else:
                    await msg.channel.send("You're not in a game!")
            else:
                await msg.channel.send("I can't find a Go command like that...")

