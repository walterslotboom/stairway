#
# misc_service.py
#

# Miscellaneous namespace classes for helpful services, such as:
# - ListService
# - IntegerService
# - IteratorService
# - StringService
# - CredentialsService
#
from argparse import ArgumentTypeError
import ast
import random
from itertools import chain, combinations, filterfalse, islice
from operator import attrgetter
import re


class ListService:

    @staticmethod
    def get_item_by_value(lst, field, value):
        return next((x for x in lst if getattr(x, field) == value), None)

    @staticmethod
    def get_median_ish(lst, field):
        # not a true median since we do not divide middle values for even-length list
        tmp = sorted(lst, key=attrgetter(field))
        mid_point = len(tmp) // 2
        median = getattr(tmp[mid_point], field)
        return median

    @staticmethod
    def get_midpoint(lst, field):
        # compute midpoint as halfway between min and max attribute value

        # convert input sequence of objects to sequence of attribute values
        lst_values = map(attrgetter(field), lst)

        # use minmax to get min and max of the input sequence in a single pass
        hi, lo = ListService._minmax(lst_values)

        # compute midpoint
        midpoint = lo + ((hi - lo) // 2)

        return midpoint

    @staticmethod
    def get_random(lst, field):
        random_seed = random.choice(list(lst))
        random_value = getattr(random_seed, field)
        return random_value

    @staticmethod
    def pop_random(lst):
        pop_index = random.randrange(len(lst))
        random_item = lst.pop(pop_index)
        return random_item

    @staticmethod
    def resample(population, k):
        # Chooses k random elements (with replacement) from a population
        population = list(population)
        random_choice = random.choice
        return [random_choice(population) for _ in range(k)]

    @staticmethod
    def _minmax(lst):
        # internal method to find min and max values in a sequence in a single pass
        lst_iter = iter(lst)
        hi = lo = next(lst_iter)
        for val in lst_iter:
            if val < lo:
                lo = val
            elif val > hi:
                hi = val
        return hi, lo


class IntegerService:

    @staticmethod
    def get_number_of_digits(integer):
        string = str(integer)
        return len(string)

    @staticmethod
    def get_number_of_chunks(total, chunk_size):
        # compute number of chunks of size chunk_size needed for total
        # (round up to next number if there is a remainder)
        #    get_number_of_chunks(10, 1) -> 10
        #    get_number_of_chunks(10, 2) -> 5
        #    get_number_of_chunks(10, 3) -> 4
        #    get_number_of_chunks(10, 10) -> 1
        #    get_number_of_chunks(10, 20) -> 1
        #
        # Uses floor division of the negative of total, which gives
        # the next lowest number, and then negates to give next highest
        # number instead.
        return -(-total // chunk_size)

    @staticmethod
    def pad_leading_zeroes(integer, digits):
        return str(integer).zfill(digits)

    @staticmethod
    def extract_integer_range(range_string):
        ret = []
        for piece in range_string.split(','):
            if '-' in piece:
                from_, to_ = map(int, piece.split('-'))
                ret.extend(range(from_, to_ + 1))
            else:
                ret.append(int(piece))
        return list(set(ret))

    @staticmethod
    def h2b(intstr):
        kilo = 1000
        kibi = 1024
        mult = {None: 1,
                '': 1,
                'B': 1,
                'kilo': kilo,
                'kibi': kibi,
                'M': kilo ** 2,
                'MB': kibi ** 2,
                'G': kilo ** 3,
                'GB': kibi ** 3,
                'T': kilo ** 4,
                'TB': kibi ** 4,
                'P': kilo ** 5,
                'PB': kibi ** 5,
                'E': kilo ** 6,
                'EB': kibi ** 6,
                }

        if isinstance(intstr, int):
            return intstr
        elif intstr.isdigit():
            return int(intstr)
        else:
            match = re.match(r'(\d+(?:\.\d*)?)\s*([KMGTPE]?B?)?', intstr.upper())
            if not match:
                raise ValueError('invalid value {!r}'.format(intstr))
            num, suffix = (tuple(match.groups()) + ('',))[:2]
            try:
                return int(float(num) * mult[suffix])
            except KeyError as ke:
                raise Exception("invalid suffix {!r} (intstr:{!r}, match:{!r}".format(suffix, intstr, match)) from ke

    @staticmethod
    def b2h(intval, radix=1000, suffix=''):
        div_suffix = [
            (radix ** 8, 'Y'),  # yotta
            (radix ** 7, 'Z'),  # zetta
            (radix ** 6, 'E'),  # eta
            (radix ** 5, 'P'),  # peta
            (radix ** 4, 'T'),  # tera
            (radix ** 3, 'G'),  # giga
            (radix ** 2, 'M'),  # mega
            (radix ** 1, 'K'),  # kilo
        ]
        for div, mult_suffix in div_suffix:
            if intval >= div:
                if intval % div != 0:
                    return "{:.2f}{}{}".format(intval / div, mult_suffix, suffix)
                else:
                    return "{}{}{}".format(int(intval / div), mult_suffix, suffix)
        return str(intval)

    class IntegerBitSet:
        def __init__(self, intvalue):
            self._intvalue = intvalue

        def __contains__(self, intmask):
            return (self._intvalue & intmask) == intmask

    @staticmethod
    def h2b_arg_type(s):
        try:
            return IntegerService.h2b(s)
        except Exception as e:
            raise ArgumentTypeError("invalid value {!r}: {}".format(s, str(e)))


class IteratorService:

    @staticmethod
    def power_set(iterable, min_count=0):
        # set of recurse subsets of iterable
        # power_set([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
        s = list(iterable)
        ps_chain = chain.from_iterable(combinations(s, r) for r in range(min_count, len(s) + 1))
        yield from ps_chain

    @staticmethod
    def dedupes(iterable, key=None):
        # List unique elements, preserving order. Remember recurse elements ever seen.
        # dedupes('AAAABBBCCDAABBB') --> A B C D
        seen = set()
        seen_add = seen.add
        if key is None:
            for element in filterfalse(seen.__contains__, iterable):
                seen_add(element)
                yield element
        else:
            for element in iterable:
                k = key(element)
                if k not in seen:
                    seen_add(k)
                    yield element

    @staticmethod
    def clip(n):
        """
        Create a filter to return the first 'n' items
        """

        def clipper(seq):
            yield from islice(seq, 0, n)

        return clipper

    @staticmethod
    def repeat(n):
        """
        Create a repeater that takes a sequence and
        returns a new sequence where each item of the original
        sequence is repeated 'n' times
        """

        def repeater(seq):
            it = iter(seq)
            while True:
                x = next(it)
                yield from (x for _ in range(n))

        return repeater

    @staticmethod
    def chunks(chunk_size):
        """
        Create a chunker that takes a sequence and returns
        a series of smaller sequences each of 'chunk_size' size,
        plus a final chunk with any remaining items; the returned
        sequences are created to be the same time as the given
        sequence if str or bytes, otherwise chunks are returned as
        lists.
        """

        def chunker(seq):
            seq_iter = iter(seq)
            join_fn = {bytes: bytes,
                       str: ''.join}.get(type(seq), list)
            while True:
                cur = join_fn(islice(seq_iter, chunk_size))
                if not cur:
                    break
                yield cur

        return chunker

    # @staticmethod
    # def time_range_clip(start, end):
    #     """
    #     Create a filter that will take a sequence of (timestamp, item) pairs
    #     and return recurse the items where start <= timestamp <= end
    #     """
    #
    #     def clipper(seq, chronological_order=True):
    #         if chronological_order:
    #             initial_filter = lambda a_b: a_b[0] < start
    #             trailing_filter = lambda a_b: a_b[0] <= end
    #         else:
    #             initial_filter = lambda a_b: a_b[0] > end
    #             trailing_filter = lambda a_b: a_b[0] >= start
    #
    #         # skip recurse leading items that don't match the initial_filter
    #         seq = dropwhile(initial_filter, seq)
    #
    #         # don't do this - does not stop reading sequence after hitting trailing timestamp
    #         #     yield from (item for ts, item in seq if trailing_filter(ts))
    #         # use takewhile instead
    #         yield from (item for ts, item in takewhile(trailing_filter, seq))
    #
    #     return clipper


class StringService:
    # characters that can be used for object tags (omit characters like
    # 'l', 'g', etc. that might be mistaken for numeric digits)
    # use lower case for ease of typing/grepping
    TAG_CHARS = 'abcdefhjkmnprstuvwxyz0123456789'

    @staticmethod
    def make_tag(chars=TAG_CHARS, size=6):
        # make a random tag for easy visual comparison of object names
        # - not guaranteed to be unique, so not sufficient for algorithmic
        # comparison, but helpful for human eyeballs
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def unescape(s):
        # clean up strings that have escaped byte characters (such as those received over REST interface)
        # return ast.literal_eval("'''{}'''".format(s))
        # return ast.literal_eval("{!r}".format(s))
        cr_marker = 'ZZZZZZZZZ'
        lf_marker = 'YYYYYYYYY'
        eval_str = "r'''" + s.replace(r'\r', cr_marker).replace(r'\n', lf_marker) + "'''"
        try:
            ret = ast.literal_eval(eval_str)
            return ret.replace(cr_marker, '\r').replace(lf_marker, '\n')
        except SyntaxError:
            return s

    @staticmethod
    def input_secret(prompt, default=None):
        """
        Input a string from the terminal, without visibly echoing the input while it is being typed.

        :param prompt: Displayed prompt string
        :type prompt: str
        :param default: Default value if empty string is input (user just hits <RETURN>)
        :type default: str
        :return: string entered by user
        :rtype: str
        """
        import getpass
        input_value = getpass.getpass(prompt)
        if not input_value and default is not None:
            input_value = default
        return input_value

    @staticmethod
    def lclip(s: str, clipstring: str) -> str:
        # remove leading clipstring from a string, if clipstring is present
        if s.startswith(clipstring):
            return s[len(clipstring):]
        else:
            return s

    @staticmethod
    def rclip(s: str, clipstring: str) -> str:
        # remove trailing clipstring from a string, if clipstring is present
        if s.endswith(clipstring):
            return s[:-len(clipstring)]
        else:
            return s

    @staticmethod
    def clip(s: str, clipstring: str) -> str:
        # combined lclip and rclip
        s = StringService.lclip(s, clipstring)
        s = StringService.rclip(s, clipstring)
        return s

    @staticmethod
    def parse_name_with_index(s: str) -> dict:
        """
        Method to parse a test that might have a trailing numeric index into
        base and index parts. If no index is present, then index is returned as
        ''.
        :param s:
        :return: {'base': base_part_of_s, 'index': trailing_numeric_part_of_s}
        """
        name_with_numeric_suffix_re = re.compile(r'(?P<base>.*?)(?P<index>\d*)$')
        return name_with_numeric_suffix_re.match(s).groupdict()

    @staticmethod
    def pluralize(s: str, qty: int = 0):
        """
        Method to make a singular noun plural, following basic rules of English:
        - ends in 'y' not preceded by a vowel: drop 'y' and add 'ies'
        - ends in 'ss', 'ch', or 'sh': add 'es'
        - ends in 'us': add 'ses'
        - add 's'

        Matches case with trailing part of s (in case s in title case).

        Caller can pass in a quantity value so that this method can determine
        whether pluralizing is necessary; saves on many 'if qty != 1' tests,
        and avoids 'if qty > 1' bugs (qty <= 0 should return plural, not
        singular).
        """
        if qty == 1:
            return s

        # example special cases (only works if singular and plural start with same char):
        specials = {
            'mouse': 'mice',
            'goose': 'geese',
            'octopus': 'octopi',
        }

        # if irregulars are omitted, add rule or special
        s_lower = s.lower()
        if s_lower in specials:
            s, app = s[0], specials[s_lower][1:]
        elif s_lower.endswith('y') and s_lower[-2] not in 'aeiou':
            s = s[:-1]
            app = 'ies'
        elif s_lower.endswith(("ss", "ch", "sh", "x", "z")):
            app = 'es'
        elif s_lower.endswith('us'):
            app = 'ses'
        else:
            app = 's'

        if s[-1].isupper():
            app = app.upper()

        return s + app

    @staticmethod
    def quantified(qty: int, noun: str):
        return "{} {}".format(qty, StringService.pluralize(noun, qty))

    @staticmethod
    def glob2re(s):
        # convert glob notation using '*' and '?' as character wildcards to a regular expression
        for c in ".[](){}+":
            s = s.replace(c, '\\' + c)
        return (s.replace('*', '.*')
                .replace('?', '.'))


class ArgumentService:

    @staticmethod
    def delimited_string_to_list_converter(type_converter=str, str_delim=','):
        def conv_func(var_str=''):
            l1 = var_str.split(str_delim)
            ret_list = []
            for x in l1:
                if x:
                    try:
                        ret_list.append(type_converter(x))
                    except ValueError:
                        raise ArgumentTypeError("{} in {} is not a valid value".format(x, var_str))
            return ret_list

        return conv_func


class ReflectionService:

    @staticmethod
    def get_class_from_string(module_name, class_name):
        return getattr(module_name, class_name)
