import csv
import argparse

def checkArgs():
    parser = argparse.ArgumentParser(description='Parse CSV file')
    parser.add_argument('csvFile', help='CSV file to parse')
    args = parser.parse_args()

    #print(args.csvFile)
    if not ".csv" in args.csvFile:
        print("Error File is not valid CSV")
        return 1
    
    try:
        open(args.csvFile, "r")
    except IOError:
        print("Error File does not exist")
        return 1
class Superblock:
    def __init__(self, column):
        self.BlockTotal = int(column[1])
        self.InodeTotal = int(column[2])
        self.blockSize  = int(column[3])
        self.InodeSize  = int(column[4])
        self.BlocksPerGroup = int(column[5])
        self.InodesPerGroup = int(column[6])
        self.FirstNonReservedInode = int(column[7])

class Group:
    def __init__(self, column):
        self.GroupNum = int(column[1])
        self.TotalBlocks = int(column[2])
        self.TotalInodes  = int(column[3])
        self.NumFreeBlocks = int(column[4])
        self.NumFreeInodes = int(column[5])
        self.BlockBitmap = int(column[6])
        self.InodeBitmap = int(column[7])
        self.FirstInodeBlockNum = int(column[8])


class Inode:
    def __init__(self, column):
        self.InodeNumber = int(column[1])


class Dirent:
    def __init__(self, column):
        self.Name = int(column[6])

class Indirect:
    def __init__(self, column):
        self.InodeNumber = int(column[1])


def main():
    checkArgs()

if __name__ == '__main__':
    main()

