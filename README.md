# Description
This script is generally used to rate limit traffic from certain IPs based on its domain name. Specifically, it is used to limit download traffic from Fshare (a popular storage provider in Vietnam). It's using [scapy](https://pypi.python.org/pypi/scapy) to capture DNS traffic and [Linux HTB](http://lartc.org/manpages/tc-htb.html) for traffic control. Feel free to modify the code to suit your needs.

# Installation
Install the scapy module:
```
pip install scapy
```

# Usage
Assign execute permission to the script:
```
# chmod a+x rate_limit.py
```

Show the available options:
```
# ./rate_limit.py --help
usage: rate_limit.py [-h] [-rate] name

Rate limit certain IPs based on its domain name

positional arguments:
  name        domain name to rate limit its corresponding IPs

optional arguments:
  -h, --help  show this help message and exit
  -rate       rate at which to limit traffic (mbit)
```

Inside the code, I set the timeout for sniff function to 32400 seconds (9 hours), with the purpose of schedule the script to run at 9:00 every morning. As a result, we only rate limit traffic during working hours (from 9:00 to 18:00).

If you just want to collect IP addresses of Fshare servers, type **crontab -e** and add this line to the file:
```
0 9 * * 1-5 ./scripts/rate_limit.py fshare
```

Check out ```/root/iplist/fshare.py``` to see list of IP addresses being collected:
```
# cat /root/iplist/fshare.py
servers = ['118.69.215.69',
 '118.69.164.163',
 '118.69.164.148',
 '118.69.164.160',
 '118.69.164.158',
 '118.69.164.168',
 '118.69.164.169',
 '118.69.215.70',
 '118.69.164.156',
 '118.69.164.143',
 '118.69.164.170',
 '118.69.164.152',
 '118.69.164.167']
```

To limit download traffic from Fshare to 10Mbit, add this line to crontab:
```
0 9 * * 1-5 ./scripts/rate_limit.py fshare -rate 10
```
_**Notes: The rate value given in the command is the total amount of bandwidth allocated for Fshare, which means 10Mbit here will be shared for all users who download files from Fshare.**_
