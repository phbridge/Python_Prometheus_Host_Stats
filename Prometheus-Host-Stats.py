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
# This was largely built to monitor RaspberryPi4 running Debian (not rasparian) There is two flags to run in either mode
# Pull mode (prometheus/flask) or Push mode (Influx direct)
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
import sys                              # for error to catch and debug
import traceback                        # helps add more logging infomation
import subprocess
import requests

import credentials                      # imports static values

FLASK_HOSTNAME = credentials.FLASK_HOSTNAME
ABSOLUTE_PATH = credentials.ABSOLUTE_PATH
LOGFILE = credentials.LOGFILE
INFLUX_DB_Path = credentials.INFLUX_DB_PATH

INFLUX_MODE = credentials.INFLUX_MODE
FLASK_MODE = credentials.FLASK_MODE

THREAD_TO_BREAK = threading.Event()

multiprocessing_manager = Manager()
MEMORY_DATA = multiprocessing_manager.dict({})
NETWORK_DATA = multiprocessing_manager.dict({})
CPU_DATA_LIST = multiprocessing_manager.list()

FLASK_HOST = credentials.FLASK_HOST
FLASK_PORT = credentials.FLASK_PORT
flask_app = Flask(__name__)


def cpu_five_seconds_interval(interval=5):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("five_seconds_interval")
    response_string = ""
    try:
        for cpu_name in CPU_DATA_LIST[0]:
            function_logger.debug(cpu_name)
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
            cpu_total = cpu_user_last + cpu_nice_last + cpu_system_last + cpu_idle_last + cpu_iowait_last + cpu_irq_last + cpu_softirq_last + cpu_steal_last + cpu_guest_last + cpu_guest_nice_last
            cpu_user_pc = round(cpu_user_last / cpu_total, 3)
            cpu_nice_pc = round(cpu_nice_last / cpu_total, 3)
            cpu_system_pc = round(cpu_system_last / cpu_total, 3)
            cpu_idle_pc = round(cpu_idle_last / cpu_total, 3)
            cpu_iowait_pc = round(cpu_iowait_last / cpu_total, 3)
            cpu_irq_pc = round(cpu_irq_last / cpu_total, 3)
            cpu_softirq_pc = round(cpu_softirq_last / cpu_total, 3)
            cpu_steal_pc = round(cpu_steal_last / cpu_total, 3)
            cpu_guest_pc = round(cpu_guest_last / cpu_total, 3)
            cpu_guest_nice_pc = round(cpu_guest_nice_last / cpu_total, 3)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", "0", cpu_user_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", "0", cpu_nice_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", "0", cpu_system_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", "0", cpu_idle_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", "0", cpu_iowait_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", "0", cpu_irq_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", "0", cpu_softirq_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", "0", cpu_steal_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", "0", cpu_guest_last)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", "0", cpu_guest_nice_last)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", "0", cpu_user_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", "0", cpu_nice_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", "0", cpu_system_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", "0", cpu_idle_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", "0", cpu_iowait_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", "0", cpu_irq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", "0", cpu_softirq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", "0", cpu_steal_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", "0", cpu_guest_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", "0", cpu_guest_nice_pc)
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
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice_pc)
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
            function_logger.debug(cpu_name)
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
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest)
            response_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", interval, cpu_user_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", interval, cpu_nice_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", interval, cpu_system_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", interval, cpu_idle_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", interval, cpu_iowait_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", interval, cpu_irq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", interval, cpu_softirq_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", interval, cpu_steal_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", interval, cpu_guest_pc)
            response_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", interval, cpu_guest_nice_pc)
    except Exception as e:
        function_logger.error("something went bad with 15 second stats")
        function_logger.error("Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("Unexpected error:" + str(e))
        function_logger.error("TRACEBACK=" + str(traceback.format_exc()))
    return response_string


def get_latest_cpu_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("get_latest_cpu_stats")
    while not THREAD_TO_BREAK.is_set():
        t = datetime.today()
        future = datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
        future += timedelta(seconds=5)
        function_logger.debug("sleeping for %s seconds" % (future - t).seconds)
        THREAD_TO_BREAK.wait((future - t).seconds)
        if THREAD_TO_BREAK.is_set():
            return
        function_logger.debug("opening cpu file")
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
            CPU_DATA_LIST = CPU_DATA_LIST[-4:]  # keep last 3/4 results for summary over 5/15 seconds
            function_logger.debug(CPU_DATA_LIST)


@flask_app.route('/cpu_metrics')
def cpu_metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("cpu_metrics")
    return_string = cpu_metrics_data()
    return Response(return_string, mimetype='text/plain')


def cpu_metrics_data(influx=False):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    return_string = ""
    try:
        for cpu_name in CPU_DATA_LIST[0]:
            cpu_user = CPU_DATA_LIST[0][cpu_name]["user"]
            cpu_nice = CPU_DATA_LIST[0][cpu_name]["nice"]
            cpu_system = CPU_DATA_LIST[0][cpu_name]["system"]
            cpu_idle = CPU_DATA_LIST[0][cpu_name]["idle"]
            cpu_iowait = CPU_DATA_LIST[0][cpu_name]["iowait"]
            cpu_irq = CPU_DATA_LIST[0][cpu_name]["irq"]
            cpu_softirq = CPU_DATA_LIST[0][cpu_name]["softirq"]
            cpu_steal = CPU_DATA_LIST[0][cpu_name]["steal"]
            cpu_guest = CPU_DATA_LIST[0][cpu_name]["guest"]
            cpu_guest_nice = CPU_DATA_LIST[0][cpu_name]["guest_nice"]
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
            if influx:
                return_string += 'CPUUsage,host=%s,interval=%s user=%s,nice=%s,system=%s,idle=%s,iowait=%s,irq=%s,softirq=%s,steal=%s,guest=%s,guest_nice=%s \n' % \
                                 (FLASK_HOSTNAME, "0", cpu_user, cpu_nice, cpu_system, cpu_idle, cpu_iowait, cpu_irq, cpu_softirq, cpu_steal, cpu_guest, cpu_guest_nice)
                return_string += 'CPUUsage_pc,host=%s,interval=%s user=%s,nice=%s,system=%s,idle=%s,iowait=%s,irq=%s,softirq=%s,steal=%s,guest=%s,guest_nice=%s \n' % \
                                 (FLASK_HOSTNAME, "0", cpu_user_pc, cpu_nice_pc, cpu_system_pc, cpu_idle_pc, cpu_iowait_pc, cpu_irq_pc, cpu_softirq_pc, cpu_steal_pc, cpu_guest_pc, cpu_guest_nice_pc)
            else:
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", "0", cpu_user)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", "0", cpu_nice)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", "0", cpu_system)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", "0", cpu_idle)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", "0", cpu_iowait)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", "0", cpu_irq)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", "0", cpu_softirq)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", "0", cpu_steal)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", "0", cpu_guest)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", "0", cpu_guest_nice)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", "0", cpu_user_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", "0", cpu_nice_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", "0", cpu_system_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", "0", cpu_idle_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", "0", cpu_iowait_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", "0", cpu_irq_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", "0", cpu_softirq_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", "0", cpu_steal_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", "0", cpu_guest_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", "0", cpu_guest_nice_pc)
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
            if influx:
                return_string += 'CPUUsage,host=%s,interval=%s user=%s,nice=%s,system=%s,idle=%s,iowait=%s,irq=%s,softirq=%s,steal=%s,guest=%s,guest_nice=%s \n' % \
                                 (FLASK_HOSTNAME, "5", cpu_user, cpu_nice, cpu_system, cpu_idle, cpu_iowait, cpu_irq, cpu_softirq, cpu_steal, cpu_guest, cpu_guest_nice)
                return_string += 'CPUUsage_pc,host=%s,interval=%s user=%s,nice=%s,system=%s,idle=%s,iowait=%s,irq=%s,softirq=%s,steal=%s,guest=%s,guest_nice=%s \n' % \
                                 (FLASK_HOSTNAME, "5", cpu_user_pc, cpu_nice_pc, cpu_system_pc, cpu_idle_pc, cpu_iowait_pc, cpu_irq_pc, cpu_softirq_pc, cpu_steal_pc, cpu_guest_pc, cpu_guest_nice_pc)
            else:
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", "5", cpu_user)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", "5", cpu_nice)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", "5", cpu_system)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", "5", cpu_idle)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", "5", cpu_iowait)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", "5", cpu_irq)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", "5", cpu_softirq)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", "5", cpu_steal)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", "5", cpu_guest)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", "5", cpu_guest_nice)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", "5", cpu_user_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", "5", cpu_nice_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", "5", cpu_system_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", "5", cpu_idle_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", "5", cpu_iowait_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", "5", cpu_irq_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", "5", cpu_softirq_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", "5", cpu_steal_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", "5", cpu_guest_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", "5", cpu_guest_nice_pc)
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
            if influx:
                return_string += 'CPUUsage,host=%s,interval=%s user=%s,nice=%s,system=%s,idle=%s,iowait=%s,irq=%s,softirq=%s,steal=%s,guest=%s,guest_nice=%s \n' % \
                                 (FLASK_HOSTNAME, "15", cpu_user, cpu_nice, cpu_system, cpu_idle, cpu_iowait, cpu_irq, cpu_softirq, cpu_steal, cpu_guest, cpu_guest_nice)
                return_string += 'CPUUsage_pc,host=%s,interval=%s user=%s,nice=%s,system=%s,idle=%s,iowait=%s,irq=%s,softirq=%s,steal=%s,guest=%s,guest_nice=%s \n' % \
                                 (FLASK_HOSTNAME, "15", cpu_user_pc, cpu_nice_pc, cpu_system_pc, cpu_idle_pc, cpu_iowait_pc, cpu_irq_pc, cpu_softirq_pc, cpu_steal_pc, cpu_guest_pc, cpu_guest_nice_pc)
            else:
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", "15", cpu_user)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", "15", cpu_nice)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", "15", cpu_system)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", "15", cpu_idle)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", "15", cpu_iowait)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", "15", cpu_irq)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", "15", cpu_softirq)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", "15", cpu_steal)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", "15", cpu_guest)
                return_string += 'CPUUsage{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", "15", cpu_guest_nice)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "user", "15", cpu_user_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "nice", "15", cpu_nice_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "system", "15", cpu_system_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "idle", "15", cpu_idle_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "iowait", "15", cpu_iowait_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "irq", "15", cpu_irq_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "softirq", "15", cpu_softirq_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "steal", "15", cpu_steal_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest", "15", cpu_guest_pc)
                return_string += 'CPUUsage_pc{cpu="%s",host="%s",measurement="%s",interval="%s"} %s \n' % (cpu_name, FLASK_HOSTNAME, "guest_nice", "15", cpu_guest_nice_pc)
    except Exception as e:
        function_logger.error("something went bad with cpu second stats")
        function_logger.error("Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("Unexpected error:" + str(e))
        function_logger.error("TRACEBACK=" + str(traceback.format_exc()))
    return return_string


def cpu_metrics_thread():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("cpu_metrics_thread")
    THREAD_TO_BREAK.wait(30)  # wait here to avoid getting errors on start
    historical_upload = ""
    while not THREAD_TO_BREAK.is_set():
        now = datetime.now()
        timestamp_string = str(int(now.timestamp()) * 1000000000)
        future = now + timedelta(seconds=15)
        influx_upload = ""
        influx_upload += cpu_metrics_data(influx=True)
        to_send = ""
        for each in influx_upload.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.info("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            function_logger.info("adding to history")
            historical_upload += influx_upload
        time_to_sleep = (future - datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            THREAD_TO_BREAK.wait(time_to_sleep)


@flask_app.route('/memory_metrics')
def memory_metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("memory_metrics")
    return_string = memory_metrics_data()
    return Response(return_string, mimetype='text/plain')


def memory_metrics_data(influx=False):
    return_string = ""
    with open("/proc/meminfo") as memfile:
        for memline in memfile.readlines():
            line = memline.split()
            if "SwapTotal" in line[0]:
                MEMORY_DATA["SwapTotal"] = line[1]
            elif "SwapFree" in line[0]:
                MEMORY_DATA["SwapFree"] = line[1]
            elif "SwapCached" in line[0]:
                MEMORY_DATA["SwapCached"] = line[1]
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
    if influx:
        return_string += 'MemoryUsage,host=%s SwapTotal=%s,SwapFree=%s,SwapCached=%s,SwapUsed=%s,MemTotal=%s,MemFree=%s,MemAvailable=%s,Buffers=%s,Cached=%s,Active=%s,Inactive=%s \n' % \
                         (FLASK_HOSTNAME, MEMORY_DATA["SwapTotal"], MEMORY_DATA["SwapFree"], MEMORY_DATA["SwapCached"], int(MEMORY_DATA["SwapTotal"]) - int(MEMORY_DATA["SwapFree"]), MEMORY_DATA["MemTotal"], MEMORY_DATA["MemFree"], MEMORY_DATA["MemAvailable"], MEMORY_DATA["Buffers"], MEMORY_DATA["Cached"], MEMORY_DATA["Active"], MEMORY_DATA["Inactive"])
    else:
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "SwapTotal", MEMORY_DATA["SwapTotal"])
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "SwapFree", MEMORY_DATA["SwapFree"])
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "SwapCached", MEMORY_DATA["SwapCached"])
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "SwapUsed", int(MEMORY_DATA["SwapTotal"]) - int(MEMORY_DATA["SwapFree"]))
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "MemTotal", MEMORY_DATA["MemTotal"])
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "MemFree", MEMORY_DATA["MemFree"])
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "MemAvailable", MEMORY_DATA["MemAvailable"])
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "Buffers", MEMORY_DATA["Buffers"])
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "Cached", MEMORY_DATA["Cached"])
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "Active", MEMORY_DATA["Active"])
        return_string += 'MemoryUsage{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "Inactive", MEMORY_DATA["Inactive"])
    return return_string


