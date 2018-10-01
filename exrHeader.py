
import os
import sys
from struct import *

MAGIC = 0x01312f76
COMPRESSION = ['NO','RLE','ZIPS','ZIP','PIZ','PXR24','B44','B44A']
LINEORDER = ['INCRESING Y','DECREASING Y','RANDOM Y']
PIXELTYPE = ['UINT','HALF','FLOAT']

class ExrHeader:
    def __init__(self):
        self.header = {}

    def readInt32(self, fd):
        l = fd.read(4)
        return unpack('I', l)[0]

    def readString(self,fd):
        byts = []
        d = fd.read(1)
        while d != '\0' and ord(d) != 0x00:
            byts.append(d)
            d = fd.read(1)
        if len(byts) == 0:
            return ""
        byts.append(b'\0')
        bytes_as_str = b''.join(byts).decode("unicode_escape")
        return bytes_as_str[:-1]

    def convData(self,name, data, size):
        result = ""
        if name == 'int':
            result = unpack('i', data)[0]
        elif name == 'float':
            result = unpack('f', data)[0]
        elif name == 'double':
            result = unpack('d', data)[0]
        elif name == 'string':
            result = "%s" % data
        elif name == 'box2i':
            result = unpack('4i', data)
        elif name == 'v2i':
            result = unpack('2i', data)
        elif name == 'v2f':
            result = unpack('2f', data)
        elif name == 'v3i':
            result = unpack('3i', data)
        elif name == 'v3f':
            result = unpack('3f', data)
        elif name == 'compression':
            result = COMPRESSION[ unpack('B', data)[0] ]
        elif name == 'chlist':
            chld = {}
            cid = 0
            while cid < (size-1):
                str = []
                while cid < size and data[cid] != '\0' and data[cid] != 0: # 0 value is equal to \0
                    str.append(bytes([ data[cid] ])) # convert back to byte
                    cid = cid + 1
                str.append(b'\0')
                bytes_as_str = b''.join(str).decode("unicode_escape")
                idx = bytes_as_str[:-1]
                cid = cid + 1
                ch = unpack('iiii', data[cid:cid+16])
                cid = cid + 16
                chld[idx] = {'pixeltype':PIXELTYPE[ch[0]], 'sampling x':ch[2], 'sampling y':ch[3] }
            result = chld
        elif name == 'lineOrder':
            result = LINEORDER[ unpack('B', data)[0] ]
        else:
            result = unpack('%dB' % size, data)

        return result

    def read(self,fd):
        self.header = {}
        id = self.readInt32(fd)
        ver = self.readInt32(fd)
        if id != MAGIC:
            return False

        cn = self.readString(fd)
        while len(cn):
            name = self.readString(fd)
            size = self.readInt32(fd)
            data = fd.read(size)

            data = self.convData(name, data, size)

            self.header[ cn ] = { name:data }
            cn = self.readString(fd)

        return True

    def getAttr(self,name):
        if name in self.header:
            return self.header[name]
        return ""

    def get(self):
        return self.header

    def __getattr__(self, name):
        return self.getAttr(name)

    def attributes(self):
        return self.header.keys()

if __name__ == "__main__":
    fd = open(sys.argv[1], 'rb')
    exr = ExrHeader()
    if exr.read(fd):
        for a in exr.attributes():
            print(a,":",exr.getAttr(a))
    else:
        print( "unknown file or error" )
    
    fd.close()

