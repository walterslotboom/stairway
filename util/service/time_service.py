#
# time_service.py
#
# miscellaneous time and timing functions
#
import copy
from datetime import datetime, timedelta, timezone
import time

import pytz
import tzlocal

time.clock()


class TimeService:

    SECONDS_IN_MINUTE = 60
    MINUTES_IN_HOUR = 60
    HOURS_IN_DAY = 24
    SECONDS_IN_DAY = SECONDS_IN_MINUTE * MINUTES_IN_HOUR * HOURS_IN_DAY

    @staticmethod
    def utc_now():
        return datetime.utcnow().replace(tzinfo=timezone.utc)

    @staticmethod
    def convert_datetime_to_timestamp(dt=None, tz_name=None):
        if (dt, tz_name) == (None, None):
            utc_ts = TimeService.utc_now()

        else:
            if dt is None:
                dt = datetime.now()
            if tz_name is None:
                tz_name = str(tzlocal.get_localzone())

            # Python's native handling of timezones is borked...
            # Start with a naive (ie., no timezone) datetime object and localize it via pyzt
            if dt.tzinfo is not None:
                raise AssertionError("'dt' should be a naive datetime object (no timezone specified)")
            local_ts = pytz.timezone(tz_name).localize(dt)

            utc_ts = local_ts.astimezone(pytz.utc)  # Convert to UTC

        # return calendar.timegm(utc_ts.timetuple())  # Return Unix timestamp
        return utc_ts.timestamp()

    @staticmethod
    def convert_timestamp_to_datetime(unix_ts=None, tz_name=None, naive=False):
        # Converts a Unix timestamp (seconds since epoch) to a datetime object,
        # localized for the specified timezone.
        #
        # If naive is requested, then the timezone info is stripped from the
        # datetime object (although the value is still localized).
        if unix_ts is None:
            unix_ts = TimeService.convert_datetime_to_timestamp()
        if tz_name is None:
            tz_name = str(tzlocal.get_localzone())
        local_dt = datetime.fromtimestamp(unix_ts, pytz.timezone(tz_name))
        if naive:
            local_dt = local_dt.replace(tzinfo=None)
        return local_dt

    @staticmethod
    def convert_timestamp_to_date(unix_ts=None, tz_name=None, naive=False):
        return TimeService.convert_timestamp_to_datetime(unix_ts, tz_name, naive).date()

    @staticmethod
    def trim_timestamp_to_seconds(unix_ts=None, tz_name=None, naive=False):
        return TimeService.convert_timestamp_to_datetime(unix_ts, tz_name, naive).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def trim_timestamp_to_milliseconds(unix_ts=None, tz_name=None, naive=False):
        return TimeService.convert_timestamp_to_datetime(unix_ts, tz_name, naive).strftime('%Y-%m-%d %H:%M:%S.%f')[:23]

    @staticmethod
    def convert_days_to_seconds(days):

        return days * TimeService.SECONDS_IN_DAY

    @staticmethod
    def convert_seconds_to_whole_days(seconds):

        return seconds // TimeService.SECONDS_IN_DAY

    @staticmethod
    def convert_seconds_to_partial_days(seconds):

        return seconds / TimeService.SECONDS_IN_DAY

    @staticmethod
    def convert_timestamp_to_days_ago(timestamp):

        seconds_ago = TimeService.convert_datetime_to_timestamp() - timestamp
        days_ago = TimeService.convert_seconds_to_whole_days(seconds_ago)
        return days_ago

    @staticmethod
    def convert_days_ago_to_timestamp(days_ago):
        return TimeService.convert_datetime_to_timestamp() - TimeService.convert_days_to_seconds(days_ago)

    @staticmethod
    def convert_duration_string_to_seconds(s):
        """
        convert string to number of seconds
            <int>[smhdw]
        """
        time_multiplier = {
            's': 1,
            'm': TimeService.SECONDS_IN_MINUTE,
            'h': TimeService.SECONDS_IN_MINUTE * TimeService.MINUTES_IN_HOUR,
            'd': TimeService.SECONDS_IN_DAY,
            'w': TimeService.SECONDS_IN_DAY * 7,
        }
        if s[-1] not in time_multiplier:
            raise ValueError('invalid duration string, must end with one of {!r}'.format(''.join(time_multiplier)))
        num = int(s[:-1])
        return num * time_multiplier[s[-1]]

    class StopWatch(object):
        def __init__(self, cpu=False, name=''):
            self._name = name or "StopWatch<{}>".format(id(self))

            self._starttime = -1
            self._endtime = 0
            self._accum = 0
            self._running = False

            self._start_timestamp = None
            self._end_timestamp = None

            if cpu:
                self._timefn = time.clock
            else:
                self._timefn = time.time

            self.clear()

        def __str__(self):
            return "{}: ({!s:.23}::{!s:.23})".format(self._name, self._start_timestamp, self._end_timestamp)

        def __contains__(self, other):
            if isinstance(other, (int, float)):
                other = datetime.utcfromtimestamp(float(other)).replace(tzinfo=timezone.utc)

            if self._start_timestamp is None:
                if self._end_timestamp is None:
                    raise IndexError("cannot check containment with no start or end time")
                else:
                    return other <= self._end_timestamp
            else:
                if self._end_timestamp is None:
                    return self._start_timestamp <= other
                else:
                    return self._start_timestamp <= other <= self._end_timestamp

        def offset(self, pre=0, post=0):
            # Returns a copy of this stopwatch, with slightly offset start and/or
            # end times, to accommodate out-of-sync clocks across servers when
            # matching up logs or other events.
            #
            # To return a stopwatch that is 1 second earlier at start and 1 second
            # later at end, call stopwatch.offset(-1, 1)
            #
            # If handling comparisons where a timewindow is measure to milliseconds
            # but the test time is truncated to whole seconds, use stopwatch.offset(-1, 0)

            ret = copy.copy(self)
            if pre and ret._start_timestamp:
                ret._starttime += pre
                ret._start_timestamp += timedelta(seconds=pre)
            if post and ret._end_timestamp:
                ret._endtime += post
                ret._end_timestamp += timedelta(seconds=post)

            return ret

        @property
        def elapsed(self) -> float:
            if self._starttime < 0:
                return 0

            if self._endtime:
                return self._endtime - self._starttime
            else:
                return self._timefn() - self._starttime

        @property
        def elapsed_timedelta(self) -> timedelta:
            return timedelta(seconds=self.total_elapsed)

        @property
        def total_elapsed(self):
            if self._running:
                return self._accum + self.elapsed
            else:
                return self._accum

        @property
        def start_timestamp(self):
            return self._start_timestamp

        @property
        def end_timestamp(self):
            return self._end_timestamp

        @property
        def running(self):
            return self._running

        def start(self):
            if not self._running:
                self._starttime = self._timefn()
                self._start_timestamp = TimeService.utc_now()
                self._end_timestamp = None

            self._running = True
            return self

        def stop(self):
            if self._running:
                self._endtime = self._timefn()
                self._end_timestamp = TimeService.utc_now()
                self._accum += self.elapsed

            self._running = False
            return self

        def restart(self):
            return self.clear().start()

        def clear(self):
            self._starttime = -1
            self._endtime = 0
            self._accum = 0
            self._running = False
            return self

        def __enter__(self):
            self.start()
            time.sleep(0.5)
            return self

        def __exit__(self, *args):
            time.sleep(0.5)
            self.stop()

        def __bool__(self):
            return self._start_timestamp is not None


if __name__ == '__main__':

    sw = TimeService.StopWatch()
    sw.start()
    time.sleep(2)
    test = TimeService.utc_now()
    time.sleep(2)
    sw.stop()
    print(sw, test, test in sw)

    sw = TimeService.StopWatch()
    sw.start()
    time.sleep(2)
    sw.stop()
    test = TimeService.utc_now()
    print(sw, test, test in sw)

    sw = TimeService.StopWatch()
    sw.start()
    time.sleep(2)
    test = time.time()
    time.sleep(2)
    sw.stop()
    print(sw, test, test in sw)
