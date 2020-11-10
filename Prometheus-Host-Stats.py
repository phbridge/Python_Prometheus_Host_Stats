# # Title
# Python Prometheus Host Stats
#
# # Language
# Python 3.5+
#
# # Description
# This is designed to be an easy way to collect host stats using prometheus scrape as if your are scraping for other stuff
# nice and easy to also scrape for this. I got fed up of the different ways telegraf and prometheus reported stuff making
# comparisons and graphing on a single page hard work.
#
# # Contacts
# Phil Bridges - phbridge@cisco.com
#
# # Licence
# Please see LICENCE file
#
# # EULA
# This software is provided as is and with zero support level. Support can be purchased by providing Phil bridges with a
# varity of Beer, Wine, Steak and Greggs pasties. Please contact phbridge@cisco.com for support costs and arrangements.
# Until provison of alcohol or baked goodies your on your own but there is no rocket sciecne involved so dont panic too
# much. To accept this EULA you must include the correct flag when running the script. If this script goes crazy wrong and
# breaks everything then your also on your own and Phil will not accept any liability of any type or kind. As this script
# belongs to Phil and NOT Cisco then Cisco cannot be held responsable for its use or if it goes bad, nor can Cisco make
# any profit from this script. Phil can profit from this script but will not assume any liability. Other than the boaring
# stuff please enjoy and plagerise as you like (as I have no ways to stop you) but common curtacy says to credit me in some
# way [see above comments on Beer, Wine, Steak and Greggs.].
#

import inspect                          # part of the logging stack
import logging.handlers                 # Needed for logging
import threading                        # for periodic cron type jobs
import wsgiserver                       # Runs the Flask webesite
from flask import Flask                 # Flask website
from flask import Response              # Used to respond to stats request
import signal                           # catches SIGTERM and SIGINT
from datetime import timedelta          # calculate x time ago
from datetime import datetime           # timestamps mostly
from multiprocessing import Manager     # variables between processes dict

# import psutil                           # for CPU stats
# import io                               # sending images only
# import json                             # building json DB/ parsing stuff
# import os
# import time
import sys                              # for error to catch and debug
import traceback                        # helps add more logging infomation
# from multiprocessing import Pool        # trying to run in parallel rather than in sequence
# import requests                         # fetching updates
# from flask import send_file             # Send Word Cloud via Flask
# from flask import request               # Flask website requester details
# from webexteamssdk import WebexTeamsAPI # gets and posts messages

import credentials                      # imports static values

FLASK_HOST = credentials.FLASK_HOST
FLASK_PORT = credentials.FLASK_PORT
FLASK_HOSTNAME = credentials.FLASK_HOSTNAME
TARGET_URL = "http://" + FLASK_HOSTNAME + ":" + str(FLASK_PORT) + "/"
ABSOLUTE_PATH = credentials.ABSOLUTE_PATH
LOGFILE = credentials.LOGFILE

THREAD_TO_BREAK = threading.Event()

multiprocessing_manager = Manager()
# NETWORKS_JSON = multiprocessing_manager.dict({})
MEMORY_DATA = multiprocessing_manager.dict({})
NETWORK_DATA = multiprocessing_manager.dict({})
CPU_DATA_LIST = multiprocessing_manager.list()
# MAX_THREADS = 3

flask_app = Flask(__name__)


