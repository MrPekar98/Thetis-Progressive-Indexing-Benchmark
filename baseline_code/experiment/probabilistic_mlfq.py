import os
import json
import random

# LIFO-style probabilistic MLFQ, where probabilities are assigned to the MLFQ levels and higher levels have higher probabilities to be selected during polling
class ProbabilisticMlfq:
    def __init__(self, file = '.mlfq', levels = 5):
        self.__levels = levels
        self.__file = file

        if not os.path.exists(file):
            mlfq = {'levels': dict()}

            for i in range(1, levels + 1):
                mlfq['levels'][str(i)] = list()

            self.__save(mlfq)
            self.__mlfq = mlfq

        else:
            self.__mlfq = self.__load()

    def __save(self, mlfq):
        with open(self.__file, 'w') as handle:
            json.dump(mlfq, handle)

    def __load(self):
        with open(self.__file, 'r') as handle:
            mlfq = json.load(handle)
            return mlfq

    def size(self):
        count = 0

        for level in range(1, self.__levels + 1):
            count += len(self.__mlfq['levels'][str(level)])

        return count

    def __prop_select_queue(self):
        prop = random.randint(0, 100)
        threshold = 50

        for i in range(self.__levels):
            if prop >= threshold:
                return i

            threshold /= 2

        return self.__levels - 1

    def poll(self):
        if self.size() == 0:
            return None

        level = self.__prop_select_queue() + 1

        while len(self.__mlfq['levels'][str(level)]) == 0:
            level = self.__prop_select_queue()

        table_count = len(self.__mlfq['levels'][str(level)])
        return self.__mlfq['levels'][str(level)][table_count - 1]

    def add_tables(self, tables):
        for table in tables:
            if not table in self.__mlfq['levels']['1']:
                self.__mlfq['levels']['1'].append(table)

    def move_table(self, table, new_level):
        if new_level <= 0 or new_level > self.__levels:
            raise 'New level is out of range'

        for level in range(1, self.__levels + 1):
            if table in self.__mlfq['levels'][str(level)]:
                self.__mlfq['levels'][str(level)].remove(table)

                if not table in self.__mlfq['levels'][str(new_level)]:
                    self.__mlfq['levels'][str(new_level)].append(table)

                return True

        return False

    def remove_table(self, table):
        for level in range(1, self.__levels + 1):
            if table in self.__mlfq['levels'][str(level)]:
                self.__mlfq['levels'][str(level)].remove(table)
                return True

        return False

    def levels(self):
        return self.__levels

    def level_of(self, table):
        for level in range(1, self.__levels + 1):
            if table in self.__mlfq['levels'][str(level)]:
                return level

        return -1

    def checkpoint(self):
        self.__save(self.__mlfq)