def memory_metrics_thread():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("memory_metrics_thread")
    historical_upload = ""
    while not THREAD_TO_BREAK.is_set():
        now = datetime.now()
        timestamp_string = str(int(now.timestamp()) * 1000000000)
        future = now + timedelta(seconds=30)
        influx_upload = ""
        influx_upload += memory_metrics_data(influx=True)
        to_send = ""
        for each in influx_upload.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.info("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            function_logger.info("adding to history")
            historical_upload += influx_upload
        time_to_sleep = (future - datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            THREAD_TO_BREAK.wait(time_to_sleep)


@flask_app.route('/pressure_metrics')
def pressure_metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("pressure_metrics")
    return_string = pressure_metrics_data()
    return Response(return_string, mimetype='text/plain')


def pressure_metrics_data(influx=False):
    return_string = ""
    with open("/proc/pressure/io") as io:
        for ioline in io.readlines():
            line = ioline.split()
            if "some" in line[0]:
                some_10 = line[1].split("=")[1]
                some_60 = line[2].split("=")[1]

            elif "full" in line[0]:
                full_10 = line[1].split("=")[1]
                full_60 = line[2].split("=")[1]
        if influx:
            return_string += 'Pressure,host=%s,measurement=%s full10=%s,full60s=%s,some10=%s,some60s=%s \n' % \
                             (FLASK_HOSTNAME, "IO", full_10, full_60, some_10, some_60)
        else:
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "IO", "10", "full", full_10)
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "IO", "60", "full", full_60)
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "IO", "10", "some", some_10)
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "IO", "60", "some", some_60)
    with open("/proc/pressure/cpu") as cpu:
        for cpuline in cpu.readlines():
            line = cpuline.split()
            if "some" in line[0]:
                some_10 = line[1].split("=")[1]
                some_60 = line[2].split("=")[1]
        if influx:
            return_string += 'Pressure,host=%s,measurement=%s some10=%s,some60s=%s \n' % \
                             (FLASK_HOSTNAME, "CPU", some_10, some_60)
        else:
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "CPU", "10", "some", some_10)
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "CPU", "60", "some", some_60)
    with open("/proc/pressure/memory") as mem:
        for memline in mem.readlines():
            line = memline.split()
            if "some" in line[0]:
                some_10 = line[1].split("=")[1]
                some_60 = line[2].split("=")[1]
            elif "full" in line[0]:
                full_10 = line[1].split("=")[1]
                full_60 = line[2].split("=")[1]
        if influx:
            return_string += 'Pressure,host=%s,measurement=%s full10=%s,full60s=%s,some10=%s,some60s=%s \n' % \
                             (FLASK_HOSTNAME, "MEM", full_10, full_60, some_10, some_60)
        else:
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "MEM", "10", "full", full_10)
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "MEM", "60", "full", full_60)
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "MEM", "10", "some", some_10)
            return_string += 'Pressure{host="%s",measurement="%s",time=%s,type="%s"} %s \n' % (FLASK_HOSTNAME, "MEM", "60", "some", some_60)
    return return_string


