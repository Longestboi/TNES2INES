#/bin/python
import sys
import os
import argparse
import zlib

parser = argparse.ArgumentParser(description='Convert TNES roms to INES roms')
group = parser.add_mutually_exclusive_group()

parser.add_argument("Input", help="TNES Rom")
group.add_argument("-i", "--romInfo", help="Show TNES rom info", action="store_true")
group.add_argument("-x", "--extract", help="Extract PRG and CHR roms (or FDS bios and FDS .qd, if input is a FDS game) from TNES input", action="store_true")
group.add_argument("-c", "--convert", help="Convert TNES rom to INES", action="store_true")

args = parser.parse_args()

def readFileMagic(file):
    file.seek(0, 0)
    byte = file.read(4)
    return byte

def readTNESHeader(file):
    file.seek(4, 0)
    byte = file.read(12)
    return byte

file = open(args.Input, 'rb')

class TNESHeader:

    TNESHeaderMinusMagic = bytes(readTNESHeader(file))

    def getMapper(self, outputNumber=False):
        mapper = self.TNESHeaderMinusMagic[0]
        TNESMappers = ["NROM", "SxROM", "PNROM", "TxROM", "FxROM", "ExROM", "UxROM", "CNROM", "AxROM", "FDS"] 
        if (mapper == 9):
            a = 8
        if (mapper == 100):
            a = 9
        else:
            a = mapper
        if (outputNumber == True):
            return a
        return TNESMappers[a]
    
    def getPRGSize(self):
        prgMultiple = self.TNESHeaderMinusMagic[1]
        if (prgMultiple == 0):
            return "No PRG rom"
        else:
            prgRomSize = prgMultiple * 8192
            return prgRomSize

    def getCHRSize(self):
        chrMultiple = self.TNESHeaderMinusMagic[2]
        if (chrMultiple == 0):
            return "No CHR rom"
        else:
            chrRomSize = chrMultiple * 8192
            return chrRomSize 

    def hasWRAM(self):
        boolean = self.TNESHeaderMinusMagic[3]
        if (boolean == 0):
            return "No"
        if (boolean == 1):
            return "Yes"
        else:
            return "Couldn't check if game uses WRAM"

    def getMirroring(self):
        mirror = self.TNESHeaderMinusMagic[4]
        if (mirror == 0):
            return "Mapper controlled"
        if (mirror == 1):
            return "Horizontal"
        if (mirror == 2):
            return "Vertical"
        else:
            return "Couldn't find mirroring type"

    def hasBattery(self):
        bat = self.TNESHeaderMinusMagic[5]
        if (bat == 0):
            return "No"
        if (bat == 1):
            return "Yes"
        else:
            return "Couldn't find if game uses a battery"

    def getFDSBioscrc32(self, file):
        file.seek(16, 0)
        biosCRC32 = zlib.crc32(file.read(8192))
        biosCRC32 = str(hex(biosCRC32)[2:])
        return biosCRC32

    def getSidePerDiskCount(self):
        sides = self.TNESHeaderMinusMagic[6]
        mod = sides / 2
        if (((mod % 2) == 0)):
            sides = mod
        return str(int(sides))

    def getDiskCount(self):
        sides = int(self.getSidePerDiskCount())
        if (sides == 1):
            disks = 1.0
        if ((sides % 2) == 0):
            disks = sides / 2
        return str(disks)[:-2]

class TNESExtractor:
    def extPRGRom(self, PRGSize):
        #Seek to constant prg rom location
        file.seek(16, 0)

        return file.read(PRGSize)
        
    def extCHRRom(self, PRGSize, CHRSize):
        #Seek to variable chr rom location
        chrseek = PRGSize + 16
        file.seek(chrseek, 0)
        
        return file.read(CHRSize)
        
    def dumpFDSBios(self, file, crc32):
        bios = open(crc32 + "-fds.bin", 'wb')
        file.seek(16, 0)
        bios.write(file.read(8192))
        bios.close
    
    def extQD(self, file):
        qd = open(args.Input[:-4] + ".qd", 'wb')
        file.seek(8208, 0)
        qd.write(file.read())
        qd.close()

    def saveToFile(self, extension, inFile):
        dump = open(args.Input[:-4] + extension, 'wb')
        dump.write(inFile)
        dump.close()

class TNESConv:
    def retINESMagic(self):
        return "NES\x1A"

    def retSizeOfRomMultipleKB(self, ROMSize, PRGorCHR):
        if (ROMSize == "No CHR rom" or ROMSize == "No PRG rom"):
            return bytes(1)
        if (PRGorCHR == "prg" or PRGorCHR == "PRG"):
            size = int(int(ROMSize) / 16000)
        elif (PRGorCHR == "chr" or PRGorCHR == "CHR"):
            size = int(int(ROMSize) / 8000)
        return size.to_bytes(1, byteorder="big")


