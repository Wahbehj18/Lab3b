import csv
import argparse
import sys
group = None
blockSet = set([])
inodeSet = set([])
freeInodes = []
inodeList = []
direntList = []
IndirectList = []
bfreeList = []
superBlockObject = None
usedBlocks = {}

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
        self.inodeNumber = int(column[1])
        self.fileType = column[2]
        self.mode  = int(column[3])
        self.owner = int(column[4])
        self.group = int(column[5])
        self.linkCount = int(column[6])
        self.LastChange = column[7]
        self.ModificationTime = column[8]
        self.lastAccess = column[9]
        self.fileSize = int(column[10])
        self.DiskSpace = int(column[11])
        self.directBlocks = []
        self.indirectBlocks = []
        if self.fileType == 'f' or self.fileType == 'd':
            for x in range(12,24):
                self.directBlocks.append(int(column[x]))
            for x in range(24,27):
                self.indirectBlocks.append(int(column[x]))
        
        
class Block:
    def __init__(self, blockNumber, indirect, free, offset, inodeNum):
        self.blockNumber = blockNumber
        self.indirection = indirect # 0-direct, 1-single ...
        self.free = free
        self.offset = offset
        self.inodeNum = inodeNum

        
class Dirent:
    def __init__(self, column):
        self.ParentInode = int(column[1])
        self.ByteOffset = int(column[2])
        self.InodeNum = int(column[3])
        self.EntryLength = int(column[4])
        self.NameLength = int(column[5])
        self.Name = column[6]

class Indirect:
    def __init__(self, column):
        self.OwnerInode = int(column[1])
        self.IndirectionLevel = int(column[2])
        self.BlockOffset = int(column[3])
        self.BlockNum = int(column[4])
        self.BlockNumRef = int(column[5])


def BlockAudit(superBlock, groupObj):
    MaxBlocks = superBlock.BlockTotal
    FirstBlock = int(groupObj.FirstInodeBlockNum + superBlock.InodeSize * groupObj.TotalInodes / superBlock.blockSize)
    for x in inodeList:
        logicalOffset = 0
        for block in x.directBlocks:
            if block < 0 or block >= MaxBlocks:
                print("INVALID BLOCK {} IN INODE {} AT OFFSET {}".format(block, x.inodeNumber, logicalOffset))
            elif block != 0 and block < FirstBlock:
                print("RESERVED BLOCK {} IN INODE {} AT OFFSET {}".format(block, x.inodeNumber, logicalOffset))
            elif block != 0:
                if block not in usedBlocks:
                    usedBlocks[block] = [Block(block, 0, False, logicalOffset, x)]
                else:
                    usedBlocks[block].append(Block(block, 0, False, logicalOffset, x))             
            logicalOffset += 1
    return

def isFreeInode(iNum, superBlock):
    if iNum < superBlock.FirstNonReservedInode or iNum > superBlock.InodeTotal:
        return False
    elif iNum not in freeInodes:
        return False
    else:
        return True

def InodeAudit(superBlock):
    
    for i in inodeList:
        free = isFreeInode(i.inodeNumber, superBlock)
        if i.mode <= 0 and not free:
            print("UNALLOCATED INODE " + i.inodeNumber + " NOT ON FREELIST")

            
    for j in range(superBlock.FirstNonReservedInode,
                   1+ superBlock.InodeTotal):
        if j not in freeInodes:
            for n in inodeList:
                if j == n.inodeNumber:
                    allocated = True
            if not allocated:
                print("UNALLOCATED INODE " + j + " NOT ON FREELIST")

def DirectoryAudit():
    return

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
       
    for row in fileReader:
        if row[0] == "SUPERBLOCK":
            superBlockObject = Superblock(row)

        elif row[0] == "BFREE":
            bfreeList.append(int(row[1]))
            #blockSet.add(Block(int(row[1]), 0, True, 0))
        elif row[0] == "INDIRECT":
            IndirectList.append(Indirect(row))
            #blockSet.add(Block(int(row[5]), int(row[2]), False, int(row[4])))
        elif row[0] == "GROUP":
            group = Group(row)
        elif row[0] == "IFREE":
            freeInodes.append(int(row[1]))
            #inodeSet.add(int(row[1]))
        elif row[0] == "INODE":
            inodeList.append(Inode(row))
        elif row[0] == "DIRENT":
            direntList.append(Dirent(row))
    
    #print(superBlockObject)
    #for b in blockSet:
    #       print(b.blockNumber)

    print("Nodes")
    for i in inodeList:
        print(i.inodeNumber)
            
    print("free")
    for i in freeInodes:
        print(i)
    print("all")
    for j in range(superBlockObject.FirstNonReservedInode, 1+ superBlockObject.InodeTotal):
        print(j)
        

    BlockAudit(superBlockObject, group)
    InodeAudit(superBlockObject)        
    return

if __name__ == '__main__':
    main()

