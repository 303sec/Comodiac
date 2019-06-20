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


@click.command()
@click.option('-c', '--company', required=True, help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
@click.pass_context
def add_target(ctx, company, target):
	print(target, company)
	ctx['company'] = company
	ctx['target'] = target 

@click.option('-tf', '--targetfile', help='File of target Domains and IPs', type=click.File('rb'))
@click.option('-x', '--outofscope', help='Out-of-scope Domain or IP in a comma delimited list')
@click.option('-xf', '--outofscopefile', help='File of out-of-scope target Domains and IPs', type=click.File('rb'))
@click.option('-i', '--schedule-interval', default='daily', help='Schedule Interval for scans')
@click.option('-S', '--schedule-id', help='Schedule ID to edit')

@click.option('-C', '--category', help='Scan category', not_required_if='tool')
@click.option('-T', '--tool', help='Tool to schedule', not_required_if='category')
@click.option('-a', '--alert', help='Alert options')
@click.option('-p', '--pause', is_flag=True, help='Pause or unpause scan - toggle')
def cli():
	print('test')




'''
How to create the CLI:

Ideally, it'd have 'smart parameters' that change the functionality based on the switches given, as follows:

NOPE. Don't like this idea

-t | -c
If it doesn't exist as a target already, add it

-t | -c | -s
View the schedule of the target

-c |
View the schedule of the company

if the s (--schedule) and either -p (--preset), -T (--tool) or -C (--category) are present, we add the schedule


Instead, how about using argument switches?
--add-target
requires: -c --company | -t --target

--schedule
requires: -c --company | -t --target | -i --scan-interval | 
optional: only one of: ( -p --preset | -T --tool | -C --category )
optional: -a --alert: default = on any change. 

--view-schedule
requires: -c --company
optional: -t --target

--edit-schedule
requires: -S --scan-id
optional: -T --tool | -a --alert | -p --pause / -r --resume | -i --interval 


CLI functions:


1 & 2: bugbot  -c test -t target.com,othertarget.com -xt notinscope.com
3: bugbot -c test -t target.com -s daily -p default  
4: bugbot -S 15 -s hourly -t


1) Add company, targets & out-of-scope targets
Requires:
	- Company name
	- Target list or file
	- Out of scope file or list

2) Add targets or out of scope targets to pre-existing company
Requires: 
	- Company name
	- Target list or file
	- Out of scope file or list

3) Schedule a scan using either a category or a tool
Requires:
	- Company Name or Target Name - if company supplied it scans all in scope targets. If target supplied it takes precident.
	- schedule interval
	- tool or category
	- Alerting options (possibly)

4) Edit a scheduled scan
Requires:
	- Scan ID
	- Schedule Interval or 
	- Alerting Options or
	- Pause toggle

6) View current schedule
	- Company
	- Target

7) Schedule a preset scan
	- Company Name
	- Target
	- Preset options: 
		basic:

		- OSINT - Every 6 hours
		- Subdomain Enumeration - every 16 Hours
		- content monitor - every hour
		- Content discovery - Every 6 hours



/*
7) View latest assets
	- Target
	- Company
	- Asset Type
	- Since (dates)
*/
'''