def cpu_five_seconds_interval(interval=5):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("five_seconds_interval")
    response_string = ""
    try:
        for cpu_name in CPU_DATA_LIST[0]:
            function_logger.info(cpu_name)
            cpu_user_last = CPU_DATA_LIST[0][cpu_name]["user"]
            cpu_nice_last = CPU_DATA_LIST[0][cpu_name]["nice"]
            cpu_system_last = CPU_DATA_LIST[0][cpu_name]["system"]
            cpu_idle_last = CPU_DATA_LIST[0][cpu_name]["idle"]
            cpu_iowait_last = CPU_DATA_LIST[0][cpu_name]["iowait"]
            cpu_irq_last = CPU_DATA_LIST[0][cpu_name]["irq"]
            cpu_softirq_last = CPU_DATA_LIST[0][cpu_name]["softirq"]
            cpu_steal_last = CPU_DATA_LIST[0][cpu_name]["steal"]
            cpu_guest_last = CPU_DATA_LIST[0][cpu_name]["guest"]
            cpu_guest_nice_last = CPU_DATA_LIST[0][cpu_name]["guest_nice"]

            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", "0", cpu_user_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", "0", cpu_nice_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", "0", cpu_system_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", "0", cpu_idle_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", "0", cpu_iowait_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", "0", cpu_irq_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", "0", cpu_softirq_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", "0", cpu_steal_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", "0", cpu_guest_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", "0", cpu_guest_nice_last)


            cpu_user = CPU_DATA_LIST[1][cpu_name]["user"] - CPU_DATA_LIST[0][cpu_name]["user"]
            cpu_nice = CPU_DATA_LIST[1][cpu_name]["nice"] - CPU_DATA_LIST[0][cpu_name]["nice"]
            cpu_system = CPU_DATA_LIST[1][cpu_name]["system"] - CPU_DATA_LIST[0][cpu_name]["system"]
            cpu_idle = CPU_DATA_LIST[1][cpu_name]["idle"] - CPU_DATA_LIST[0][cpu_name]["idle"]
            cpu_iowait = CPU_DATA_LIST[1][cpu_name]["iowait"] - CPU_DATA_LIST[0][cpu_name]["iowait"]
            cpu_irq = CPU_DATA_LIST[1][cpu_name]["irq"] - CPU_DATA_LIST[0][cpu_name]["irq"]
            cpu_softirq = CPU_DATA_LIST[1][cpu_name]["softirq"] - CPU_DATA_LIST[0][cpu_name]["softirq"]
            cpu_steal = CPU_DATA_LIST[1][cpu_name]["steal"] - CPU_DATA_LIST[0][cpu_name]["steal"]
            cpu_guest = CPU_DATA_LIST[1][cpu_name]["guest"] - CPU_DATA_LIST[0][cpu_name]["guest"]
            cpu_guest_nice = CPU_DATA_LIST[1][cpu_name]["guest_nice"] - CPU_DATA_LIST[0][cpu_name]["guest_nice"]

            cpu_total = cpu_user + cpu_nice + cpu_system + cpu_idle + cpu_iowait + cpu_irq + cpu_softirq + cpu_steal + cpu_guest + cpu_guest_nice

            cpu_user_pc = round(cpu_user / cpu_total, 3)
            cpu_nice_pc = round(cpu_nice / cpu_total, 3)
            cpu_system_pc = round(cpu_system / cpu_total, 3)
            cpu_idle_pc = round(cpu_idle / cpu_total, 3)
            cpu_iowait_pc = round(cpu_iowait / cpu_total, 3)
            cpu_irq_pc = round(cpu_irq / cpu_total, 3)
            cpu_softirq_pc = round(cpu_softirq / cpu_total, 3)
            cpu_steal_pc = round(cpu_steal / cpu_total, 3)
            cpu_guest_pc = round(cpu_guest / cpu_total, 3)
            cpu_guest_nice_pc = round(cpu_guest_nice / cpu_total, 3)

            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice)


            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice_pc)

    except Exception as e:
        function_logger.error("something went bad with 5 second stats")
        function_logger.error("Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("Unexpected error:" + str(e))
        function_logger.error("TRACEBACK=" + str(traceback.format_exc()))
    return response_string


def cpu_fifteen_seconds_interval(interval=15):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("fifteen_seconds_interval")
    response_string = ""
    try:
        for cpu_name in CPU_DATA_LIST[0]:
            function_logger.info(cpu_name)
            cpu_user = CPU_DATA_LIST[3][cpu_name]["user"] - CPU_DATA_LIST[0][cpu_name]["user"]
            cpu_nice = CPU_DATA_LIST[3][cpu_name]["nice"] - CPU_DATA_LIST[0][cpu_name]["nice"]
            cpu_system = CPU_DATA_LIST[3][cpu_name]["system"] - CPU_DATA_LIST[0][cpu_name]["system"]
            cpu_idle = CPU_DATA_LIST[3][cpu_name]["idle"] - CPU_DATA_LIST[0][cpu_name]["idle"]
            cpu_iowait = CPU_DATA_LIST[3][cpu_name]["iowait"] - CPU_DATA_LIST[0][cpu_name]["iowait"]
            cpu_irq = CPU_DATA_LIST[3][cpu_name]["irq"] - CPU_DATA_LIST[0][cpu_name]["irq"]
            cpu_softirq = CPU_DATA_LIST[3][cpu_name]["softirq"] - CPU_DATA_LIST[0][cpu_name]["softirq"]
            cpu_steal = CPU_DATA_LIST[3][cpu_name]["steal"] - CPU_DATA_LIST[0][cpu_name]["steal"]
            cpu_guest = CPU_DATA_LIST[3][cpu_name]["guest"] - CPU_DATA_LIST[0][cpu_name]["guest"]
            cpu_guest_nice = CPU_DATA_LIST[3][cpu_name]["guest_nice"] - CPU_DATA_LIST[0][cpu_name]["guest_nice"]
            cpu_total = cpu_user + cpu_nice + cpu_system + cpu_idle + cpu_iowait + cpu_irq + cpu_softirq + cpu_steal + cpu_guest + cpu_guest_nice
            cpu_user_pc = round(cpu_user / cpu_total, 3)
            cpu_nice_pc = round(cpu_nice / cpu_total, 3)
            cpu_system_pc = round(cpu_system / cpu_total, 3)
            cpu_idle_pc = round(cpu_idle / cpu_total, 3)
            cpu_iowait_pc = round(cpu_iowait / cpu_total, 3)
            cpu_irq_pc = round(cpu_irq / cpu_total, 3)
            cpu_softirq_pc = round(cpu_softirq / cpu_total, 3)
            cpu_steal_pc = round(cpu_steal / cpu_total, 3)
            cpu_guest_pc = round(cpu_guest / cpu_total, 3)
            cpu_guest_nice_pc = round(cpu_guest_nice / cpu_total, 3)

            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice)

            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice_pc)

    except Exception as e:
        function_logger.error("something went bad with 5 second stats")
        function_logger.error("Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("Unexpected error:" + str(e))
        function_logger.error("TRACEBACK=" + str(traceback.format_exc()))
    return response_string


def cpu_one_min_interval(interval=60):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("one_min_interval")
    response_string = ""
    try:
        for cpu_name in CPU_DATA_LIST[0]:
            function_logger.info(cpu_name)
            cpu_user = CPU_DATA_LIST[12][cpu_name]["user"] - CPU_DATA_LIST[0][cpu_name]["user"]
            cpu_nice = CPU_DATA_LIST[12][cpu_name]["nice"] - CPU_DATA_LIST[0][cpu_name]["nice"]
            cpu_system = CPU_DATA_LIST[12][cpu_name]["system"] - CPU_DATA_LIST[0][cpu_name]["system"]
            cpu_idle = CPU_DATA_LIST[12][cpu_name]["idle"] - CPU_DATA_LIST[0][cpu_name]["idle"]
            cpu_iowait = CPU_DATA_LIST[12][cpu_name]["iowait"] - CPU_DATA_LIST[0][cpu_name]["iowait"]
            cpu_irq = CPU_DATA_LIST[12][cpu_name]["irq"] - CPU_DATA_LIST[0][cpu_name]["irq"]
            cpu_softirq = CPU_DATA_LIST[12][cpu_name]["softirq"] - CPU_DATA_LIST[0][cpu_name]["softirq"]
            cpu_steal = CPU_DATA_LIST[12][cpu_name]["steal"] - CPU_DATA_LIST[0][cpu_name]["steal"]
            cpu_guest = CPU_DATA_LIST[12][cpu_name]["guest"] - CPU_DATA_LIST[0][cpu_name]["guest"]
            cpu_guest_nice = CPU_DATA_LIST[12][cpu_name]["guest_nice"] - CPU_DATA_LIST[0][cpu_name]["guest_nice"]
            cpu_total = cpu_user + cpu_nice + cpu_system + cpu_idle + cpu_iowait + cpu_irq + cpu_softirq + cpu_steal + cpu_guest + cpu_guest_nice
            cpu_user_pc = round(cpu_user / cpu_total, 3)
            cpu_nice_pc = round(cpu_nice / cpu_total, 3)
            cpu_system_pc = round(cpu_system / cpu_total, 3)
            cpu_idle_pc = round(cpu_idle / cpu_total, 3)
            cpu_iowait_pc = round(cpu_iowait / cpu_total, 3)
            cpu_irq_pc = round(cpu_irq / cpu_total, 3)
            cpu_softirq_pc = round(cpu_softirq / cpu_total, 3)
            cpu_steal_pc = round(cpu_steal / cpu_total, 3)
            cpu_guest_pc = round(cpu_guest / cpu_total, 3)
            cpu_guest_nice_pc = round(cpu_guest_nice / cpu_total, 3)

            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice)

            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval=%s} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice_pc)

    except Exception as e:
        function_logger.error("something went bad with 5 second stats")
        function_logger.error("Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("Unexpected error:" + str(e))
        function_logger.error("TRACEBACK=" + str(traceback.format_exc()))
    return response_string


def five_min_interval(interval=300):
    print("nothing")


def get_latest_cpu_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("get_latest_cpu_stats")
    while not THREAD_TO_BREAK.is_set():
        t = datetime.today()
        future = datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
        future += timedelta(seconds=5)
        function_logger.info("sleeping for %s seconds" % (future - t).seconds)
        THREAD_TO_BREAK.wait((future - t).seconds)
        if THREAD_TO_BREAK.is_set():
            return
        function_logger.info("opening cpu file")
        with open("/proc/stat") as cpufile:
            cpu_scrape = {}
            for cpuline in cpufile.readlines():
                function_logger.debug(cpuline)
                cputimes = cpuline.split()
                function_logger.debug(cputimes)
                if "cpu" in cputimes[0]:
                    function_logger.debug(cputimes)
                    cpu_scrape[cputimes[0]] = {}
                    cpu_scrape[cputimes[0]]['cpu_name'] = cputimes[0]
                    cpu_scrape[cputimes[0]]['user'] = int(cputimes[1])
                    cpu_scrape[cputimes[0]]['nice'] = int(cputimes[2])
                    cpu_scrape[cputimes[0]]['system'] = int(cputimes[3])
                    cpu_scrape[cputimes[0]]['idle'] = int(cputimes[4])
                    cpu_scrape[cputimes[0]]['iowait'] = int(cputimes[5])
                    cpu_scrape[cputimes[0]]['irq'] = int(cputimes[6])
                    cpu_scrape[cputimes[0]]['softirq'] = int(cputimes[7])
                    cpu_scrape[cputimes[0]]['steal'] = int(cputimes[8])
                    cpu_scrape[cputimes[0]]['guest'] = int(cputimes[9])
                    cpu_scrape[cputimes[0]]['guest_nice'] = int(cputimes[10])

            function_logger.debug(cpu_scrape)
            global CPU_DATA_LIST
            CPU_DATA_LIST.append(cpu_scrape)
            # CPU_DATA_LIST = CPU_DATA_LIST[-120:]
            CPU_DATA_LIST = CPU_DATA_LIST[-3:]
            function_logger.debug(CPU_DATA_LIST)


def get_latest_mem_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("get_latest_mem_stats")
    while not THREAD_TO_BREAK.is_set():
        t = datetime.today()
        future = datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
        future += timedelta(seconds=5)
        function_logger.info("sleeping for %s seconds" % (future - t).seconds)
        THREAD_TO_BREAK.wait((future - t).seconds)
        if THREAD_TO_BREAK.is_set():
            return
        function_logger.info("opening mem file")
        global MEMORY_DATA
        with open("/proc/meminfo") as memfile:
            for memline in memfile.readlines():
                # function_logger.info(memline)
                line = memline.split()
                # function_logger.info(line)
                if "SwapTotal" in line[0]:
                    MEMORY_DATA["SwapTotal"] = line[1]
                elif "SwapFree" in line[0]:
                    MEMORY_DATA["SwapFree"] = line[1]
                elif "MemTotal" in line[0]:
                    MEMORY_DATA["MemTotal"] = line[1]
                elif "MemFree" in line[0]:
                    MEMORY_DATA["MemFree"] = line[1]
                elif "MemAvailable" in line[0]:
                    MEMORY_DATA["MemAvailable"] = line[1]
                elif "Buffers" in line[0]:
                    MEMORY_DATA["Buffers"] = line[1]
                elif "Cached" in line[0]:
                    MEMORY_DATA["Cached"] = line[1]
                elif "Active" in line[0]:
                    MEMORY_DATA["Active"] = line[1]
                elif "Inactive" in line[0]:
                    MEMORY_DATA["Inactive"] = line[1]
        function_logger.info(MEMORY_DATA)


def get_latest_net_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("get_latest_net_stats")
    while not THREAD_TO_BREAK.is_set():
        t = datetime.today()
        future = datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
        future += timedelta(seconds=5)
        function_logger.info("sleeping for %s seconds" % (future - t).seconds)
        THREAD_TO_BREAK.wait((future - t).seconds)
        if THREAD_TO_BREAK.is_set():
            return
        function_logger.info("opening net file")
        global NETWORK_DATA
        with open("/proc/net/dev") as netfile:
            for netline in netfile.readlines():
                if "Inter" or "face" not in netline:
                    line = netline.split()
                    function_logger.info(line)
                    interface_name = line[0].strip(":")
                    NETWORK_DATA[interface_name]["R_bytes"] = line[1]
                    NETWORK_DATA[interface_name]["R_packets"] = line[2]
                    NETWORK_DATA[interface_name]["R_errs"] = line[3]
                    NETWORK_DATA[interface_name]["R_drop"] = line[4]
                    NETWORK_DATA[interface_name]["R_fifo"] = line[5]
                    NETWORK_DATA[interface_name]["R_frame"] = line[6]
                    NETWORK_DATA[interface_name]["R_compressed"] = line[7]
                    NETWORK_DATA[interface_name]["R_multicast"] = line[8]
                    NETWORK_DATA[interface_name]["T_bytes"] = line[9]
                    NETWORK_DATA[interface_name]["T_packets"] = line[10]
                    NETWORK_DATA[interface_name]["T_errs"] = line[11]
                    NETWORK_DATA[interface_name]["T_drop"] = line[12]
                    NETWORK_DATA[interface_name]["T_fifo"] = line[13]
                    NETWORK_DATA[interface_name]["T_colls"] = line[14]
                    NETWORK_DATA[interface_name]["T_carrier"] = line[15]
                    NETWORK_DATA[interface_name]["T_compressed"] = line[16]


@flask_app.route('/cpu_metrics')
def cpu_metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("metrics")
    return_string = ""
    return_string += cpu_five_seconds_interval()
    # return_string += cpu_fifteen_seconds_interval()
    # return_string += cpu_one_min_interval()
    # return_string += five_min_interval()
    return Response(return_string, mimetype='text/plain')


@flask_app.route('/memory_metrics')
def memory_metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("metrics")
    return_string = ""
    return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "SwapTotal", MEMORY_DATA["SwapTotal"])
    return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "SwapFree", MEMORY_DATA["SwapFree"])
    return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "MemTotal", MEMORY_DATA["MemTotal"])
    return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "MemFree", MEMORY_DATA["MemFree"])
    return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "MemAvailable", MEMORY_DATA["MemAvailable"])
    return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "Buffers", MEMORY_DATA["Buffers"])
    return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "Cached", MEMORY_DATA["Cached"])
    return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "Active", MEMORY_DATA["Active"])
    return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "Inactive", MEMORY_DATA["Inactive"])
    return Response(return_string, mimetype='text/plain')


