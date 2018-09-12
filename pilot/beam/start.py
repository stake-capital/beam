import click
import os
import toml
from sys import exit
from .commands.commander import initialize
from .commands.gaiad import check_gaiad, start_gaiad, get_unbonded_steak, bond_steak
from .commands.network import get_local_ip, get_public_ip
from .commands.voting import get_new_votes, voting_alert
from .commands.utils import get_moniker
from .utils import check_config, get_config, get_node


def run(config, noupdate, firstrun):

    node_config = os.path.expanduser('~/.beam/node.toml')
    beam_config = os.path.expanduser('~/.beam/config.toml')
    check_config()
    configuration = get_config()
    if not os.path.exists(node_config):
        click.echo("No node file found. Creating one now...")
        click.echo("")
        # gather necessary information
        config_raw = open(beam_config, "r").read()
        config_file = toml.loads(config_raw)
        node_type = config_file['node_type']
        click.echo("Node Type: %s" %(node_type))
        local_ip = get_local_ip()
        click.echo("Local IP: %s" %(local_ip))
        public_ip = get_public_ip()
        click.echo("Public IP: %s" %(public_ip))
        moniker = get_moniker(local_ip,node_type)
        click.echo("Gaiad Moniker: %s" %(moniker))

        data = {}
        data['node_type'] = node_type
        data['local_ip'] = local_ip
        data['public_ip'] = public_ip
        data['moniker'] = moniker
        # write node config file
        try:
            formatted_data = toml.dumps(data).rstrip()
            with open(node_config, 'w') as f:
                f.write(formatted_data)
        except OSError as e:
            click.secho("Error writing node file: %s - %s." % (e.filename, e.strerror), fg="red", bold=True)
            click.echo("")
            exit(1)

        click.echo("")
        click.echo("Node file successfully created. Continuing...")
        click.echo("")

    node_configuration = get_node()
    if firstrun and \
       configuration['gaiad']['enable'] and \
       configuration['commander']['enable']:
        click.echo("Checking into commander....")
        local_ip = node_configuration['local_ip']
        public_ip = node_configuration['public_ip']
        moniker = node_configuration['moniker']
        node_type = node_configuration['node_type']
        initialize(local_ip,public_ip,moniker,node_type)
        start_gaiad()



    click.echo("Now running checks...")
    check_gaiad()
    if configuration['node_type'] is 'validator':

        if configuration['validator']['bonding']:
            steak = get_unbonded_steak()
            if steak > 0:
                click.echo("There are %s unbonded steak. Bonding now..." %(steak))
                bond_steak(steak)

        if configuration['validator']['voting']:
            votes = get_new_votes()
            if votes['new'] and configuration['alerting']:
                click.echo("New votes found. Alerting...")
                # TODO: Need to figure out a way to only notify of the proposal once.
                # Don't alert every time this runs.
                # Also need to find out how long until the proposal expires and do an auto-vote right before
                voting_alert()

    elif configuration['node_type'] is 'sentry':

        print("sentry")

    return
