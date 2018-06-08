import discord
import yaml

from discord.ext import commands

with open('config.yml', 'r') as config_file:
    config = yaml.load(config_file)

client = commands.Bot(config['prefix'])
client.config = config  # In case we need the client to store config values in the future
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name=f"Type `{client.command_prefix} help` for help"))
    client.load_extension('cmds')

    print("I'm here!!!")


def format_args(cmd):
    """Returns the argument list with optional/mandatory brackets"""
    params = list(cmd.clean_params.items())
    p_str = ''
    for p in params:
        if p[1].default == p[1].empty: 
            p_str += f' <{p[0]}>'
        else: 
            p_str += f' [{p[0]}]'

    return p_str.strip()


def format_commands(prefix, cmd, name=None):
    """Lists command and subcommands with formatted args"""
    cmd_args = format_args(cmd)
    if not name:
        name = cmd.name
    name = name.replace('  ', ' ')
    d = f'`{prefix}{name} {cmd_args}`\n'
    d = d.replace('  ', ' ')

    if type(cmd) == commands.core.Group:
        cmds = sorted(list(cmd.commands), key=lambda x: x.name)
        for subcmd in cmds:
            d += format_commands(prefix, subcmd, name=f'{name} {subcmd.name}')

    return d


def get_help(ctx, cmd, name=None):
    """Get help for a command"""
    d = f'Help for command `{cmd.name}`:\n'
    d += '\n**Usage:**\n'
    d += format_commands(ctx.prefix, cmd, name=name)
    d += '\n**Description:**\n'
    d += '{}\n'.format('None' if cmd.help is None else cmd.help.strip())

    if cmd.aliases:
        d += '\n**Aliases:**'
        for alias in cmd.aliases:
            d += f'\n`{ctx.prefix}{alias}`'

        d += '\n'

    return d


@client.command()
async def help(ctx, *args):
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
    client.run(open(config['token_file'], 'r').read().split('\n')[0])
