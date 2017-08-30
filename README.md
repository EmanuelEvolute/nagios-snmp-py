# snmp-py
Simple Network Management Protocol script in Python that returns port numbers in excess of bandwith usage from a hostname with performance data.

# Dependencies
easysnmp

time

argparse

# Arguments
### Required:

--ports PORTS ...

--hostname HOSTNAME

### Non-concurrent and required:

--above WARNING CRITICAL

OR

--below WARNING CRITICAL

### Optional:

-h

--help

--seconds SECONDS

## Conditions
Only 1 of the non-concurrent arguments can be used at a time.

In case of --above, CRITICAL must be greater than WARNING and WARNING must be greater than or equal to 0.

CRITICAL > WARNING >= 0

Note that if WARNING is equal to 0, all ports with any activity will enter the warn list.

In case of --below, WARNING must be greater than CRITICAL and CRITICAL must be greater than or equal to 0.

WARNING > CRITICAL >= 0

Note that if CRITICAL is equal to 0, it will be impossible for any port to enter the critical list.

## Definitions
PORTS are port numbers. From 1 to how many ports your switch/router has. Invalid ports will result in an exception.

HOSTNAME is either an IP address or a domain. 127.0.0.1, google.com, switch1.room. Invalid hostnames will result in a timeout.

Above WARNING is the upper bitrate limit for port warning violation, at which point the port will be added to the warn list.

Above CRITICAL is the upper bitrate limit for port critical violation, at which point the port will be added to the critical list.

Below WARNING is the lower bitrate limit for port warning violation.

Below CRITICAL is the lower bitrate limit for port critical violation.

SECONDS is the amount of seconds the script will wait before probing again, allowing for some data to flow and give out an average for the span of time passed.


# Output
If the critical list has any entries, the critical list is printed.

If the warn list has any entries but the critical list does not, the warn list is printed.

If there are no entries on either list, OK is printed.

All of these outputs are followed by | warn_count=LEN(WARN_LIST), crit_count=LEN(CRIT_LIST).
