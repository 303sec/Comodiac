import click
from bugbot import scheduling, scoping
import json
import uuid
from terminaltables import AsciiTable

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
@click.option('-c', '--company', required=True, help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-tf', '--targetfile', help='File of target Domains and IPs', type=click.File('r+'))
@click.option('-x', '--outofscope', help='Out-of-scope Domain or IP in a comma delimited list')
@click.option('-xf', '--outofscopefile', help='File of out-of-scope target Domains and IPs', type=click.Path())
def add_target(verbose, company, target, targetfile, outofscope, outofscopefile):
    """ Adds a target to the bb folder """
    if target is None and targetfile is None and outofscope is None and outofscopefile is None:
        click.echo('[-] Error: at least one in-scope or out-of-scope target or file required. Exiting.')
        exit()

    scope = scoping.scoping(company, verbose)

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
        parsed_scope = scope.parse_scope_to_files(targets)
        print(parsed_scope)
        # Looks at the inscope_domains.txt file and generates a file with the wildcards as usable domains.
        # e.g. *.test.com inscope_domains.txt becomes test.com in wildcard_domains.
        wildcards = scope.parse_wildcard_domains()
        # We create folders for each of the inscope targets, including wildcards
        for scoped_domain in parsed_scope['domain_list']:
            scope.add_new_target(scoped_domain.strip())
        for scoped_ip in parsed_scope['ip_list']:
            scope.add_new_target(scoped_ip.strip())

    if outofscope or outofscopefile:
        scope.parse_scope_to_files(targets, False)


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
def view_target(verbose, company, target):
    """ View all targets associated with a given company """
    print('View-target functionality is todo.')

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', required=True, help='Company Name')
@click.option('-t', '--target', required=True, help='Target to add scheduled scans')
@click.option('-i', '--schedule-interval', required=True, default='daily', help='Schedule Interval for scans')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
@click.option('-p', '--profile', help='Schedule profile')
@click.option('-a', '--alert', help='Alert options', default='default')
def add_schedule(verbose, company, target, schedule_interval, tool, category, profile, alert):
    """ Adds a scheduled scan to the specified target """

    if tool is None and profile is None and category is None:
        click.echo('[-] Error: at least one tool, category or preset required. Exiting.')
        exit()
    if preset:
        print('Profiles not yet supported! Exiting.')
        exit()
    if category:
        print('Categories not yet supported! Exiting.')
        exit()

    scope = scoping.scoping(company, verbose)
    scheduler = scheduling.scheduling(verbose)


    # Need to check if the target exists. This would be easier if there was a database for the targets...
    if not scope.does_target_exist(target):
        click.echo('[-] Error: Target not found. Exiting.')
        exit()
        # add_target(verbose, company, target, None, None, None)


    # @param: info: dict: A dictionary of relevant information about the schedule, including:
    #
    # schedule['active']: default = 1
    # schedule['target']: required by CLI.
    # schedule['company']: self.company
    # schedule['schedule_interval']: default: 86400 (daily). Provided by CLI.
    # schedule['tool']: name of the tool (or category, if use_category == 1) required by CLI. 
    # schedule['use_category']: 1 if the scan is a category of tools (or just one). In the CLI, this can be used with --category

    # schedule['wordlist']: default: the wordlist in tools.json
    # schedule['infile']: if 'intype' == file, use this infile. From tools.json
    # schedule['intype']: 'file' or 'target'. If file, use the supplied 'infile', which should be available in tools.json
    # schedule['parser']: the parser regular expression to use on the output file. From tools.json
    # schedule['meta']: any extra functions to perform post-scan. From tools.json


    # This logic probably needs to be moved to scheduling.py at some point.
    if category:
        tool = category
        use_category = 1
    else:
        use_category = 0

    with open('tools.json', 'r') as tools_file:
        tool_found = False
        tools = json.loads(tools_file.read())
        for tool_name, tool_options in tools.items():
            if tool_name == tool or tool_options['category'] == tool:
                tool_found = True
                if 'wordlist' in tool_options:
                    wordlist = tool_options['wordlist']
                else:
                    wordlist = None
                if tool_options['intype'] == 'file':
                    schedule_input = tool_options['input']
                else:
                    schedule_input = target
                intype = tool_options['intype']
                parser = tool_options['parse_result']
                meta = tool_options['meta']
                schedule_uuid = str(uuid.uuid4())

                schedule_interval
                schedule = {'active': 1, 'target': target, 'company': company, 'schedule_interval': schedule_interval, \
                'tool': tool, 'use_category': use_category, 'wordlist': wordlist, 'input': schedule_input, 'intype':intype, \
                'parser':parser, 'meta': meta, 'alert': alert, 'uuid': schedule_uuid}
                scheduler.add_schedule(schedule)
    if tool_found == False:
        click.echo('[-] Tool not found.')
	

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
def view_schedule(verbose, company, target, schedule_id):
    """ View a scheduled scan by target, company or schedule id """
    scheduler = scheduling.scheduling(verbose)
    print(AsciiTable(scheduler.get_schedule(company, target, schedule_id)).table)
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
    """ Edit a scheduled scan by the schedule ID """
    return

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
def delete_schedule(verbose, company, target, schedule_interval, schedule_id, alert, pause):
    """ Remove a scheduled scan by the schedule ID """
    return

@cli.command()
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
def scan_now(verbose, company, target, tool, category):
    """ Immediately perform a given scan """
    scheduler = scheduling.scheduling(verbose)
    if tool and category:
        click.echo('[-] Can only have either tool or category. Exiting.')
        exit()
    if schedule_id:
        click.echo('[+] Scanning by Schedule ID')
        scheduler.immediate_scan(None, None, None, schedule_id)
    elif target and company and tool:
        click.echo('[+] Scanning by supplied tool, target & company')
        scheduler.immediate_scan(company, target, tool)
    elif target and company and category:
        click.echo('[+] Scanning by category not yet supported.')
        # scheduler.immediate_scan(company, target, category)
    else:
        print('Incorrect options given. Exiting.')
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
    """ View the latest assets from a given target or company """
    print(company)
    print(target)
    return

@cli.command(hidden=True)
@click.option('-v', '--verbose', is_flag=True, help='Increase the tool\'s verbosity')
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
@click.option('-fd', '--from-date', help='Start date of assets to view')
@click.option('-td', '--to-date', help='End date of assets to view', default='today')
def heartbeat(verbose, company, target, tool, category, from_date, to_date):
    scheduler = scheduling.scheduling(verbose)
    scheduler.heartbeat()
    return





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

