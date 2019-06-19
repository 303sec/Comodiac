import click
from bugbot import bugbot


@click.command()
@click.option('-c', '--company', required=True, help='Company Name')
@click.option('-t', '--target', help='Target Domain or IP in a comma delimited list')
def add_target(company, target):
	print(company, target)
	return
@click.option('-tf', '--targetfile', help='File of target Domains and IPs')
@click.option('-x', '--outofscope', help='Out-of-scope Domain or IP in a comma delimited list')
@click.option('-xf', '--outofscopefile', help='File of out-of-scope target Domains and IPs')
@click.option('-s', '--schedule', default='daily', help='Schedule Interval for scans')
@click.option('-C', '--category', help='Scan category')
@click.option('-T', '--tool', help='Tool to schedule')
@click.option('-a', '--alert', help='Alert options')
@click.option('-p', '--pause', help='Pause or unpause scan - toggle')


def cli():
	# There must be a better way than this! Maybe functions for each of the options, or groups?
	# bb = bugbot(company)
	return


if __name__ == '__main__':
	cli()