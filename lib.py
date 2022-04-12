import csv
from datetime import datetime, timedelta

class HeaderError(Exception):
    pass


class EventError(Exception):
    pass


class MyTimeDelta(timedelta):
    def __str__(self):
        seconds = self.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        out = '{:02d}:{:02d}:{:02d}'.format(int(hours), int(minutes), int(seconds))
        return out


class Reader:
    def __init__(self, filename):
        self.data = []
        self.read(filename)

    def no_blank(self, file):
        try:
            while True:
                line = next(file)
                if len(line.strip()) != 0:
                    yield line
        except StopIteration:
            return

    def read(self, filename):
        try:
            with open(filename, newline="") as inputFile:
                header = [h.strip() for h in inputFile.__next__().split(";")]
                if set(header) != {'Date', 'Gate', 'Event'}:
                    raise HeaderError

                reader = csv.DictReader(self.no_blank(inputFile), delimiter=";", fieldnames=header)
                for row in reader:
                    if any(field.strip() for field in row):
                        dt = datetime.strptime(row['Date'].strip(), '%Y-%m-%d %H:%M:%S')
                        if "entry" in row['Event'].lower():
                            event = "entry"
                        elif "exit" in row['Event'].lower():
                            event = "exit"
                        else:
                            raise EventError
                        gate = row['Gate'].strip()
                        self.data.append((dt, event, gate))

            self.data.sort(key=lambda tup: tup[0])
            return self.data

        except IOError:
            print("File reading error")
        except ValueError:
            print("Wrong data format")
        except EventError:
            print("Wrong event format")
        except HeaderError:
            print("Wrong header format")
        except StopIteration:
            print("File empty")
        except Exception:
            print("Other error")


class Processor:
    def __init__(self, data):
        self.data = data
        self.result = []
        self.cleanData()
        self.compute()

    def cleanData(self):
        self.removeCentral()
        self.removeRepetitons()

    def removeCentral(self):
        try:
            for i in range(len(self.data)):
                while self.data[i][0].date() == self.data[i+2][0].date():
                    self.data.pop(i+1)
        except IndexError:
            pass

    def removeRepetitons(self):
        try:
            for i in range(len(self.data)):
                while self.data[i][0] == self.data[i + 1][0]:
                    self.data.pop(i + 1)
        except IndexError:
            pass

    def compute(self):
        workTimeWeek = MyTimeDelta()
        overTimeWeek = MyTimeDelta()
        while self.data:
            start = self.data[0]
            if len(self.data) == 1:
                end = start
                del self.data[:1]
            elif self.data[0][0].date() != self.data[1][0].date():
                end = start
                del self.data[:1]
            else:
                end = self.data[1]
                del self.data[:2]

            timeAtWork = end[0] - start[0]

            workTimeWeek += timeAtWork
            overTimeWeek += timeAtWork - timedelta(hours=8)

            resultRecord = ["Day", str(start[0].date()), "Work", str(timeAtWork)]

            inconclusivity = self.checkInconclusive(start, end)
            overtime = self.checkOvertime(timeAtWork)
            weekendDay = self.checkWeekend(start[0].weekday())

            if inconclusivity: resultRecord.append(inconclusivity)
            if overtime: resultRecord.append(overtime)
            if weekendDay: resultRecord.append(weekendDay)

            if self.isLastInWeek(start[0].date(), self.getNextDay()):
                resultRecord += [str(MyTimeDelta(seconds=workTimeWeek.total_seconds())),
                                 str(MyTimeDelta(seconds=overTimeWeek.total_seconds()))]
                workTimeWeek = MyTimeDelta()
                overTimeWeek = MyTimeDelta()

            self.result.append(resultRecord)

    def checkInconclusive(self, start, end):
        return False if start[1] == "entry" and end[1] == "exit" else "i"

    def checkOvertime(self, timeAtWork):
        if timeAtWork < timedelta(hours=6):
            return "ut"
        elif timeAtWork > timedelta(hours=9):
            return "ot"
        else:
            return False

    def checkWeekend(self, day):
        return "w" if day == 5 or day == 6 else False

    def isLastInWeek(self, thisDay, nextDay):
        if not nextDay:
            return True
        sundayDate = thisDay + timedelta(6 - thisDay.weekday())
        return True if nextDay > sundayDate else False

    def getNextDay(self):
        return self.data[0][0].date() if self.data else None


class Writer:
    def __init__(self, data):
        with open("result", "w") as outputFile:
            for row in data:
                outputFile.writelines(" ".join(row) + "\n")