import discord
import yaml
import re
import pickle

from discord.ext import commands
from utils.help_format import get_help


with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file)


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
    
    def save_games(self):
        with open("games.txt", "wb") as f:
            pickle.dump(self.gogames, f)

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name=f"Type `{client.command_prefix} help` for help"))
        self.load_extension('cmds')
        print("I'm here!!!")
    
    async def on_command_error(self, ctx: commands.Context, exception: Exception):
        if isinstance(exception, commands.CommandInvokeError):
            # all exceptions are wrapped in CommandInvokeError if they are not a subclass of CommandError
            # you can access the original exception with .original
            original = exception.original
            if isinstance(original, discord.Forbidden):
                # permissions error
                try:
                    await ctx.send('Permissions error: `{}`'.format(exception))
                except discord.Forbidden:
                    # we can't send messages in that channel
                    pass

            elif isinstance(original, discord.HTTPException) and original.status == 400:
                try: await ctx.send('I can\'t send that.')
                except discord.Forbidden: pass
            else: raise exception

        elif isinstance(exception, commands.CheckFailure): pass
        elif isinstance(exception, commands.CommandNotFound): pass
        elif isinstance(exception, commands.UserInputError):
            error = ' '.join(exception.args)
            error_data = re.findall('Converting to \"(.*)\" failed for parameter \"(.*)\"\.', error)
            if not error_data: await ctx.send('Error: {}'.format(' '.join(exception.args)))
            else:
                await ctx.send('`{1}` should be a `{0}`.'.format(*error_data[0]))
        else: raise exception
    
    @commands.command()
    async def help(self, ctx, *args):
        """This help message"""
        if len(args) == 0:
            d = 'Commands:\n'
            cmds = client.commands
            for cmd in sorted(list(cmds), key=lambda x: x.name):
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
                    d += 'Command not found.'
                    break
            else:
                d = get_help(ctx, cmd, name=cmd_name)

        return await ctx.send(d)


if __name__ == '__main__':
    client = FourBot(config)
    client.run(open(config['token_file'], 'r').read().split('\n')[0])
