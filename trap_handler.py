#!/usr/bin/python
__author__ = "Pavel Polyakov"
__copyright__ = "Copyright (C) 2016 Pavel Polyakov"
__version__ = "0.3"

import sys
from models import connect_db
from processor import Processor
from mailer import send_mail
import logging

from config import MAIL_TO
from functions import for_html_trap_list, for_html_title

logging.basicConfig(format = u'[%(asctime)s] %(message)s', level = logging.INFO, filename = u'/var/log/trap_handler.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')

trap_up = """UDP: [192.168.168.222]:59010->[85.112.112.25]:162
UDP: [192.168.168.222]:59010->[85.112.112.25]:162
DISMAN-EVENT-MIB::sysUpTimeInstance 5:19:57:42.82
SNMPv2-MIB::snmpTrapOID.0 IF-MIB::linkUp
IF-MIB::ifIndex[544] 544
IF-MIB::ifAdminStatus[544] 1
IF-MIB::ifOperStatus[544] 1
IF-MIB::ifName[544] ge-0/0/21"""

trap_down = """UDP: [192.168.168.222]:59010->[85.112.112.25]:162
UDP: [192.168.168.222]:59010->[85.112.112.25]:162
DISMAN-EVENT-MIB::sysUpTimeInstance 5:19:57:42.82
SNMPv2-MIB::snmpTrapOID.0 IF-MIB::linkDown
IF-MIB::ifIndex[544] 544
IF-MIB::ifAdminStatus[544] 1
IF-MIB::ifOperStatus[544] 0
IF-MIB::ifName[544] ge-0/0/21"""

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) > 1:
        if argv[-1] == 'up':
            raw = trap_up
        if argv[-1] == 'down':
            raw = trap_down
    else:
        raw = sys.stdin.read()
    processor = Processor()
    trap = processor.work(raw)
    if trap is not None:
        logging.info(trap)
        session, e = connect_db()
        session.add(trap)
        session.commit()
        # ignore subinterfaces
        if '.' not in trap.ifName:
            if not trap.is_blocked(session):

                if trap.is_flapping(session):
                    trap.block(session)
                    trap.event = 'Flapping'
                else:
                    trap.event = trap.event.replace('IF-MIB::link','')

                text_main = for_html_trap_list([trap])
                text_title = for_html_title([trap])
                send_mail(text_title, MAIL_TO, text_main)
                logging.info(text_title)
    else:
        logging.info("I don't know how to deal with it:\n\n"+raw)
