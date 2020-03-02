# comodiac 
#### Continuous Offensive Monitoring of Domains, IPs and Content

## What is comodiac?

Comodiac is a tool created in response to the rapid turnover of modern security testing tooling and techniques, allowing for easy plug and play of new tools into a larger, more robust framework. As a high level overview, comodiac allows for CLI tools to be added through a configuration file and run, with the results parsed out into a SQLite database.

This approach to security tooling is incredibly versatile, allowing for features and conveniences such as:
* Scheduled scanning and continuous monitoring of hosts, which can 
* Alerting on changes to an organization's hosts, such as downtime monitoring or new asset discovery
* Dynamic CLI input generation, based on previous findings. This allows you to chain together multiple tools, essentially piping multiple inputs into a tool 
	* For example, say you wanted to run a content discovery scan on an organization's web infrastructure, using a list of previously web content in the individual hosts within the infrastructure. It would possible to dynamically generate a wordlist and discovered host list by creating a tool in the tools.json like the following:
	```
	{
		"name":"organization_similar_content_discovery",
		"command": "gobuster dir -u INPUT -oA OUTPUT -w WORDLIST",
		"input_type": "asset",
		"input_asset": "discovered_hosts",
		"wordlist_type": "asset",
		"wordlist_asset": "discovered_content",
		"output_asset": "organization_similar_content",
		"output_parse": "(regex to run on every line of the file to parse hosts)"
		}
	```
* 


## Note on Progress

Whilst several features currently work, the project is still in it's infancy. The following features are still to do:
* Alerting
* Dynamic tooling wordlist input
* Adding profiles and tools with the CLI. At the moment you manually need to edit tools.json.
* Use of profiles with the tool
* Meta - performing actions on scan completion outside of the scope of the tool such as creating directories or moving files. This is not a priority feature.
* Web interface. This is not a priority feature.

#### Call for Contributors

If anyone wants to contribute and get things working let me know and I'll get you up to speed. 

## Examples

#### Configuration

The following are some examples of adding/editing details in the config file. The config file can also be located and edited in .config/comodiac/comodiac.conf

`comodiac config add --tools_file=~/bugbounty/tools.json`

`comodiac config add --target_dir=~/bugbounty/targets`

`comodiac config add --alerting=email`

It is possible to retrieve the config setting for alerting with the following example:

`comodiac config get --alerting`

#### Adding Targets

`comodiac add-target -c tesla -tf tesla.scope -xf tesla.outofscope`

Sets up directory structure for all in-scope items from file to the target directory given by the config. If no database, initialises the database and adds the hosts.

`comodiac add-target -c tesla -t *.tesla.com`

If Tesla already exists in the database, adds \*.tesla.com to the target scope. If Tesla does not exist, creates the company in the db and creates the relevant files.

`comodiac view-target -c tesla -t tesla.com`

Displays information about the given target or company.

#### Scheduling Scans

`comodiac add-schedule -t tesla.com -i daily -C content_discovery`

Add a full content discovery scan of the tesla.com domain to the schedule for target tesla.com. This runs every tool that is categorised as content_discovery in tools.json.

`comodiac add-schedule -t *.tesla.com -i hourly -T amass_active -a new`

Creates an hourly amass_active scan of \*.tesla.com. When a new asset is discovered that wasn't previously in the database, it will alert with the alerting system defined in the configuration.


## Creating new Tools and Profiles

#### Creating a New Tool

Comodiac is designed to allow for many different CLI tools to be pipelined together, and the output of each tool parsed into the database.

Adding a new tool through the CLI is a future feature. For now, tools need to be added to the tools.json file directly. The following JSON is an example of a command:

```json

		{
		"name":"amass_active",
		"command": "amass -active -brute -ip -src -d INPUT -oA OUTPUT -w WORDLIST",
		"intype": "file",
		"infile": "wildcard_domains.txt",
		"wordlist": "/usr/share/wordlists/all.txt",
		"category": "subdomain_enumeration",
		"type": "domain",
		"parse_result": "regex",
		"meta": "add_asset_dir"
		}

```

Name: The name of the tool that will be used on the CLI. Best practice is to avoid whitespace.

Command: The CLI command to be run. Several placeholders can be used to make the scan dynamic:
	* INPUT - either the input file or a single asset.
	* OUTPUT - the name of the file to output.
	* WORDLIST - the path to the wordlist to use. This can be dynamically generated from previously discovered assets

#### Creating a Profile

