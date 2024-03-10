import datetime
import unittest
from io import StringIO
from unittest.mock import patch
import os
from lib import Reader, Processor, Writer


class TestTimeRecorder(unittest.TestCase):
    def setUp(self):
        self.testInput = "Date;Event;Gate\n" \
                        "2019-02-04 09:05:58 ;Reader entry;E/0/KD1/7-9\n" \
                        "2019-02-04 09:07:03 ;Reader entry;E/3/KD1/3-8\n" \
                        "2019-02-04 17:32:34 ;Reader exit;E/3/KD1/3-8\n" \
                        "2019-02-04 19:33:03 ;Reader exit;E/0/KD1/7-8\n" \
                        "2019-02-05 09:10:34 ;Reader entry;E/0/KD1/7-9\n" \
                        "2019-02-05 09:11:35 ;Reader entry;E/3/KD1/3-8\n" \
                        "2019-02-05 15:26:36 ;Reader entry;E/0/KD1/8-8\n" \
                        "2019-02-06 09:21:57 ;Reader entry;E/0/KD1/7-9\n" \
                        "2019-02-06 09:22:27 ;Reader entry;E/3/KD1/3-8\n" \
                        "2019-02-06 12:07:06 ;Reader exit;E/3/KD1/3-8\n" \
                        "2019-02-06 12:07:54 ;Reader entry;E/0/KD1/7-8\n" \
                        "2019-02-06 12:23:43 ;Reader entry;E/0/KD1/7-9\n" \
                        "2019-02-06 12:24:31 ;Reader entry;E/3/KD1/3-8\n" \
                        "2019-02-06 16:09:44 ;Reader exit;E/0/KD1/8-8\n" \
                        "2019-02-07 09:09:57 ;Reader entry;E/0/KD1/7-9\n" \
                        "2019-02-07 09:10:27 ;Reader entry;E/3/KD1/3-8\n" \
                        "2019-02-07 10:56:26 ;Reader exit;E/3/KD1/3-8\n" \
                        "2019-02-07 10:57:18 ;Reader entry;E/0/KD1/7-8\n" \
                        "2019-02-07 11:05:01 ;Reader entry;E/0/KD1/7-9\n" \
                        "2019-02-07 11:06:40 ;Reader exit;E/2/KD1/4-8\n" \
                        "2019-02-07 12:33:01 ;Reader entry;E/3/KD1/3-8\n" \
                        "2019-02-07 18:33:50 ;Reader exit;E/0/KD1/7-8 "
        self.expectedOutput = "Day 2019-02-04 Work 10:27:05 ot\n" \
                              "Day 2019-02-05 Work 6:16:02 i\n" \
                              "Day 2019-02-06 Work 6:47:47\n" \
                              "Day 2019-02-07 Work 9:23:53 ot 32:54:47 00:54:47\n"
        self.inputFile = "input_test.csv"
        self.outputFile = "result.txt"

    def tearDown(self):
        try: os.remove(self.inputFile)
        except FileNotFoundError: pass
        try: os.remove(self.outputFile)
        except FileNotFoundError: pass

    def test_reader(self):
        with open(self.inputFile, 'w') as file:
            file.writelines(self.testInput)
        reader = Reader(self.inputFile)
        self.assertEqual(reader.data[0], (datetime.datetime(2019, 2, 4, 9, 5, 58), 'entry', 'E/0/KD1/7-9'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_readerNoInput(self, mock_stdout):
        Reader('wrongName.csv')
        self.assertEqual(mock_stdout.getvalue(), "File reading error\n")

    def test_processor(self):
        dataCleaned = [(datetime.datetime(2019, 2, 4, 9, 5, 58), 'entry', 'E/0/KD1/7-9'),
                       (datetime.datetime(2019, 2, 4, 19, 33, 3), 'exit', 'E/0/KD1/7-8')]
        with open(self.inputFile, 'w') as file:
            file.writelines(self.testInput)
        reader = Reader(self.inputFile)
        process = Processor(reader.data)
        self.assertEqual(process.data[:2], dataCleaned[:2])

    def test_computations(self):
        with open(self.inputFile, 'w') as file:
            file.writelines(self.testInput)
        reader = Reader(self.inputFile)
        process = Processor(reader.data)
        process.compute()
        self.assertEqual(' '.join(process.result[0]), self.expectedOutput.split('\n')[0])

    def test_writer(self):
        with open(self.inputFile, 'w') as file:
            file.writelines(self.testInput)
        reader = Reader(self.inputFile)
        process = Processor(reader.data)
        process.compute()
        Writer(process.result)
        with open(self.outputFile, 'r') as rf:
            actualOutput = ''.join(rf.readlines())
        self.assertEqual(self.expectedOutput, actualOutput)



