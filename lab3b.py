import csv
import argparse

    
class Superblock:
    def __init__(self, column):
        self.BlockTotal = int(column[1])
        self.InodeTotal = int(column[2])
        self.blockSize  = int(column[3])
        self.InodeSize  = int(column[4])
        self.BlocksPerGroup = int(column[5])
        self.InodesPerGroup = int(column[6])
        self.FirstNonReservedInode = int(column[7])

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

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
        self.fileType = str(column[2])

        
class Block:
    def __init__(self, blockNumber, indirect, free, offset):
        self.blockNumber = blockNumber
        self.indirection = indirect # 0-direct, 1-single ...
        self.free = free
        self.offset = offset

        
class Dirent:
    def __init__(self, column):
        self.Name = int(column[6])



def main():
    parser = argparse.ArgumentParser(description='Parse CSV file')
    parser.add_argument('csvFile', help='CSV file to parse')
    args = parser.parse_args()

    #print(args.csvFile)
    if not ".csv" in args.csvFile:
        print("Error File is not valid CSV")
        return 1

    try:
        csvFile = open(args.csvFile, "r")
    except IOError:
        print("Error File does not exist")
        return 1

    fileReader = csv.reader(csvFile)
    group = []
    blockSet = set([])
    inodeSet = set([])
    for row in fileReader:
        #print(','.join(row))
        if row[0] == "SUPERBLOCK":
            super = Superblock(row)
        elif row[0] == "BFREE":
            blockSet.add(Block(int(row[1]), 0, True, 0))
        elif row[0] == "INDIRECT":
            blockSet.add(Block(int(row[5]), int(row[2]), False, int(row[4])))
            
        
    for b in blockSet:
        print(b.blockNumber)

            

if __name__ == '__main__':
    main()

