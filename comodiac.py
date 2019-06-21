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
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-tf', '--targetfile', help='File of target Domains and IPs', type=click.File('rb'))
@click.option('-x', '--outofscope', help='Out-of-scope Domain or IP in a comma delimited list')
@click.option('-xf', '--outofscopefile', help='File of out-of-scope target Domains and IPs', type=click.File('rb'))
def add_target(company, target, targetfile, outofscope, outofscopefile):
    print(company)
    print(target)
    print(targetfile)
    print(outofscope)
    print(outofscopefile)

@cli.command()
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
def view_target(company, target):
    print(company)
    print(target)

@cli.command()
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-i', '--schedule-interval', default='daily', help='Schedule Interval for scans')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
@click.option('-p', '--preset', help='Schedule Preset', default='default')
@click.option('-a', '--alert', help='Alert options', default='default')
def add_schedule(company, target, schedule_interval, schedule_id, alert):
    print(company)
    print(target)
    print(targetfile)
    print(outofscope)
    print(outofscopefile)
	

@cli.command()
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
def view_schedule(company, target, schedule_id):
    return

@cli.command()
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
@click.option('-i', '--schedule-interval', default='daily', help='Schedule Interval for scans')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
@click.option('-p', '--preset', help='Schedule Preset', default='default')
@click.option('-a', '--alert', help='Alert options', default='default')
@click.option('-p', '--pause', is_flag=True, help='Pause or unpause scan')
def edit_schedule(company, target, schedule_interval, schedule_id, alert, pause):
    return

@cli.command()
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
def delete_schedule(company, target, schedule_interval, schedule_id, alert, pause):
    return

@cli.command()
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
def scan_now(company, target, tool, category):
    return


@cli.command()
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-C', '--category', help='Category of tools to schedule')
@click.option('-fd', '--from-date', help='Start date of assets to view')
@click.option('-td', '--to-date', help='End date of assets to view', default='today')
def view_assets(company, target, tool, category, from_date, to_date):
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

