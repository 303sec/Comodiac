import click
from bugbot import bugbot


# From stackoverflow - https://stackoverflow.com/questions/44247099/click-command-line-interfaces-make-options-required-if-other-optional-option-is
class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
            ' NOTE: This argument is mutually exclusive with %s' %
            self.not_required_if
        ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with `%s`" % (
                        self.name, self.not_required_if))
            else:
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)

@click.group()
def cli():
    pass

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name', required=True)
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-tf', '--targetfile', help='File of target Domains and IPs', type=click.File('r+'))
@click.option('-x', '--outofscope', help='Out-of-scope Domain or IP in a comma delimited list')
@click.option('-xf', '--outofscopefile', help='File of out-of-scope target Domains and IPs', type=click.Path())
def add_target(verbose, company, target, targetfile, outofscope, outofscopefile):
    if target == None and targetfile == None and outofscope == None and outofscopefile == None:
        click.echo('Error: at least one in scope or out of scope target or file required.')
        return -1

    bb = bugbot.bugbot(company, verbose)

    # parse targets from file or CLI
    targets = []
    out_of_scope_targets = []
    if targetfile:
        for file_target in targetfile:
            targets.append(file_target.strip())
    if target:
        for split_target in target.split(','):
            targets.append(split_target)

    if outofscopefile:
        for out_of_scope_target in outofscopefile:
            out_of_scope_targets.append(out_of_scope_target.strip())
    if outofscope:
        for split_target in outofscope.split(','):
            out_of_scope_targets.append(split_target)

    if target or targetfile:
        print(targets)
        # Turns input into inscope_domains.txt & inscope_ips.txt
        parsed_scope = bb.parse_scope_to_files(targets)
        print(parsed_scope)
        # Looks at the inscope_domains.txt file and generates a file with the wildcards as usable domains.
        # e.g. *.test.com inscope_domains.txt becomes test.com in wildcard_domains.
        wildcards = bb.parse_wildcard_domains()
        # We create folders for each of the inscope targets, including wildcards
        for scoped_domain in parsed_scope['domain_list']:
            bb.add_new_target(scoped_domain.strip())
        for scoped_ip in parsed_scope['ip_list']:
            bb.add_new_target(scoped_ip.strip())

    if outofscope or outofscopefile:
        bb.parse_scope_to_files(targets, False)


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
def view_target(verbose, company, target):
    print('View-target functionality is todo.')

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-i', '--schedule-interval', default='daily', help='Schedule Interval for scans')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
@click.option('-p', '--preset', help='Schedule Preset', default='default')
@click.option('-a', '--alert', help='Alert options', default='default')
def add_schedule(verbose, company, target, schedule_interval, tool, category, preset, alert):
    
	

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
def view_schedule(verbose, company, target, schedule_id):
    return

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
@click.option('-i', '--schedule-interval', default='daily', help='Schedule Interval for scans')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
@click.option('-p', '--preset', help='Schedule Preset', default='default')
@click.option('-a', '--alert', help='Alert options', default='default')
@click.option('-p', '--pause', is_flag=True, help='Pause or unpause scan')
def edit_schedule(verbose, company, target, schedule_interval, schedule_id, alert, pause):
    return

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
def delete_schedule(verbose, company, target, schedule_interval, schedule_id, alert, pause):
    return

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
def scan_now(verbose, company, target, tool, category):
    return


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
@click.option('-fd', '--from-date', help='Start date of assets to view')
@click.option('-td', '--to-date', help='End date of assets to view', default='today')
def view_assets(verbose, company, target, tool, category, from_date, to_date):
    print(company)
    print(target)
    return



if __name__ == '__main__':
	cli()



'''
arg: --new-target
requires: -c --company ( -t --target || -tf --targetfile ) 
optional: ( -x --outofscope || -xf --outofscopefile )

arg: --schedule
requires: -c --company | -t --target | -i --scan-interval | 
requires: only one of: ( -p --preset | -T --tool | -C --category )
optional: -a --alert: default = 'default': on any change. 

arg: --view-schedule
requires: -c --company
optional: -t --target | -S --scan-id

arg: --edit-schedule
requires: -S --scan-id (if no other params, shows the schedule info table)
optional: only one of: ( -p --preset | -T --tool | -C --category )
optional: -a --alert | -p --pause / -r --resume | -i --interval 

arg: --delete-schedule
requires: -S --scan-id

arg: --scan-now
requires: -c --company | -t --target
requires: only one of: ( -p --preset | -T --tool | -C --category )

arg: --view-assets
requires: -c --company | -fd --from-date
optional: -td --to-date: default: today
optional: -t --target | -C --category | -T --tool 


'''

