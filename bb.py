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
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-tf', '--targetfile', help='File of target Domains and IPs', type=click.File('rb'))
@click.option('-x', '--outofscope', help='Out-of-scope Domain or IP in a comma delimited list')
@click.option('-xf', '--outofscopefile', help='File of out-of-scope target Domains and IPs', type=click.File('rb'))
@click.pass_context
def cli(ctx, company, target, targetfile, outofscope, outofscopefile):
	ctx.ensure_object(dict)
	ctx.obj['company'] = company
	ctx.obj['target'] = target
	pass

@cli.command()
@click.pass_context
def new_target(ctx):
	print(ctx.obj['target'], ctx.obj['company'])

@cli.command()
@click.option('-i', '--schedule-interval', default='daily', help='Schedule Interval for scans')
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
@click.option('-a', '--alert', help='Alert options')
@click.option('-p', '--pause', is_flag=True, help='Pause or unpause scan - toggle')
def schedule(company, target, targetfile, outofscope, outofscopefile, schedule_interval, schedule_id, alert, pause):
	print('test')








'''
@click.option('-c', '--company', help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.option('-tf', '--targetfile', help='File of target Domains and IPs', type=click.File('rb'))
@click.option('-x', '--outofscope', help='Out-of-scope Domain or IP in a comma delimited list')
@click.option('-xf', '--outofscopefile', help='File of out-of-scope target Domains and IPs', type=click.File('rb'))
@click.option('-i', '--schedule-interval', default='daily', help='Schedule Interval for scans')
@click.option('-S', '--schedule-id', help='Schedule ID to edit')
@click.option('-a', '--alert', help='Alert options')
@click.option('-p', '--pause', is_flag=True, help='Pause or unpause scan - toggle')
'''

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

