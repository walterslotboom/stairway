import sys
import time
from src.util.service.report_service import ReportService, IReport


# __all__ = ("SleepService",)


class SleepService(object):
    """
    A wrapper for python's sleep with text to notify the user that it is
    sleeping.
    """

    @staticmethod
    def sleep(seconds, msg='Unspecified reason', delimiter=".", trailing=True,
              level=IReport.Level.none):
        seconds = float(seconds)
        if seconds > 0:

            # trick to limit seconds output to 3 decimal places, but also
            # strip trailing zeros.
            formatted_seconds = ("%.3f" % seconds).rstrip("0").rstrip(".")

            if msg is not None:
                msg = "Sleep %s second(s): %s" % (formatted_seconds, msg)
                ReportService.report(msg, level=level)
            while seconds > 0:
                interval = min(seconds, 1)
                time.sleep(interval)
                sys.stdout.write(delimiter)
                sys.stdout.flush()
                seconds -= interval
            if trailing:
                sys.stdout.write("\n")


if __name__ == '__main__':
    SleepService.sleep(3, "Three")
