import discord
import yaml
import re
import pickle
import secret

from discord.ext import commands
from utils.help_format import get_help, format_args


with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)


class FourBot(commands.Bot):
    def __init__(self, cfg):
        super().__init__(cfg['prefix'])
        
        # keep a copy of the config for future purposes
        self.config = cfg
        
        # replace help command with our own
        self.all_commands['help'] = self.help
        self.gogames = {}
        try:
            with open("games.txt", "rb") as f:
                self.gogames = pickle.load(f)
        
        except FileNotFoundError: pass

    async def on_message(self, message):

        content = message.content
        author = message.author

        if author.id == 416693134412611586:
            return

        if message.guild is None:
            if content.startswith("?") and len(content) > 1:
                await message.channel.send("That's not my prefix!")

            if content.startswith(config['prefix']):
                print("DM with " + author.name + ": " + message.content)

                if content.startswith(config['prefix'] + secret.letter):
                    text = secret.dothething(author.mention, author.name + "#" + author.discriminator, content)
                    await client.get_channel(secret.channel).send(text)

        elif message.guild.id in (356544373267103744, 422904859654750210):
            print(message.guild.name
                  + " in " + message.channel.name
                  + " by " + message.author.name
                  + ": " + message.content)

        await self.process_commands(message)

    def save_games(self):
        with open("games.txt", "wb") as f:
            pickle.dump(self.gogames, f)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name=f"Type {client.command_prefix}help for help"))
        self.load_extension('cmds')
        print("I'm here!!!")
    
    async def on_command_error(self, ctx: commands.Context, exception: Exception):

        phrase = "Something's gone wrong... \n"
        prefix = config["prefix"]

        if isinstance(exception, commands.CommandInvokeError):
            # all exceptions are wrapped in CommandInvokeError if they are not a subclass of CommandError
            # you can access the original exception with .original
            original = exception.original
            if isinstance(original, discord.Forbidden):
                # permissions error
                try:
                    await ctx.send(phrase + 'There was a permissions error: `{}`'.format(exception))
                except discord.Forbidden:
                    # we can't send messages in that channel
                    pass

            elif isinstance(original, discord.HTTPException) and original.status == 400:
                try: await ctx.send(phrase + "The output can't be sent on Discord (probably too long).")
                except discord.Forbidden: pass
            else: raise exception

        elif isinstance(exception, commands.CheckFailure): pass
        elif isinstance(exception, commands.CommandNotFound): pass
        elif isinstance(exception, commands.MissingRequiredArgument):
            cmd = client
            for i in ctx.message.content[len(prefix):].split():
                if cmd == ctx.bot and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                elif type(cmd) == commands.Group and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                else:
                    break

            if cmd.name not in ("go",):
                await ctx.channel.send("There's not enough arguments here.\n"
                                       f"Syntax: `{prefix}{cmd.signature}`")
            elif cmd.name == "go":
                await ctx.channel.send("Use `4.help go` for information on the command go.")

        elif isinstance(exception, commands.UserInputError):
            error = ' '.join(exception.args)
            error_data = re.findall('Converting to \"(.*)\" failed for parameter \"(.*)\"\.', error)
            if not error_data: await ctx.send(phrase + error)
            else:
                if ctx.message.id % 50 == 0 and error_data[0] == "game":
                    await ctx.send(file=discord.File("game.png"))
                else:
                    await ctx.send(phrase + '`{1}` needs to be a(n) `{0}`.'.format(*error_data[0]))
        else: raise exception
    
    @commands.command()
    async def help(self, ctx, *args):
        """Shows the help message."""
        if len(args) == 0:
            d = f"Use `{config['prefix']}help <command>` for more info. Works for subcommands, too!"
            cmds = client.commands
            for cmd in sorted(list(cmds), key=lambda x: x.name):
                if cmd.hidden is not True:
                    d += '\n  `{}{}`'.format(ctx.prefix, cmd.name)

                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    if brief is not None:
                        d += ' - {}'.format(brief)
            d += '\n'
        
        else:
            d = ''
            cmd = client
            cmd_name = ''
            for i in args:
                i = i.replace('@', '@\u200b')
                if cmd == ctx.bot and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                elif type(cmd) == commands.Group and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                else:
                    d += "I don't have a command like that."
                    break
            else:
                d = get_help(ctx, cmd, name=cmd_name)

        return await ctx.send(d)


if __name__ == '__main__':
    client = FourBot(config)
    client.run(open(config['token_file'], 'r').read().split('\n')[0])
