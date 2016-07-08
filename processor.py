import re
import time
from models import Link
from functions import getSnmp, parseTrap

class Processor(object):
    def work(self, data):
        trap = parseTrap(data)
        oid = trap.get('snmpTrapOID.0', None)
	if oid in ['IF-MIB::linkUp','IF-MIB::linkDown']:
            processor = LinkProcessor()
            return processor.job(trap)
        else:
            return None

class LinkProcessor(object):
    """Trap example:
    UDP: [192.168.168.222]:59010->[85.112.112.25]:162
    UDP: [192.168.168.222]:59010->[85.112.112.25]:162
    DISMAN-EVENT-MIB::sysUpTimeInstance 5:5:34:58.39
    SNMPv2-MIB::snmpTrapOID.0 IF-MIB::linkUp
    IF-MIB::ifIndex.567 567
    IF-MIB::ifAdminStatus.567 1
    IF-MIB::ifOperStatus.567 1
    IF-MIB::ifName.567 ge-0/0/21.0"""

    def job(self, trap):
        timestamp = time.time()
        host = trap['host']
        hostname = getSnmp(host, 'SNMPv2-MIB::sysName.0')
        event = trap['snmpTrapOID.0']
        ifIndex = trap.get('ifIndex')
        ifName = trap.get('ifName', getSnmp(host,'IF-MIB::ifName.'+ifIndex))
        ifAlias = trap.get('ifAlias', getSnmp(host,'IF-MIB::ifAlias.'+ifIndex))

        return Link(time = timestamp,
                    host = host,
                    hostname = hostname,
                    event = event,
                    ifIndex = ifIndex,
                    ifName = ifName,
                    ifAlias = ifAlias)