def pressure_metrics_thread():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("pressure_metrics_thread")
    historical_upload = ""
    while not THREAD_TO_BREAK.is_set():
        now = datetime.now()
        timestamp_string = str(int(now.timestamp()) * 1000000000)
        future = now + timedelta(seconds=30)
        influx_upload = ""
        influx_upload += pressure_metrics_data(influx=True)
        to_send = ""
        for each in influx_upload.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.info("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            function_logger.info("adding to history")
            historical_upload += influx_upload
        time_to_sleep = (future - datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            THREAD_TO_BREAK.wait(time_to_sleep)


@flask_app.route('/pi_metrics')
def pi_metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("pi_metrics")  # Note this is for running debian on pi (not rested on rasperian just debian)
    return_string = pi_metrics_data()
    return Response(return_string, mimetype='text/plain')


def pi_metrics_data(influx=False):
    return_string = ""
    with open("/sys/class/thermal/thermal_zone0/temp") as temp:
        for line in temp.readlines():
            if influx:
                return_string += 'PiStats,host=%s,measurement=%s temp=%s \n' % (FLASK_HOSTNAME, "temp", int(line) / 1000)
            else:
                return_string += 'PiStats{host="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, "temp", int(line) / 1000)
    with open("/sys/devices/system/cpu/cpufreq/policy0/stats/time_in_state") as cpu_fre_max:
        freq_string = ""
        freq_ratio = 0
        freq_steps = 0
        for line in cpu_fre_max.readlines():
            if influx:
                freq_string += "freq_%s=%s," % (line.split()[0], line.split()[1])
                freq_ratio += int(line.split()[0]) * int(line.split()[1])
                freq_steps += int(line.split()[1])
            else:
                return_string += 'PiStats{host="%s",measurement="%s",freq=%s} %s \n' % (FLASK_HOSTNAME, "cpu_freq", line.split()[0], line.split[1])
        if influx:
            return_string += 'PiStats,host=%s,measurement=%s %s \n' % (FLASK_HOSTNAME, "cpu_freq", freq_string[:-1])
            return_string += 'PiStats,host=%s,measurement=%s cpu_ratio=%s,cpu_cycles=%s,cpu_rate=%s \n' % \
                             (FLASK_HOSTNAME, "cpu_ratio", freq_ratio/freq_steps, freq_ratio, freq_steps)
    return return_string


def pi_metrics_thread():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("pi_metrics_thread")
    historical_upload = ""
    while not THREAD_TO_BREAK.is_set():
        now = datetime.now()
        timestamp_string = str(int(now.timestamp()) * 1000000000)
        future = now + timedelta(seconds=30)
        influx_upload = ""
        influx_upload += pi_metrics_data(influx=True)
        to_send = ""
        for each in influx_upload.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.info("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            function_logger.info("adding to history")
            historical_upload += influx_upload
        time_to_sleep = (future - datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            THREAD_TO_BREAK.wait(time_to_sleep)


@flask_app.route('/network_metrics')
def network_metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("network_metrics")
    # with open("/proc/net/dev") as netfile:
    #     network_scrape = {}
    #     for netline in netfile.readlines():
    #         if "Inter" not in netline and "face" not in netline:
    #             line = netline.split()
    #             interface_name = line[0].strip(":")
    #             NETWORK_DATA[interface_name] = {}
    #             network_scrape["R_bytes"] = line[1]
    #             network_scrape["R_packets"] = line[2]
    #             network_scrape["R_errs"] = line[3]
    #             network_scrape["R_drop"] = line[4]
    #             network_scrape["R_fifo"] = line[5]
    #             network_scrape["R_frame"] = line[6]
    #             network_scrape["R_compressed"] = line[7]
    #             network_scrape["R_multicast"] = line[8]
    #             network_scrape["T_bytes"] = line[9]
    #             network_scrape["T_packets"] = line[10]
    #             network_scrape["T_errs"] = line[11]
    #             network_scrape["T_drop"] = line[12]
    #             network_scrape["T_fifo"] = line[13]
    #             network_scrape["T_colls"] = line[14]
    #             network_scrape["T_carrier"] = line[15]
    #             network_scrape["T_compressed"] = line[16]
    #             NETWORK_DATA[interface_name] = network_scrape
    return_string = network_metrics_data()
    # for each in NETWORK_DATA.keys():
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_bytes", NETWORK_DATA[each]["R_bytes"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_packets", NETWORK_DATA[each]["R_packets"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_errs", NETWORK_DATA[each]["R_errs"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_drop", NETWORK_DATA[each]["R_drop"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_fifo", NETWORK_DATA[each]["R_fifo"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_frame", NETWORK_DATA[each]["R_frame"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_compressed", NETWORK_DATA[each]["R_compressed"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_multicast", NETWORK_DATA[each]["R_multicast"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_bytes", NETWORK_DATA[each]["T_bytes"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_packets", NETWORK_DATA[each]["T_packets"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_errs", NETWORK_DATA[each]["T_errs"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_drop", NETWORK_DATA[each]["T_drop"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_fifo", NETWORK_DATA[each]["T_fifo"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_colls", NETWORK_DATA[each]["T_colls"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_carrier", NETWORK_DATA[each]["T_carrier"])
    #     return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_compressed", NETWORK_DATA[each]["T_compressed"])
    return Response(return_string, mimetype='text/plain')


def network_metrics_data(influx=False):
    return_string = ""
    with open("/proc/net/dev") as netfile:
        network_scrape = {}
        for netline in netfile.readlines():
            if "Inter" not in netline and "face" not in netline:
                line = netline.split()
                interface_name = line[0].strip(":")
                NETWORK_DATA[interface_name] = {}
                network_scrape["R_bytes"] = line[1]
                network_scrape["R_packets"] = line[2]
                network_scrape["R_errs"] = line[3]
                network_scrape["R_drop"] = line[4]
                network_scrape["R_fifo"] = line[5]
                network_scrape["R_frame"] = line[6]
                network_scrape["R_compressed"] = line[7]
                network_scrape["R_multicast"] = line[8]
                network_scrape["T_bytes"] = line[9]
                network_scrape["T_packets"] = line[10]
                network_scrape["T_errs"] = line[11]
                network_scrape["T_drop"] = line[12]
                network_scrape["T_fifo"] = line[13]
                network_scrape["T_colls"] = line[14]
                network_scrape["T_carrier"] = line[15]
                network_scrape["T_compressed"] = line[16]
                NETWORK_DATA[interface_name] = network_scrape
    for each in NETWORK_DATA.keys():
        if influx:
            return_string += 'NetworkStats,host=%s,interface=%s R_bytes=%s,R_packets=%s,R_errs=%s,R_drop=%s,R_fifo=%s,R_frame=%s,' \
                             'R_compressed=%s,R_multicast=%s,T_bytes=%s,T_packets=%s,T_errs=%s,T_drop=%s,T_fifo=%s,T_colls=%s,T_carrier=%s,T_compressed=%s \n' % \
                             (FLASK_HOSTNAME, each, NETWORK_DATA[each]["R_bytes"], NETWORK_DATA[each]["R_packets"], NETWORK_DATA[each]["R_errs"], NETWORK_DATA[each]["R_drop"], NETWORK_DATA[each]["R_fifo"], NETWORK_DATA[each]["R_frame"],
                              NETWORK_DATA[each]["R_compressed"], NETWORK_DATA[each]["R_multicast"], NETWORK_DATA[each]["T_bytes"], NETWORK_DATA[each]["T_packets"], NETWORK_DATA[each]["T_errs"], NETWORK_DATA[each]["T_drop"], NETWORK_DATA[each]["T_fifo"], NETWORK_DATA[each]["T_colls"], NETWORK_DATA[each]["T_carrier"], NETWORK_DATA[each]["T_compressed"])
        else:
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_bytes", NETWORK_DATA[each]["R_bytes"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_packets", NETWORK_DATA[each]["R_packets"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_errs", NETWORK_DATA[each]["R_errs"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_drop", NETWORK_DATA[each]["R_drop"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_fifo", NETWORK_DATA[each]["R_fifo"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_frame", NETWORK_DATA[each]["R_frame"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_compressed", NETWORK_DATA[each]["R_compressed"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "R_multicast", NETWORK_DATA[each]["R_multicast"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_bytes", NETWORK_DATA[each]["T_bytes"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_packets", NETWORK_DATA[each]["T_packets"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_errs", NETWORK_DATA[each]["T_errs"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_drop", NETWORK_DATA[each]["T_drop"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_fifo", NETWORK_DATA[each]["T_fifo"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_colls", NETWORK_DATA[each]["T_colls"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_carrier", NETWORK_DATA[each]["T_carrier"])
            return_string += 'NetworkStats{host="%s",interface="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, each, "T_compressed", NETWORK_DATA[each]["T_compressed"])
    return return_string


def network_metrics_thread():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("network_metrics_thread")
    historical_upload = ""
    while not THREAD_TO_BREAK.is_set():
        now = datetime.now()
        timestamp_string = str(int(now.timestamp()) * 1000000000)
        future = now + timedelta(seconds=30)
        influx_upload = ""
        influx_upload += network_metrics_data(influx=True)
        to_send = ""
        for each in influx_upload.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.info("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            function_logger.info("adding to history")
            historical_upload += influx_upload
        time_to_sleep = (future - datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            THREAD_TO_BREAK.wait(time_to_sleep)


@flask_app.route('/disk_metrics')
def disk_metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("disk_metrics")
    return_string = disk_metrics_data(influx=False)
    # output = subprocess.check_output(['df', '-BM'], stderr=subprocess.STDOUT).decode("utf-8")
    # for line in output.splitlines():
    #     element = line.split()
    #     if element[0] == "Filesystem":
    #         continue
    #     else:
    #         return_string += 'DiskStats{host="%s",filesystem="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, element[0], "total", element[1][:-1])
    #         return_string += 'DiskStats{host="%s",filesystem="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, element[0], "used", element[2][:-1])
    #         return_string += 'DiskStats{host="%s",filesystem="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, element[0], "avaliable", element[3][:-1])
    #         return_string += 'DiskStats{host="%s",filesystem="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, element[0], "pc", element[4][:-1])
    return Response(return_string, mimetype='text/plain')


def disk_metrics_data(influx=False):
    output = subprocess.check_output(['df', '-BM'], stderr=subprocess.STDOUT).decode("utf-8")
    return_string = ""
    for line in output.splitlines():
        element = line.split()
        if element[0] == "Filesystem":
            continue
        else:
            if influx:
                return_string += 'DiskStats,host=%s,filesystem="%s" total=%s,used=%s,avaliable=%s,pc=%s \n' % (FLASK_HOSTNAME, element[0], element[1][:-1], element[2][:-1], element[3][:-1], element[4][:-1])
            else:
                return_string += 'DiskStats{host="%s",filesystem="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, element[0], "total", element[1][:-1])
                return_string += 'DiskStats{host="%s",filesystem="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, element[0], "used", element[2][:-1])
                return_string += 'DiskStats{host="%s",filesystem="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, element[0], "avaliable", element[3][:-1])
                return_string += 'DiskStats{host="%s",filesystem="%s",measurement="%s"} %s \n' % (FLASK_HOSTNAME, element[0], "pc", element[4][:-1])
    return return_string


def disk_metrics_thread():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("disk_metrics_thread")
    historical_upload = ""
    while not THREAD_TO_BREAK.is_set():
        now = datetime.now()
        timestamp_string = str(int(now.timestamp()) * 1000000000)
        future = now + timedelta(seconds=30)
        influx_upload = ""
        influx_upload += disk_metrics_data(influx=True)
        to_send = ""
        for each in influx_upload.splitlines():
            to_send += each + " " + timestamp_string + "\n"
        if not historical_upload == "":
            function_logger.info("adding history to upload")
            to_send += historical_upload
        if update_influx(to_send):
            historical_upload = ""
        else:
            function_logger.info("adding to history")
            historical_upload += influx_upload
        time_to_sleep = (future - datetime.now()).seconds
        if 30 > time_to_sleep > 0:
            THREAD_TO_BREAK.wait(time_to_sleep)


def update_influx(raw_string, timestamp=None):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.debug("update_influx")
    try:
        string_to_upload = ""
        if timestamp is not None:
            timestamp_string = str(int(timestamp.timestamp()) * 1000000000)
            for each in raw_string.splitlines():
                string_to_upload += each + " " + timestamp_string + "\n"
        else:
            string_to_upload = raw_string
        success_array = []
        upload_to_influx_sessions = requests.session()
        for influx_url in INFLUX_DB_Path:
            success = False
            attempts = 0
            attempt_error_array = []
            while attempts < 5 and not success:
                try:
                    upload_to_influx_sessions_response = upload_to_influx_sessions.post(url=influx_url, data=string_to_upload, timeout=(2, 1))
                    if upload_to_influx_sessions_response.status_code == 204:
                        function_logger.debug("content=%s" % upload_to_influx_sessions_response.content)
                        success = True
                    else:
                        attempts += 1
                        function_logger.warning("status_code=%s" % upload_to_influx_sessions_response.status_code)
                        function_logger.warning("status_code=%s" % upload_to_influx_sessions_response.content)
                except requests.exceptions.ConnectTimeout as e:
                    attempts += 1
                    function_logger.debug("update_influx - attempted " + str(attempts) + " Failed Connection Timeout")
                    function_logger.debug("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
                    function_logger.debug("update_influx - Unexpected error:" + str(e))
                    function_logger.debug("update_influx - String was:" + str(string_to_upload).splitlines()[0])
                    function_logger.debug("update_influx - TRACEBACK=" + str(traceback.format_exc()))
                    attempt_error_array.append(str(sys.exc_info()[0]))
                except requests.exceptions.ConnectionError as e:
                    attempts += 1
                    function_logger.debug("update_influx - attempted " + str(attempts) + " Failed Connection Error")
                    function_logger.debug("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
                    function_logger.debug("update_influx - Unexpected error:" + str(e))
                    function_logger.debug("update_influx - String was:" + str(string_to_upload).splitlines()[0])
                    function_logger.debug("update_influx - TRACEBACK=" + str(traceback.format_exc()))
                    attempt_error_array.append(str(sys.exc_info()[0]))
                except Exception as e:
                    function_logger.error("update_influx - attempted " + str(attempts) + " Failed")
                    function_logger.error("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
                    function_logger.error("update_influx - Unexpected error:" + str(e))
                    function_logger.error("update_influx - String was:" + str(string_to_upload).splitlines()[0])
                    function_logger.debug("update_influx - TRACEBACK=" + str(traceback.format_exc()))
                    attempt_error_array.append(str(sys.exc_info()[0]))
                    break
            success_array.append(success)
        upload_to_influx_sessions.close()
        super_success = False
        for each in success_array:
            if not each:
                super_success = False
                break
            else:
                super_success = True
        if not super_success:
            function_logger.error("update_influx - FAILED after 5 attempts. Failed up update " + str(string_to_upload.splitlines()[0]))
            function_logger.error("update_influx - FAILED after 5 attempts. attempt_error_array: " + str(attempt_error_array))
            return False
        else:
            function_logger.debug("update_influx - " + "string for influx is " + str(string_to_upload))
            function_logger.debug("update_influx - " + "influx status code is  " + str(upload_to_influx_sessions_response.status_code))
            function_logger.debug("update_influx - " + "influx response is code is " + str(upload_to_influx_sessions_response.text[0:1000]))
            return True
    except Exception as e:
        function_logger.error("update_influx - something went bad sending to InfluxDB")
        function_logger.error("update_influx - Unexpected error:" + str(sys.exc_info()[0]))
        function_logger.error("update_influx - Unexpected error:" + str(e))
        function_logger.error("update_influx - TRACEBACK=" + str(traceback.format_exc()))
    return False


def graceful_killer(signal_number, frame):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("Got Kill signal")
    function_logger.info('Received:' + str(signal_number))
    THREAD_TO_BREAK.set()
    function_logger.info("set thread to break")
    cpu_update_thread.join()
    if INFLUX_MODE:
        cpu_thread.join()
        mem_thread.join()
        pressure_thread.join()
        pi_thread.join()
        network_thread.join()
        disk_thread.join()
    function_logger.info("joined all threads")
    if FLASK_MODE:
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
    logger.info("python prometheus script started")

    # Catch SIGTERM etc
    signal.signal(signal.SIGHUP, graceful_killer)
    signal.signal(signal.SIGTERM, graceful_killer)

    # Start the cron type jobs
    logger.info("start the cron update thread")
    cpu_update_thread = threading.Thread(target=lambda: get_latest_cpu_stats())
    cpu_update_thread.start()
    if INFLUX_MODE:
        cpu_thread = threading.Thread(target=lambda: cpu_metrics_thread())
        mem_thread = threading.Thread(target=lambda: memory_metrics_thread())
        pressure_thread = threading.Thread(target=lambda: pressure_metrics_thread())
        pi_thread = threading.Thread(target=lambda: pi_metrics_thread())
        network_thread = threading.Thread(target=lambda: network_metrics_thread())
        disk_thread = threading.Thread(target=lambda: disk_metrics_thread())
        cpu_thread.start()
        mem_thread.start()
        pressure_thread.start()
        pi_thread.start()
        network_thread.start()
        disk_thread.start()

    # Start WebServer
    if FLASK_MODE:
        logger.info("start web server")
        http_server = wsgiserver.WSGIServer(host=FLASK_HOST, port=FLASK_PORT, wsgi_app=flask_app)
        http_server.start()
