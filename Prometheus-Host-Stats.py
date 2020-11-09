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
# import sys                              # for error to catch and debug
# import traceback                        # helps add more logging infomation
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
# DEVICES_JSON = multiprocessing_manager.dict({})
CPU_DATA_LIST = multiprocessing_manager.Array([])
# MAX_THREADS = 3

flask_app = Flask(__name__)


def five_seconds_interval(interval=5):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("metrics")
    response_string = ""
    for each in CPU_DATA_LIST[0]:
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s,interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "user", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["user"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["user"]))
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "nice", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["nice"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["nice"]))
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "system", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["system"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["system"]))
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "idle", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["idle"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["idle"]))
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "iowait", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["iowait"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["iowait"]))
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "irq", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["irq"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["irq"]))
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "softirq", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["softirq"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["softirq"]))
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "steal", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["steal"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["steal"]))
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "guest", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["guest"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["guest"]))
        response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (each["cpu_name"], FLASK_HOST, "guest_nice", interval,
                                                                                         (CPU_DATA_LIST[0][each["cpu_name"]]["guest_nice"] -
                                                                                          CPU_DATA_LIST[1][each["cpu_name"]]["guest_nice"]))
    return response_string


def fifteen_seconds_interval(interval=15):
    print("nothing")


def one_min_interval(interval=60):
    print("nothing")


def five_min_interval(interval=300):
    print("nothing")


def get_latest_cpu_stats():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("get_latest_cpu_stats")
    while not THREAD_TO_BREAK.is_set():
        t = datetime.today()
        future = datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
        future += timedelta(seconds=5)
        THREAD_TO_BREAK.wait((future - t).seconds)
        if THREAD_TO_BREAK.is_set():
            return
        with open("/proc/stat") as cpufile:
            cputimes = cpufile.readline().split(" ")
            cpu_scrape = {}
            if "cpu" in cputimes[0]:
                cpu_scrape[cputimes[0]] = {}
                cpu_scrape[cputimes[0]]['cpu_name'] = cputimes[0]
                cpu_scrape[cputimes[0]]['user'] = cputimes[1]
                cpu_scrape[cputimes[0]]['nice'] = cputimes[2]
                cpu_scrape[cputimes[0]]['system'] = cputimes[3]
                cpu_scrape[cputimes[0]]['idle'] = cputimes[4]
                cpu_scrape[cputimes[0]]['iowait'] = cputimes[5]
                cpu_scrape[cputimes[0]]['irq'] = cputimes[6]
                cpu_scrape[cputimes[0]]['softirq'] = cputimes[7]
                cpu_scrape[cputimes[0]]['steal'] = cputimes[8]
                cpu_scrape[cputimes[0]]['guest'] = cputimes[9]
                cpu_scrape[cputimes[0]]['guest_nice'] = cputimes[10]
            global CPU_DATA_LIST
            CPU_DATA_LIST.append(cpu_scrape)
            CPU_DATA_LIST = CPU_DATA_LIST[-120:]

        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s,interval=%s} %s" % (cputimes[0], FLASK_HOST, "user", interval, cputimes[1])
        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (cputimes[0], FLASK_HOST, "nice", interval, cputimes[2])
        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (cputimes[0], FLASK_HOST, "system", interval, cputimes[3])
        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (cputimes[0], FLASK_HOST, "idle", interval, cputimes[4])
        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (cputimes[0], FLASK_HOST, "iowait", interval, cputimes[5])
        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (cputimes[0], FLASK_HOST, "irq", interval, cputimes[6])
        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (cputimes[0], FLASK_HOST, "softirq", interval, cputimes[7])
        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (cputimes[0], FLASK_HOST, "steal", interval, cputimes[8])
        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (cputimes[0], FLASK_HOST, "guest", interval, cputimes[9])
        # response_string += "CPUUsage{cpu=%s, host=%s, measurement=%s interval=%s} %s" % (cputimes[0], FLASK_HOST, "guest_nice", interval, cputimes[10])


@flask_app.route('/metrics')
def metrics():
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("metrics")
    return_string = ""
    return_string += five_seconds_interval()
    return Response(return_string, mimetype='text/plain')


def graceful_killer(signal_number, frame):
    function_logger = logger.getChild("%s.%s.%s" % (inspect.stack()[2][3], inspect.stack()[1][3], inspect.stack()[0][3]))
    function_logger.info("Got Kill signal")
    function_logger.info('Received:' + str(signal_number))
    THREAD_TO_BREAK.set()
    function_logger.info("set thread to break")
    update_thread.join()
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
    update_thread = threading.Thread(target=lambda: get_latest_cpu_stats())
    update_thread.start()

    # Delete/Create Webhooks
    logger.info("start web server")
    http_server = wsgiserver.WSGIServer(host=FLASK_HOST, port=FLASK_PORT, wsgi_app=flask_app)
    http_server.start()
