FLASK_HOST = "::"
FLASK_PORT = 8050
FLASK_HOSTNAME = "example.com"
ABSOLUTE_PATH = "/Users/phbridge/Documents/Git/Python_Prometheus_Host_Stats"
LOGFILE = ABSOLUTE_PATH + "/logs/Python_Prometheus_Host_Stats_%s_%s.log" % (FLASK_HOST, FLASK_PORT)
INFLUX_MODE = True
FLASK_MODE = False
INFLUX_DB_PATH = ["https://influx-pri.test.co.uk:8086/write?db=<DBNAME>&u=<UserName>&p=<Password>","https://influx-sec.test.co.uk:8086/write?db=<DBNAME>&u=<UserName>&p=<Password>"]
