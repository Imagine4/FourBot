import discord
import pickle
import cmds
import Go
import importlib

client = discord.Client()

auth = cmds.readjson("auth.json")


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Type " + cmds.prefix + "help for help"))
    print("I'm here!!!")


@client.event
async def on_message(msg):

    if msg.content[:len(cmds.prefix)] != cmds.prefix:
        return

    await cmds.process(msg, client)

    if cmds.isupdate(msg):

        with open("games.txt", "wb") as f:
            pickle.dump(cmds.gogames, f)

        importlib.reload(cmds)
        importlib.reload(Go)

        with open("games.txt", "rb") as f:
            cmds.gogames = pickle.load(f)

client.run(auth)
