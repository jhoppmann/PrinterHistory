from mysql_connection import Connector


class StatisticsCalculator:

    def __init__(self, source: 'Connector'):
        self.source = source

    def numbers_by_printers(self) -> dict:
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

    def numbers_by_printers_cleaned(self) -> dict:
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

    def print_time(self) -> int:
        data = self.source.load_data()
        time = 0
        for line in data:
            print_time = line['PRINT_TIME']
            time += int(print_time)
        return time

    def print_time_by_printer(self) -> dict:
        data = self.source.load_data()
        times = {}
        for line in data:
            print_time = line['PRINT_TIME']
            printer = line['MACHINE']
            if printer not in times:
                times[printer] = 0
            times[printer] += int(print_time)
        return times
