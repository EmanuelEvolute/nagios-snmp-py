#!/usr/bin/python3
# Script version 1.0
# This script was created for python versions 3.5.3 and might not run on other versions

# Imports
from easysnmp import Session
from time import time, sleep
from argparse import ArgumentParser

# Args
args = ArgumentParser()
requiredargs = args.add_argument_group('required arguments')
conflictargs = args.add_argument_group('non-concurrent required arguments')
requiredargs.add_argument('--ports', nargs='+', required=True)
requiredargs.add_argument('--hostname', required=True, type=str)
conflictargs.add_argument('--above', nargs=2, type=int, metavar=('WARNING', 'CRITICAL'))
conflictargs.add_argument('--below', nargs=2, type=int, metavar=('WARNING', 'CRITICAL'))
args.add_argument('--seconds', type=float, default=1.0, help='Default: 1.0 Minimum: 1.0 Maximum: 10.0')

try:
    # Validate args
    a = args.parse_args()
    if a.above is not None and a.below is not None:
        raise Exception
    elif a.below is None and a.above[1] > a.above[0] >= 0:
        ceilwarn = a.above[0]
        ceilcrit = a.above[1]
        floorwarn = 0
        floorcrit = 0
    elif a.below[0] > a.below[1] >= 0:
        floorwarn = a.below[0]
        floorcrit = a.below[1]
        ceilcrit = float('inf')
        ceilwarn = float('inf')
    else:
        raise Exception
except:
    print('Invalid arguments')
    args.print_help()
    exit(2)

seconds = min(max(a.seconds, 1.0), 10.0)  # Wait for 1 to 10 seconds

# Create SNMP session
try:
    session = Session(hostname=a.hostname, community='public', version=2)
except:
    try:
        session = Session(hostname=a.hostname, community='public', version=1)
    except:
        print('Invalid hostname or host timed out')
        exit(2)

# Map port array
ports = {}
for port in a.ports:
    # Oper, DlTime, DlVal, UpTime, UpVal
    ports.update({port: list((False, 0, 0, 0, 0))})
errors = {'crit': [], 'warn': []}


# Get initial port operational status, download bytes and upload bytes
try:
    for port in ports:
        get = session.get('1.3.6.1.2.1.2.2.1.8.' + port)  # Get IfOperational
        if int(get.value) is 1:  # IfOperational
            ports[port][0] = True  # Oper = True
            get = session.get('1.3.6.1.2.1.2.2.1.10.' + port)  # Get download bytes
            ports[port][1] = time()  # DlTime = Now
            ports[port][2] = int(get.value)  # DlVal = Download bytes
            get = session.get('1.3.6.1.2.1.2.2.1.16.' + port)  # Get upload bytes
            ports[port][3] = time()  # UpTime = Now
            ports[port][4] = int(get.value)  # UpVal = Upload bytes
except:
    print('Invalid ports past port %s inclusive' % port)
    exit(2)

sleep(seconds)  # Wait X seconds

for port in ports:
    if ports[port][0]:  # Oper == True
        get = session.get('1.3.6.1.2.1.2.2.1.10.' + port)  # Get download bytes
        # Calculate download speed in bits/s accounting for time difference between readings
        dlspeed = (int(get.value) - ports[port][2]) / (time() - ports[port][1]) * 8
        get = session.get('1.3.6.1.2.1.2.2.1.16.' + port)  # Get upload bytes
        # Calculate upload speed in bits/s accounting for time difference between readings
        upspeed = (int(get.value) - ports[port][4]) / (time() - ports[port][3]) * 8

        # Look for warning or critical violations
        if dlspeed > ceilcrit or dlspeed < floorcrit:
            errors['crit'].append(port)
        elif dlspeed > ceilwarn or dlspeed < floorwarn:
            errors['warn'].append(port)
        if port not in errors['crit'] and (upspeed > ceilcrit or upspeed < floorcrit):
            errors['crit'].append(port)
        elif port not in errors['warn'] and port not in errors['crit'] and (upspeed > ceilwarn or upspeed < floorwarn):
            errors['warn'].append(port)

# Print violations and exit
if len(errors['crit']) > 0:
    err = ''
    for item in errors['crit']:
        err += str(item) + ' '
    print(err + '| warn_count=%s, crit_count=%s' % (len(errors['warn']), len(errors['crit'])))
    exit(2)
elif len(errors['warn']) > 0:
    err = ''
    for item in errors['warn']:
        err += str(item) + ' '
    print(err + '| warn_count=%s, crit_count=0' % len(errors['warn']))
    exit(1)
else:
    print('OK | warn_count=0, crit_count=0')