@flask_app.route('/network_metrics')
def network_metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("metrics")
    return_string = ""
    for each in NETWORK_DATA.keys():
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "R_bytes", NETWORK_DATA[each]["R_bytes"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "R_packets", NETWORK_DATA[each]["R_packets"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "R_errs", NETWORK_DATA[each]["R_errs"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "R_drop", NETWORK_DATA[each]["R_drop"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "R_fifo", NETWORK_DATA[each]["R_fifo"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "R_frame", NETWORK_DATA[each]["R_frame"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "R_compressed", NETWORK_DATA[each]["R_compressed"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "R_multicast", NETWORK_DATA[each]["R_multicast"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "T_bytes", NETWORK_DATA[each]["T_bytes"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "T_packets", NETWORK_DATA[each]["T_packets"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "T_errs", NETWORK_DATA[each]["T_errs"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "T_drop", NETWORK_DATA[each]["T_drop"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "T_fifo", NETWORK_DATA[each]["T_fifo"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "T_colls", NETWORK_DATA[each]["T_colls"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "T_carrier", NETWORK_DATA[each]["T_carrier"])
        return_string += 'NetworkStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "T_compressed", NETWORK_DATA[each]["T_compressed"])
    return Response(return_string, mimetype='text/plain')


def graceful_killer(signal_number, frame):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("Got Kill signal")
    function_logger.info('Received:' + str(signal_number))
    THREAD_TO_BREAK.set()
    function_logger.info("set thread to break")
    cpu_update_thread.join()
    mem_update_thread.join()
    net_update_thread.join()
    function_logger.info("joined auto_update_thread thread")
    http_server.stop()
    function_logger.info("stopped HTTP server")
    quit()


if __name__ == "__main__":
    # Create Logger
    logger = logging.getLogger(".__main__")
    handler = logging.handlers.TimedRotatingFileHandler(LOGFILE, backupCount=365, when='D')
    logger_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(process)d:%(name)s - %(message)s')
    handler.setFormatter(logger_formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info("---------------------- STARTING ----------------------")
    logger.info("cisco EoS EoL script started")

    # Catch SIGTERM etc
    signal.signal(signal.SIGHUP, graceful_killer)
    # signal.signal(signal.SIGINT, graceful_killer)
    # signal.signal(signal.SIGQUIT, graceful_killer)
    # signal.signal(signal.SIGILL, graceful_killer)
    # signal.signal(signal.SIGTRAP, graceful_killer)
    # signal.signal(signal.SIGABRT, graceful_killer)
    # signal.signal(signal.SIGBUS, graceful_killer)
    # signal.signal(signal.SIGFPE, graceful_killer)
    # signal.signal(signal.SIGKILL, graceful_killer)
    # signal.signal(signal.SIGUSR1, graceful_killer)
    # signal.signal(signal.SIGSEGV, graceful_killer)
    # signal.signal(signal.SIGUSR2, graceful_killer)
    # signal.signal(signal.SIGPIPE, graceful_killer)
    # signal.signal(signal.SIGALRM, graceful_killer)
    signal.signal(signal.SIGTERM, graceful_killer)

    # Start the cron type jobs
    logger.info("start the cron auto update thread")
    cpu_update_thread = threading.Thread(target=lambda: get_latest_cpu_stats())
    mem_update_thread = threading.Thread(target=lambda: get_latest_mem_stats())
    net_update_thread = threading.Thread(target=lambda: get_latest_net_stats())
    cpu_update_thread.start()
    mem_update_thread.start()
    net_update_thread.start()

    # Delete/Create Webhooks
    logger.info("start web server")
    http_server = wsgiserver.WSGIServer(host=FLASK_HOST, port=FLASK_PORT, wsgi_app=flask_app)
    http_server.start()
