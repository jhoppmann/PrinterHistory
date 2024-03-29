import statistics
from datetime import datetime

from mysql_connection import Connector


def get_month(date: datetime) -> str:
    ret = str(date.year) + '-' + str(date.month).rjust(2, '0')
    return ret


class StatisticsCalculator:

    def __init__(self, source: 'Connector'):
        self.source = source

    def cumulative_prints(self, data: dict = None) -> dict:
        """Returns a dict with overall prints, excluding those under a minute."""
        if data is None:
            data = self.source.load_data()
        prints = 0
        successes = 0
        fails = 0
        for line in data:
            if line['PRINT_TIME'] < 60:
                continue
            prints += 1
            if line['STATUS'] == 'Print Failed':
                fails += 1
            else:
                successes += 1
        return {"SUCCESSES": successes,
                "FAILS": fails,
                "PRINTS": prints}

    def fail_rate_by_printers(self, data: dict = None) -> dict:
        """Returns a dict with the printer name as keys and the fail rate as value."""
        if data is None:
            data = self.source.load_data()
        return_value = {}
        data_by_printer = {}
        for line in data:
            if line['PRINT_TIME'] < 60:
                continue
            printer = line['MACHINE']
            if printer not in data_by_printer:
                data_by_printer[printer] = (0, 0)
            failed_addition = 0
            if line['STATUS'] == 'Print Failed':
                failed_addition = 1
            data_by_printer[printer] = (data_by_printer[printer][0] + 1, data_by_printer[printer][1] + failed_addition)

            for printer, values in data_by_printer.items():
                fails = values[1]
                prints = values[0]
                return_value[printer] = fails / prints
        return return_value

    def numbers_by_printers(self, data: dict = None) -> dict:
        """Returns a dict of print statuses mapped to machine identifiers."""
        if data is None:
            data = self.source.load_data()
        return_value = {}
        for line in data:
            printer = line['MACHINE']
            status = line['STATUS']
            if printer not in return_value:
                return_value[printer] = {}
            status_count = return_value[printer]
            if status not in status_count:
                status_count[status] = 0
            status_count[status] = status_count[status] + 1
        return return_value

    def numbers_by_printers_cleaned(self, data: dict = None) -> dict:
        """Returns a dict of print statuses mapped to machine identifiers. Prints with a total duration of under a
        minute are exluded."""
        if data is None:
            data = self.source.load_data()
        return_value = {}
        for line in data:
            if line['PRINT_TIME'] < 60:
                continue
            printer = line['MACHINE']
            status = line['STATUS']
            if printer not in return_value:
                return_value[printer] = {}
            status_count = return_value[printer]
            if status not in status_count:
                status_count[status] = 0
            status_count[status] = status_count[status] + 1
        return return_value

    def print_time(self, data: dict = None) -> dict:
        """Returns a dict containing one item, PRINT_TIME, with the total logged duration over all printers."""
        if data is None:
            data = self.source.load_data()
        time = sum([x['PRINT_TIME'] for x in data])
        return {"PRINT_TIME": time}

    def print_time_by_printer(self, data: dict = None) -> dict:
        """Returns a dict of total print times mapped to the machine on which they were logged"""
        if data is None:
            data = self.source.load_data()
        times = {}
        for line in data:
            print_time = line['PRINT_TIME']
            printer = line['MACHINE']
            if printer not in times:
                times[printer] = 0
            times[printer] += int(print_time)
        return times

    def mean_print_length(self, data: dict = None) -> dict:
        """Returns a dict containing one key, PRINT_TIME, with a value of mean print time logged over all printers."""
        if data is None:
            data = self.source.load_data()
        print_times = [int(x['PRINT_TIME']) for x in data]
        return {"PRINT_TIME": statistics.mean(print_times)}

    def prints_by_month_and_printer(self, data: dict = None) -> dict:
        """Provides a dict containing months in the format MM-yyyy. Every month contains another dict with all printers
        that logged print time in that month. Every printer item is its own dict, containing the keys PRINTS (overall
        prints in that month), TIME (print time in that month), SUCCESS (successful prints) and FAIL (failed prints)."""
        if data is None:
            data = self.source.load_data()
        result = {}
        for line in data:
            if line['PRINT_TIME'] < 60:
                continue
            printer = line['MACHINE']
            month = get_month(line['DATE'])
            if month not in result:
                result[month] = {}
            month_data = result[month]
            if printer not in month_data:
                month_data[printer] = {'PRINTS': 0, 'TIME': 0, 'SUCCESS': 0, 'FAIL': 0}
            month_data[printer]['PRINTS'] += 1
            month_data[printer]['TIME'] += line['PRINT_TIME']
            if line['STATUS'] == 'Print Failed':
                month_data[printer]['FAIL'] += 1
            else:
                month_data[printer]['SUCCESS'] += 1
        return result

    def all_data(self) -> dict:
        """Calls every statistics method and puts the result into a dict."""
        result = {}
        data = self.source.load_data()
        result['PRINT_TIME'] = self.print_time(data)
        result['PRINT_TIME_BY_PRINTER'] = self.print_time_by_printer(data)
        result['MEAN_PRINT_LENGTH'] = self.mean_print_length(data)
        result['NUMBERS_BY_PRINTER_CLEANED'] = self.numbers_by_printers_cleaned(data)
        result['PRINTS_BY_MONTH_AND_PRINTER'] = self.prints_by_month_and_printer(data)
        result['CUMULATIVE_PRINTS'] = self.cumulative_prints(data)
        result['FAIL_RATE_BY_PRINTERS'] = self.fail_rate_by_printers(data)

        return result