header = TNESHeader()
extracter = TNESExtractor()
convert = TNESConv()

if (readFileMagic(file).decode("utf-8") == "TNES"):
    pass
else:
    print("not a TNES file")
    exit()


### Used for the romInfo argument ###
if ((args.romInfo == True) or (args.romInfo == False and args.extract == False and args.convert == False)):
    print("Rom: " + str(args.Input))
    if (header.getMapper() == "FDS"):
        #print the crc32 of the bios in TNES file
        print("FDS Bios crc32: " + header.getFDSBioscrc32(file))
        print("Disk count: " + header.getDiskCount())
        print("Sides per disk: " + header.getSidePerDiskCount() + "\n")
    else:
        #print the mapper designation
        print("Mapper: " + header.getMapper())

        #print the size of Prg rom
        if (header.getPRGSize() == 0):
            print(header.getPRGSize())
        else:
            print("PRG size: " + str(header.getPRGSize()))

        #print CRC32 of PRG rom
        if (header.getPRGSize() != "No PRG rom"):
            PRGcrc32 = hex(zlib.crc32(extracter.extPRGRom(int(header.getPRGSize()))))[2:]
            print("PRG rom crc32: " + str(PRGcrc32))

        #print the size of CHR rom
        if (header.getCHRSize() == 0):
            print(header.getCHRSize())
        else:
            print("CHR size: " + str(header.getCHRSize()))

        #print CRC32 of CHR rom
        if (header.getCHRSize() != "No CHR rom"):
            CHRcrc32 = hex(zlib.crc32(extracter.extCHRRom(int(header.getPRGSize()), int(header.getCHRSize()))))[2:]
            print("CHR rom crc32: " + str(CHRcrc32))
        #print if game uses WRAM
        print("Uses WRAM: " + header.hasWRAM())

        #print Mirroing type
        print("Mirroring: " + header.getMirroring())

        #print if game uses battery
        print("Has battery: " + header.hasBattery() + '\n')

### Used for the extract argument ###
if (args.extract == True):
    if (header.getMapper() == "FDS"):
        extracter.dumpFDSBios(file, header.getFDSBioscrc32(file))
        extracter.extQD(file)
    else:

        prgSize = int(header.getPRGSize())
        extracter.saveToFile(".prg", extracter.extPRGRom(prgSize))
        

        if (header.getCHRSize() == "No CHR rom"):
            exit()
        else:
            extracter.saveToFile(".chr", extracter.extCHRRom(prgSize, int(header.getCHRSize())))

### Used for converting TNES to INES ###
if (args.convert == True):
    if (header.getMapper() == "FDS"):
        exit()
    else:
        conv = open(args.Input[:-3] + "nes", "wb")
        conv.write(bytes(convert.retINESMagic().encode("utf-8")))
        conv.seek(len(convert.retINESMagic()))
        #prg size
        conv.write(convert.retSizeOfRomMultipleKB(header.getPRGSize(), "prg"))
        #chr size
        conv.write(convert.retSizeOfRomMultipleKB(header.getCHRSize(), "chr"))

        #flag 6 - mapper, mirroring, battery
        flag6 = [0, 0, 0, 0]

        #handle the mappers
        mapperList = {
            1: "0000",#NROM
            2: "0001",#SxROM
            3: "1001",#PNROM
            4: "0100",#TxROM
            5: "1010",#FxROM
            6: "0101",#ExROM
            7: "0010",#UxROM
            8: "0011",#CNROM
            9: "0111"}#AxROM

        a = int(header.getMapper(True) + 1)
        lowerNyb = mapperList[a]
        
        #handle if the rom uses a battery backed save
        if (header.hasBattery() == "Yes"):
            flag6[2] = 1
        else:
            flag6[2] = 0
        
        #handle the mirroring
        if (header.getMirroring() == "Mapper Controlled" or header.getMirroring() == "Horizontal"):
            flag6[3] = 0
        elif (header.getMirroring() == "Vertical"):
            flag6[3] = 1

        #conv list to string
        flag6String = ''.join(str(e) for e in flag6)

        full = int(lowerNyb + flag6String, 2).to_bytes(1, byteorder="big")

        conv.write(full)
        conv.write(bytes(9))
        conv.write(extracter.extPRGRom(int(header.getPRGSize())))
        if (header.getCHRSize() != "No CHR rom"):
            conv.write(extracter.extCHRRom(int(header.getPRGSize()), int(header.getCHRSize())))
        
        conv.close()