`comodiac add-profile -n new_profile -T amass_active,aquatone`

Creates a profile called 'new_profile', which uses the tools amass_active and aquatone from tools.json. If the given tool does not exist, the profile is not created and an error is returned.


## Usage

```
Usage: comodiac [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add-schedule     Adds a scheduled scan to the specified target
  add-target       Adds a target to the bb folder
  delete-schedule  Remove a scheduled scan by the schedule ID
  edit-schedule    Edit a scheduled scan by the schedule ID
  scan-now         Immediately perform a given scan
  view-assets      View the latest assets from a given target or company
  view-schedule    View a scheduled scan by target, company or schedule id
  view-target      View all targets associated with a given company
```

#### Add Schedule

```
Usage: comodiac add-schedule [OPTIONS]

  Adds a scheduled scan to the specified target

Options:
  -v, --verbose                 Increase the tool's verbosity
  -c, --company TEXT            Company Name  [required]
  -t, --target TEXT             Target to add scheduled scans  [required]
  -i, --schedule-interval TEXT  Schedule Interval for scans  [required]
  -T, --tool TEXT               Tool to schedule
  -C, --category TEXT           Category of tools to schedule
  -p, --profile TEXT            Schedule profile
  -a, --alert TEXT              Alert options
  --help                        Show this message and exit.
```

#### Add Target

```
Usage: comodiac add-target [OPTIONS]

  Adds a target to the bb folder

Options:
  -v, --verbose               Increase the tool's verbosity
  -c, --company TEXT          Company Name  [required]
  -t, --target TEXT           Target Domain or IP in a comma delimited list
  -tf, --targetfile FILENAME  File of target Domains and IPs
  -x, --outofscope TEXT       Out-of-scope Domain or IP in a comma delimited
                              list
  -xf, --outofscopefile PATH  File of out-of-scope target Domains and IPs
  --help                      Show this message and exit.

```

#### Delete Schedule

```
Usage: comodiac delete-schedule [OPTIONS]

  Remove a scheduled scan by the schedule ID

Options:
  -v, --verbose           Increase the tool's verbosity
  -S, --schedule-id TEXT  Schedule ID to edit
  --help                  Show this message and exit.

```

#### Edit Schedule

```
Usage: comodiac edit-schedule [OPTIONS]

  Edit a scheduled scan by the schedule ID

Options:
  -v, --verbose                 Increase the tool's verbosity
  -S, --schedule-id TEXT        Schedule ID to edit
  -i, --schedule-interval TEXT  Schedule Interval for scans
  -T, --tool TEXT               Tool to schedule
  -C, --category TEXT           Category of tools to schedule
  -p, --preset TEXT             Schedule Preset
  -a, --alert TEXT              Alert options
  -p, --pause                   Pause or unpause scan
  --help                        Show this message and exit.
```

#### Scan Now

```
Usage: comodiac scan-now [OPTIONS]

  Immediately perform a given scan

Options:
  -v, --verbose        Increase the tool's verbosity
  -c, --company TEXT   Company Name
  -t, --target TEXT    Target Domain or IP in a comma delimited list
  -T, --tool TEXT      Tool to schedule
  -C, --category TEXT  Category of tools to schedule
  --help               Show this message and exit.
```

#### View Assets

```
Usage: comodiac view-assets [OPTIONS]

  View the latest assets from a given target or company

Options:
  -v, --verbose          Increase the tool's verbosity
  -c, --company TEXT     Company Name
  -t, --target TEXT      Target Domain or IP in a comma delimited list
  -T, --tool TEXT        Tool to schedule
  -C, --category TEXT    Category of tools to schedule
  -fd, --from-date TEXT  Start date of assets to view
  -td, --to-date TEXT    End date of assets to view
  --help                 Show this message and exit.
```

#### View Schedule

```
Usage: comodiac view-schedule [OPTIONS]

  View a scheduled scan by target, company or schedule id

Options:
  -v, --verbose           Increase the tool's verbosity
  -c, --company TEXT      Company Name
  -t, --target TEXT       Target Domain or IP in a comma delimited list
  -S, --schedule-id TEXT  Schedule ID to edit
  --help                  Show this message and exit.
```

#### View Target

```
Usage: comodiac view-target [OPTIONS]

  View all targets associated with a given company

Options:
  -v, --verbose       Increase the tool's verbosity
  -c, --company TEXT  Company Name
  -t, --target TEXT   Target Domain or IP in a comma delimited list
  --help              Show this message and exit.
```




