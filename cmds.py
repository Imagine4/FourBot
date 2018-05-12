import json
import discord
import Go
from Go import *
import re

prefix = "4."


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
            await msg.channel.send("```4.help: pulls up this menu \n"
                                   "4.go <create> <@player> <board size> : creates a game with you and player \n"
                                   "4.source: links FourBot's GitHub page```")

        elif arr[0] == "update" and isowner(msg):
            await msg.channel.send("Updated")

        elif arr[0] == "source":
            await msg.channel.send("https://github.com/Imagine4/FourBot/")

        elif arr[0] == "go":
            if arr[1] == "create":

                player1 = msg.author.id
                match = ""

                try:
                    match = re.search(r'<@(?:!?)([0-9]{,18})>', arr[2])
                except IndexError:
                    await msg.channel.send("Where is player 2??")

                if match is None:
                    await msg.channel.send("Why isn't player 2 pinged?")

                elif match is not "":
                    player2 = match.group(1)
                    print(player1)
                    print(player2)

                    try:
                        game = GoGame(int(arr[3]))
                    except IndexError or ValueError:
                        game = GoGame(19)
                        print("dbug Game created")
                    await msg.channel.send("```" + game.printboard(game.board) + "```")

            else:
                await msg.channel.send("I can't find a Go command like that...")

