import argparse
import datetime
import os.path
import re
import csv


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


class Day:

    def __init__(self, date: datetime.datetime = None):
        self.date = date
        self.day_total = HourMin(minutes=0)
        self.comments = []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Calculate durations of my work...'
    )
    parser.add_argument('input_file', type=str, help='Input file')
    args = parser.parse_args()
    file_name = args.input_file
    full_path = os.path.abspath(file_name)
    dir_path = os.path.dirname(full_path)
    new_full_path = os.path.join(dir_path, f'new_{file_name}')
    path, _ = os.path.splitext(full_path)
    new_csv_path = path + '.csv'

    pattern = re.compile('([0-9]{1,2}:[0-9]{2})-([0-9]{1,2}:[0-9]{2})(?: (.*))?')

    with open(new_csv_path, 'w') as csv_file:
        field_names = ['date', 'duration', 'comments']
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        with open(new_full_path, 'w') as nf:
            with open(full_path, 'r') as f:
                days = []
                day = Day()
                lines = f.readlines()
                for i, line in enumerate(lines):
                    # New day?
                    try:
                        date = datetime.datetime.strptime(line.strip(), '%d/%m/%Y')
                        nf.write(line)
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
                        match = result.group(0)
                        from_ = result.group(1)
                        to_ = result.group(2)
                        comment = result.group(3)
    
                        diff = HourMin(to_) - HourMin(from_)
                        day.day_total += diff
                        if comment is not None:
                            day.comments.append(comment)
    
                        new_line = line.replace(f'{from_}-{to_}', f'{from_}-{to_} ({diff})')
                        nf.write(new_line)
    
                    # Day over?
                    if (line.strip() == '' or i == len(lines) - 1) and day.day_total.minutes > 0:
                        nf.write(f'Total: {day.day_total}\n')
                        days.append(day)
                        print(day.date.date())
                        print(day.day_total)
                        print('\n'.join(day.comments) + '\n')
                        writer.writerow({
                            'date': day.date.date(),
                            'duration': day.day_total,
                            'comments': '; '.join(day.comments)
                        })
                        # Reset
                        day = Day()
                        nf.write('\n')
                    elif result is None:
                        print(f"Warning, didn't parse: \"{line}\"")
                        nf.write(line)
