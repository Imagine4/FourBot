import discord
import cmds
import importlib

client = discord.Client()

auth = cmds.readjson("auth.json")


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="Type " + cmds.prefix + "help for help"))
    print("I'm here!!!")


@client.event
async def on_message(msg):
    await cmds.process(msg, client)
    if cmds.isupdate(msg):
        # Reloads cmds
        importlib.reload(cmds)

client.run(auth)
