import csv
import argparse
import sys
group = None
blockSet = set([])
inodeSet = set([])
freeInodes = []
inodeList = []
direntList = []
indirectList = []
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

#    def __str__(self):
#        return str(self.__class__) + ": " + str(self.__dict__)

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

def InvalidAndReserved(MaxBlocks, FirstBlock, superBlock, groupObj):
    for x in inodeList:
        logicalOffset = 0
        for block in x.directBlocks:
            if block < 0 or block >= MaxBlocks:
                print("INVALID BLOCK {} IN INODE {} AT OFFSET {}".format(block, x.inodeNumber, logicalOffset))
            elif block != 0 and block < FirstBlock:
                print("RESERVED BLOCK {} IN INODE {} AT OFFSET {}".format(block, x.inodeNumber, logicalOffset))
            elif block != 0:
                if block not in usedBlocks:
                    usedBlocks[block] = [Block(block, 0, False, logicalOffset, x.inodeNumber)]
                else:
                    usedBlocks[block].append(Block(block, 0, False, logicalOffset, x.inodeNumber))
            logicalOffset += 1
        indirectionLevel = 1
        for indirect in x.indirectBlocks:
            level = ""
            logicalOffset = 12
            if indirectionLevel == 2:
                level = "DOUBLE "
                logicalOffset = 268
            elif indirectionLevel == 3:
                level = "TRIPLE "
                logicalOffset = 65804
            if indirect < 0 or indirect >= MaxBlocks:
                print("INVALID {}INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(level, indirect, x.inodeNumber, logicalOffset))
            elif indirect != 0 and indirect < FirstBlock:
                print("RESERVED {}INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(level, indirect, x.inodeNumber, logicalOffset))
            elif indirect != 0:
                if indirect not in usedBlocks:
                    usedBlocks[indirect] = [Block(indirect, indirectionLevel, False, logicalOffset, x.inodeNumber)]
                else:
                    usedBlocks[indirect].append(Block(indirect, indirectionLevel, False, logicalOffset, x.inodeNumber)) 
            indirectionLevel += 1
    for element in indirectList:
        level = ""
        if element.IndirectionLevel == 2:
            level = "DOUBLE "
        elif element.IndirectionLevel == 3:
            level = "TRIPLE "
        blockReference = element.BlockNumRef
        if blockReference < 0 or blockReference >= MaxBlocks:
            print("INVALID {}INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(level, blockReference, element.OwnerInode, element.BlockOffset))
        elif blockReference != 0 and blockReference < FirstBlock:
            print("RESERVED {}INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(level, blockReference, element.OwnerInode, element.BlockOffset))
        elif blockReference != 0:
            if blockReference not in usedBlocks:
                usedBlocks[blockReference] = [Block(blockReference, element.IndirectionLevel, False, element.BlockOffset, element.OwnerInode)]
            else:
                usedBlocks[blockReference].append(Block(blockReference, element.IndirectionLevel, False, element.BlockOffset, element.OwnerInode))
    return

def UnreferencedAndAllocated(MaxBlocks, FirstBlock, superBlock, groupObj):
    for x in range(FirstBlock, MaxBlocks):
        if not (x in bfreeList or x in usedBlocks): #not in free list or used
            print("UNREFERENCED BLOCK {}".format(x))
        if not (x not in bfreeList or x not in usedBlocks): #in free list and used
            print("ALLOCATED BLOCK {} ON FREELIST".format(x))
    return


def FindDuplicates(MaxBlocks, FirstBlock, superBlock, groupObj):
    for i in range(FirstBlock, MaxBlocks):
        if i in usedBlocks:
            if len(usedBlocks[i]) > 1:
                for x in usedBlocks[i]:
                    level = ""
                    if x.indirection == 1:
                        level = "INDIRECT "
                    elif x.indirection == 2:
                        level = "DOUBLE INDIRECT "
                    elif x.indirection == 3:
                        level = "TRIPLE INDIRECT "
                    print("DUPLICATE {}BLOCK {} IN INODE {} AT OFFSET {}".format(level, x.blockNumber, x.inodeNum, x.offset))
    return
            
def BlockAudit(superBlock, groupObj):
    MaxBlocks = superBlock.BlockTotal
    FirstBlock = int(groupObj.FirstInodeBlockNum + superBlock.InodeSize * groupObj.TotalInodes / superBlock.blockSize)
    InvalidAndReserved(MaxBlocks, FirstBlock, superBlock, groupObj)
    UnreferencedAndAllocated(MaxBlocks, FirstBlock, superBlock, groupObj)
    FindDuplicates(MaxBlocks, FirstBlock, superBlock, groupObj)
    return


def InodeAudit():
    for i in 
    return

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
            indirectList.append(Indirect(row))
            #blockSet.add(Block(int(row[5]), int(row[2]), False, int(row[4])))
        elif row[0] == "GROUP":
            group = Group(row)
        elif row[0] == "IFREE":
            freeInodes.append(int(row[1]))
            inodeSet.add(int(row[1]))
        elif row[0] == "INODE":
            inodeList.append(Inode(row))
        elif row[0] == "DIRENT":
            direntList.append(Dirent(row))
        
    for b in blockSet:
        print(b.blockNumber)

    BlockAudit(superBlockObject, group)
            

if __name__ == '__main__':
    main()

