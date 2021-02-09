import contextlib
import sys
from src.util.enums import OrderedEnum
from src.util.service.time_service import TimeService


class IReport:

    class Level(OrderedEnum):
        debug = 10
        detail = 20
        info = 23
        crucial = 26
        warning = 30
        error = 50
        fatal = 60
        none = 70

    class Patency(OrderedEnum):
        minor = 10
        medium = 20
        major = 30

    INDENT_DEPTH = 4


class ReportService:
    """
    Report messages to console via stdout
    """

    # for unit testing,
    #   outbuf = StringIO()
    #   ReportService.outputter = outbuf
    #   ...
    #   # test contents of outbuf
    outputter = sys.stdout
    
    level_threshold = IReport.Level.detail
    
    @staticmethod
    def report(message='', level=IReport.Level.none, patency=IReport.Patency.minor, delimiter="∞", length=10,
               lead=None, trail=None, timestamp=True):
        """
        format and write report message to stdout
        :param level:  one of IReport.LEVELS values
        :param patency:  one of IReport.LEVELS values
        :param message:  the report message
        :param delimiter:  attention getting character used to bracket the report message
        :param length: number delimiter repeats for MEDIUM patency & minimum delimiter repeats for MAJOR patency
        :param lead: if True the prepend a newline to the output
        :param trail:  if True to append a newline to the output
        :param timestamp: if True append a timestamp to output
        """
        if level < ReportService.level_threshold:
            return
        formatted_message = ReportService.format(message, level, patency, delimiter, length, lead, trail, timestamp)
        ReportService.outputter.write(formatted_message)
        ReportService.outputter.flush()

    @staticmethod
    def format(message='', level=IReport.Level.none, patency=IReport.Patency.minor, delimiter="∞", length=10,
               lead=None, trail=None, timestamp=True):
        """
        format and return the given report message
        :param level:  one of IReport.LEVEL values
        :param patency:  one of IReport.PATENCY values
        :param message:  the report message
        :param delimiter:  attention getting character used to bracket the report message
        :param length: number delimiter repeats for MEDIUM patency & minimum delimiter repeats for MAJOR patency
        :param lead: if True the prepend a newline to the output
        :param trail:  if True to append a newline to the output
        :param timestamp: if True append a timestamp to output
        :return str: the formatted report message string
        """
        template = "%s"
        if timestamp:
            message = '%s  %s' % (TimeService.trim_timestamp_to_seconds(), message)

        if level not in IReport.Level:
            raise Exception(IReport.Level.error + " report level '%s' not in valid levels %s" % (level, IReport.Level))
        elif patency not in IReport.Patency:
            raise Exception(IReport.Level.error + " report patency '%s' not in valid patencies %s" %
                            (patency, IReport.Patency))
        else:
            if patency == IReport.Patency.minor:
                if level != IReport.Level.none:
                    message = '[{}] {}'.format(str(level), message)
                template = "%s"
                if lead is None:
                    lead = False
                if trail is None:
                    trail = True
            elif patency == IReport.Patency.medium:
                affix = delimiter * length
                template = affix + " %s " + affix
                if lead is None:
                    lead = True
                if trail is None:
                    trail = True
            elif patency == IReport.Patency.major:
                affix_len = min(max(len(line) for line in message.splitlines()), 79)
                affix_len = max(affix_len, length)
                affix = delimiter * affix_len
                template = affix + "\n%s\n" + affix + "\n"
                if lead is None:
                    lead = True
                if trail is None:
                    trail = True
        if lead:
            template = "\n%s" % template
        if trail:
            template = "%s\n" % template
        # template = '{} {}'.format(TimeService.convert_timestamp_to_datetime(), template)
        return template % message

    @staticmethod
    def format_error(msg='', delimiter='!', length=10, lead=False, trail=False):
        """
        format and return the given report error message
        :param msg:  the error message
        :param delimiter:  NOT USED
        :param length: NOT USED
        :param lead: if True the prepend a newline to the output
        :param trail:  if True to append a newline to the output
        :return str: the formatted report message string
        """
        return ReportService.format(msg, IReport.Level.error, IReport.Patency.minor, delimiter=delimiter, length=length,
                                    lead=lead, trail=trail)

    @staticmethod
    def format_info(msg='', delimiter='∞', length=10, lead=False, trail=False):
        """
        format and return the given report info message
        :param msg:  the error message
        :param delimiter:  NOT USED
        :param length: NOT USED
        :param lead: if True the prepend a newline to the output
        :param trail:  if True to append a newline to the output
        :return str: the formatted report message string
        """
        return ReportService.format(msg, IReport.Level.info, IReport.Level.MINOR, delimiter=delimiter, length=length,
                                    lead=lead, trail=trail)

    @staticmethod
    def _report_phase_transition(phase, transition, delimiter):
        ReportService.report('{} {} phase'.format(transition, phase),
                             IReport.Level.none, IReport.Patency.medium, delimiter, timestamp=False)

    @staticmethod
    @contextlib.contextmanager
    def demarcate(message='', level=IReport.Level.none, patency=IReport.Patency.minor, delimiters=('>', '<'),
                  trail=True):
        ReportService.report('Entering: {}'.format(message), level, patency, delimiters[0], trail=trail)
        phase_timer = TimeService.StopWatch()
        try:
            with phase_timer:
                yield
        finally:
            elapsed = phase_timer.elapsed_timedelta
            message = '{}; Elapsed: {}'.format(message, elapsed)
            ReportService.report('Exiting: {}'.format(message), level, patency, delimiters[1])

    @staticmethod
    def indent(message, indent):
        return str(message).rjust(len(message) + indent*IReport.INDENT_DEPTH)

    # @contextlib.contextmanager
    # def phase_report(self, phase_name):
    #     ACase._report_phase_transition(phase_name, 'Entering', '>')
    #     phase_timer = TimeService.StopWatch()
    #     try:
    #         with phase_timer:
    #             yield
    #     finally:
    #         ReportService.report("{}/{} elapsed time: {}".format(self.test,
    #                                                              phase_name,
    #                                                              phase_timer.elapsed_timedelta))
    #         ACase._report_phase_transition(phase_name, 'Exiting', '<')
