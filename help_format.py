from discord.ext import commands

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

