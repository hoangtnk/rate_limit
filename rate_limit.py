#!/usr/bin/env python
#
# Rate limit certain IPs based on domain name given by user

from pprint import pformat

import sys
sys.path.append("/root/iplist")

import subprocess
import argparse
import logging
import re

try:
    import fshare
except ImportError:
    presence = False
else:
    presence = True

try:
    from scapy.all import *
except ImportError:
    sys.exit("Scapy module has not been installed on this system.\nDownload it from https://pypi.python.org/pypi/scapy and try again.")

    
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
logging.getLogger("scapy.interactive").setLevel(logging.ERROR)
logging.getLogger("scapy.loading").setLevel(logging.ERROR)


added_ip = []  # list of IPs have been added to tc filter


def name_to_ip(pkt):
   
    """ Find name to IP mapping """
   
    if pkt.haslayer(DNS):
        i = 0
        if "fshare" in args.name:
            try:
                if re.search(r"down.*fshare.*", pkt[DNS].qd.qname) is not None:
                    while True:
                        if pkt[DNS].an[i].type == 1:  # type A (IPv4 address)
                            if pkt[DNS].an[i].rdata not in added_ip:
                                # Specify IPs to match
                                if args.rate is not None:
                                    subprocess.Popen(["tc", "filter", "add", "dev", "bond1", "protocol", "ip", "parent", "1:", "prio", "1", "u32", "match", "ip", "src", pkt[DNS].an[i].rdata, "flowid", "1:1"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
                                added_ip.append(pkt[DNS].an[i].rdata)
                            return
                        else:  # type 5 (cname) or type AAAA (IPv6 address)
                            i += 1
            except TypeError:
                pass
            except AttributeError:
                pass
            except IndexError:
                pass
        else:
            try:
                if re.search(r"%s" % name, pkt[DNS].qd.qname) is not None:
                    while True:
                        if pkt[DNS].an[i].type == 1:
                            if pkt[DNS].an[i].rdata not in added_ip:
                                if args.rate is not None:
                                    subprocess.Popen(["tc", "filter", "add", "dev", "bond1", "protocol", "ip", "parent", "1:", "prio", "1", "u32", "match", "ip", "src", pkt[DNS].an[i].rdata, "flowid", "1:1"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
                                added_ip.append(pkt[DNS].an[i].rdata)
                            return
                        else: 
                            i += 1
            except TypeError:
                pass
            except AttributeError:
                pass
            except IndexError:
                pass

            
def main():
   
    """ Main function """
   
    global args
   
    parser = argparse.ArgumentParser(description="Rate limit certain IPs based on its domain name")
    parser.add_argument("name", help="domain name to rate limit its corresponding IPs")
    parser.add_argument("-rate", metavar="", type=int, help="rate at which to limit traffic (mbit)")
    args = parser.parse_args()
   
    # Set the rate limit
    if args.rate is not None:
        subprocess.Popen(["tc", "qdisc", "add", "dev", "bond1", "root", "handle", "1:", "htb"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
        subprocess.Popen(["tc", "class", "add", "dev", "bond1", "parent", "1:", "classid", "1:1", "htb", "rate", str(args.rate) + "mbit"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
   
    # Sniffing DNS answers. We will use crontab to schedule the script to run
    # at 9:00 every day, and stop after 32400s (timeout = 32400s = 9 hours),
    # meaning it will only be running during working hours (9:00 to 18:00)
    try:
        sniff(filter="src port 53", prn=name_to_ip, store=0, timeout=32400)
        if args.rate is not None:
            subprocess.Popen(["tc", "qdisc", "del", "dev", "bond1", "root"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()  # remove all tc rules after working hours
       
        # Record fshare IPs to file
        if "fshare" in args.name:
            if presence:
                new_ip = False
                for ip in added_ip:
                    if ip not in fshare.servers:
                        new_ip = True
                        fshare.servers.append(ip)
                if new_ip:
                    with open("/root/iplist/fshare.py", "w") as f:
                        f.write("servers = %s" % pformat(fshare.servers))
            else:
                with open("/root/iplist/fshare.py", "w") as f:
                    f.write("servers = %s" % pformat(added_ip))
    except socket.error:
        sys.exit("Wrong interface and/or not run as superuser.")
    except Scapy_Exception:
        sys.exit("Syntax error.")
    except KeyboardInterrupt:
        if args.rate is not None:
            subprocess.Popen(["tc", "qdisc", "del", "dev", "bond1", "root"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
        sys.exit("All tc rules have been removed.")

        
if __name__ == "__main__":
    main()
