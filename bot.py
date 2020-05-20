import discord
import yaml
import re
import pickle
import secret

from discord.ext import commands

with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.BaseLoader)

class FourBot(commands.Bot):
    def __init__(self, cfg):
        super().__init__(cfg['prefix'])
        
        # keep a copy of the config for future purposes
        self.config = cfg
        
        # replace help command with our own, defined below
        self.help_command = HelpCommand()

        self.gogames = {}
        try:
            with open("games.txt", "rb") as f:
                self.gogames = pickle.load(f)
        except FileNotFoundError: pass

    def save_games(self):
        with open("games.txt", "wb") as f:
            pickle.dump(self.gogames, f)

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
                                       f"Syntax: `{prefix}{cmd.qualified_name} {format_args(cmd)}`")
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

        elif isinstance(exception, commands.ConversionError):
            Game = self.extensions["cmds"].Game
            print(id(exception.converter))
            print(id(Game))
            if exception.converter == Game:
                name = str(exception.args[1])[1:-1]
                await ctx.send(phrase + f"There isn't a game called {name}.")

        else: raise exception


class HelpCommand(commands.HelpCommand):
    def format_commands(self, prefix, cmd, name=None):
        """Lists command and subcommands with formatted args"""
        cmd_args = format_args(cmd)
        if not name:
            name = cmd.name
        name = name.replace('  ', ' ')
        d = f'{prefix}{name} `{cmd_args}`\n' if cmd_args else f'{prefix}{name}\n'
        d = d.replace('  ', ' ')

        if type(cmd) == commands.core.Group:
            cmds = sorted(list(cmd.commands), key=lambda x: x.name)
            for subcmd in cmds:
                d += self.format_commands(prefix, subcmd, name=f'{name} {subcmd.name}')

        return d

    async def send_bot_help(self, mapping):
        ctx = self.context
        prefix = self.clean_prefix

        d = f"Use `{prefix}help <command>` for more info. Works for subcommands, too!"
        for cmd in sorted(mapping[ctx.bot.cogs["Commands"]], key=lambda x: x.name):
            if cmd.hidden is not True:
                d += '\n  `{}{}`'.format(prefix, cmd.name)

                brief = cmd.brief
                if brief is None and cmd.help is not None:
                    brief = cmd.help.split('\n')[0]

                if brief is not None:
                    d += ' - {}'.format(brief)
        await ctx.send(d)

    async def send_command_help(self, cmd, d=''):
        ctx = self.context
        prefix = self.clean_prefix

        d += self.format_commands(ctx.prefix, cmd)
        d += '\n'
        d += '{}\n'.format('' if cmd.help is None else cmd.help.strip())

        if cmd.aliases:
            d += '\n**Aliases:**'
            for alias in cmd.aliases:
                d += f'\n`{prefix}{alias}`'

            d += '\n'

        await ctx.send(d)

    async def send_group_help(self, group):
        d = f'Commands in {group.name}:\n\n'
        await self.send_command_help(group, d)

    def command_not_found(self, string):
        return f"I don't have a command called {string}."

    def subcommand_not_found(self, command, string):
        return f"I don't have a command called {string} in {command.name}."


def format_args(cmd):
    """Returns the argument list with optional/mandatory brackets"""
    params = list(cmd.clean_params.items())
    if len(params) == 0:
        return ""
    p_str = ''

    for p in params:
        if p[1].default == p[1].empty:
            p_str += f' <{p[0]}>'
        else:
            p_str += f' [{p[0]}]'

    return p_str.strip()


if __name__ == '__main__':
    client = FourBot(config)
    client.run(open(config['token_file'], 'r').read().split('\n')[0])
