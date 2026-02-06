import argparse
import csv
import datetime
import os.path
import re
from dataclasses import dataclass
from typing import List


class HourMin:
    def __init__(self, hour_min_str: str = None, minutes: int = None):
        if hour_min_str is not None:
            hours, minutes_ = list(map(int, hour_min_str.split(':')))
            self.minutes = hours * 60 + minutes_
        if minutes is not None:
            self.minutes = minutes

    def __add__(self, other):
        return HourMin(minutes=self.minutes + other.minutes)

    def __sub__(self, other):
        if other.minutes > self.minutes:
            other_ = HourMin(minutes=other.minutes - 24 * 60)
        else:
            other_ = other
        return HourMin(minutes=self.minutes - other_.minutes)

    def __str__(self):
        return ':'.join([f'{x:02}' for x in divmod(self.minutes, 60)])

    @property
    def hours(self):
        return self.minutes // 60


@dataclass
class Activity:
    start_minutes: int
    duration: HourMin
    formatted_line: str
    comment: str = None
    client: str = None


class Day:

    def __init__(self, date: datetime.datetime = None):
        self.date = date
        self.day_total = HourMin(minutes=0)
        self.activities: List[Activity] = []

    def get_comments(self):
        return [a.comment for a in sorted(self.activities, key=lambda a: a.start_minutes) if a.comment is not None]

    def get_clients(self):
        seen = set()
        clients = []
        for a in sorted(self.activities, key=lambda a: a.start_minutes):
            if a.client is not None and a.client not in seen:
                seen.add(a.client)
                clients.append(a.client)
        return clients


def write_csv(csv_path: str, days: List[Day]):
    with open(csv_path, 'w') as csv_file:
        field_names = ['date', 'duration', 'comments']
        writer = csv.DictWriter(csv_file, fieldnames=field_names, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for day in days:
            writer.writerow({
                'date': day.date.date(),
                'duration': day.day_total,
                'comments': '; '.join(day.get_comments())
            })


def main(input_path: str):
    file_name = os.path.basename(input_path)
    full_path = os.path.abspath(input_path)
    dir_path = os.path.dirname(full_path)
    new_full_path = os.path.join(dir_path, f'new_{file_name}')
    path, _ = os.path.splitext(full_path)
    new_csv_path = path + '.csv'

    pattern = re.compile('([0-9]{1,2}:[0-9]{2})-([0-9]{1,2}:[0-9]{2})(?: (.*))?')
    client_pattern = re.compile(r'^(.*?)\s*\[(\w+)\]$')

    # Parse all days first
    days = []
    day = Day()
    with open(full_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            # New day?
            try:
                date = datetime.datetime.strptime(line.strip(), '%Y-%m-%d')
                if day.date is None:
                    day.date = date
                    continue
                else:
                    raise Exception
            except ValueError:
                pass

            # Hours?
            result = re.match(pattern, line)
            if result is not None:
                from_ = result.group(1)
                to_ = result.group(2)
                comment = result.group(3)

                client = None
                if comment is not None:
                    client_match = re.match(client_pattern, comment)
                    if client_match:
                        comment = client_match.group(1)
                        client = client_match.group(2)

                diff = HourMin(to_) - HourMin(from_)
                day.day_total += diff

                new_line = line.rstrip('\n').replace(f'{from_}-{to_}', f'{from_}-{to_} ({diff})')
                start_minutes = HourMin(from_).minutes
                day.activities.append(Activity(start_minutes, diff, new_line, comment, client))

            # Day over?
            if (line.strip() == '' or i == len(lines) - 1) and day.day_total.minutes > 0:
                day.activities.sort(key=lambda a: a.start_minutes)
                days.append(day)
                day = Day()
            elif result is None:
                print(f'Warning, didn\'t parse: "{line}"')

    # Sort days by date and write output
    days.sort(key=lambda d: d.date)

    with open(new_full_path, 'w') as nf:
        for day in days:
            nf.write(day.date.strftime('%Y-%m-%d') + '\n')
            for a in day.activities:
                nf.write(a.formatted_line + '\n')
            nf.write(f'\nTotal: {day.day_total}\n\n')

            print(day.date.date())
            print(day.day_total)
            print('\n'.join(day.get_comments()) + '\n')

    if new_csv_path:
        write_csv(new_csv_path, days)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Calculate durations of my work...'
    )
    parser.add_argument('input_file', type=str, help='Input file')
    args = parser.parse_args()
    main(args.input_file)
