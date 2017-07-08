# Description
This script is generally used to rate limit traffic from certain IPs based on its domain name. Specifically, it is written to limit download traffic from Fshare (a popular storage provider in Vietnam). It's using ```scapy``` to capture DNS traffic and [Linux HTB](http://lartc.org/manpages/tc-htb.html) for traffic control. Feel free to modify the code to suit your needs.

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

Show available options:
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

