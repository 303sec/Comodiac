MVP for an enumeration platform:
Scheduled full subdomain discovery
Scheduled full host (IP address) discovery
Scheduled full content discovery - good wordlist.
Scheduled full port scanning
Create folders & oranize everything discovered
Alert system with Slack / Email if:
    new hosts are discovered
    new content is found
    new IP address found
    new open port discovered

How?:

Enter Scope -> ( Subdomain Discovery -> IPs parsed from Subdomains -> 
EyeWitness all subdomains & IP addresses -> IP enumeration (Reverse DNS / Lookup owner) -> 
Portscan all IPs -> Content Discovery -> Parameter Discovery ) = Added to Cron job! -> Vulnerability Scanning / Manual Analysis 

Enter Scope:
bugbot CLI
Available Commands:
-h = show this help
-v = verbose output
+   +   +   +   +   +   +   
-c = Company Name
-t = Targets in scope (10.10.10.10,www.paypal.com,*.this.com)
-xt = Targets not in scope
-s = Schedule (hourly/daily/weekly) - Each tool should have a default schedule.

Process =
1 - Start 

bugbot -c Paypal -t 10.10.10.10,www.paypal.com,*.this.com -xt

Creates the company directory, creates the scope folder. Creates 

Dir to start a test should have:
CompanyName/
    scope/
        inscope_domains.txt
        outofscope_domains.txt
        inscope_ips.txt
        outofscope_ips.txt

2 - Create discovered_hosts folder
CompanyName/
    discovered_hosts/
        domains.txt
        ips.txt

3 - Add all scoped domains / ips to the domains /ip folder


3 - Initial scans: 
    any wildcard subdomains? Sub-discovery. 
    Get IP addresses of given domains. 
    Any non-CDN IPs? Port scans on these. 
    CDN IPs? See if possible to bypass WAF/CDN 
    
    Content Discovery:
        - Spidering
        - JSParsing
        - Dir Brute - Gobuster / Recursebuster






Subdomain discovery:
When new subdomain is found:
    - create a SQLite DB for that subdomain.
    - create folder inside company folder
    - create placeholder folders for organization
    - trigger an alert
    - add subdomain to the base dir's subdomains.txt file



Root folder: Paypal
Directory: $base/paypal/www.paypal.com/
Database: www.paypal.com
Table: Uptime Monitor:

    Timestamp | Live | IP | 



Get information from the database and parse it into tool commands.
Get the output of tools and parse them into a database.

Individual wrappers need to be written for each tool that parses and gets information.

Folders created for each tool type.

Folder structure:

Paypal/
    paypal.db
    notes/
        <script to collect up notes folder on a daily basis, and add them to timestamped folders in this dir.>
    scope/
        inscope_domains.txt
        outofscope_domains.txt
        inscope_ips.txt
        outofscope_ips.txt
    discovery/
        discovered_domains.txt
        discovered_ips.txt
    targets/
        *.paypal.com/
            www.paypal.com/
                /

Example:

Requirement: An ideal command to use with placeholders:
e.g.
amass -active -brute -ip -src -d $domain -oA $dir/$domain

Database Structure:

DB for each discovered host within a bug bounty.
DB for each subdomain for content discovery

DB: Paypal
Table: www.paypal.com
Directory: $base/paypal/www.paypal.com/
Timestamp | Live | IP  


1 - Main logic:


2 - Get required information required from the database

[tool | command | ]

3 - 

4 - Parse the file created and put the information into the database

[XML parser / JSON parser required]

open $dir/$domain
parse contents
add to database
remove file / store indefinitely on google drive

3 - 


'''


# scrape subdomains
# run amass
# run sublister
# - iceman543/subfinder
# cloudflare enum


# dictionary-attacking subdomains
# massdns is real fast
# aquatone-scan is useful

# https://gist.github.com/jhaddix/
# - Contails a..txt for subdomains / content_discovery_all.txt for content

# Commonspeak & scans.io for some extra wordlists

# -------------

# Portscan = not with nmap, use massscan. Nmap = super slow
# masscan does not have host resolution:
#strip=$(echo $1 | sed 's/https\?:\/\///')
#masscan -p1-65535 $(dig +short $strip | grep -oE "\b([0-9]{1,3}\.{3}[0-9]{1,3}\b") | head -1) --max-rate 1000 |& tee $strip_scan

# brutespray for default passwords / anon logins remote admin protocols

# eyewitness --prepend-https : tries both http & https! Then screenshots.
# potential change in config to add more ports, which would be useful.

# Label sites with live/non-live and give an interesting rating out of 10.


#content discovery

#spider site - Go through all links

# parse javascript
# linkfinder
# jsparser

# directory bruting: use gobuster
# Wordlists: robts.disallowed / robts.txt / raft / content_discovery_all.txt

# Parraameter bruting: parameth
# wordlist - backslash powered scanners top 2500 params

# exploits / testing
# blind xs - bxss
#idor - look for numerical parameters / hashes / email addresses

#subdomain takeover: can-itake-over-xyz

# cdn / waf bypass: find origin / find dev
# origin.sub.domain.com / origin-sub.domain.com / pragma:akamai-x-get-true-cache-key



# amass usage:

# amass -active -d $1 | tee <output>

# subfinder usage:

# subfinder -d $1 | tee <output>