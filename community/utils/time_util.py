import datetime
import time


class TimeUtil(object):
    """docstring for timeUtil"""
    @staticmethod
    def get_utc_time():
        utc_time = time.mktime(datetime.datetime.utcnow().timetuple())
        return utc_time
