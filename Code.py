import discord
import cmds
import importlib

client = discord.Client()

auth = cmds.readjson("/home/pi/Documents/FourBot/auth.json")


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
        # Reloads cmds
        importlib.reload(cmds)

client.run(auth)
