import os
import json

# FIFO-style MLFQ
class Mlfq:
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

    def poll(self):
        for level in range(1, self.__levels):
            if len(self.__mlfq['levels'][str(level)]) > 0:
                table = self.__mlfq['levels'][str(level)][0]
                return table

        return None

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
