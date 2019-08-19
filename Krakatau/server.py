import struct
import socket

class Server(object):
    def __init__(self, port):
        self._remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._remote.connect(("127.0.0.1", port))

    def _recvall(self, want):
        response = bytearray()
        while len(response) < want:
            response.extend(self._remote.recv(want - len(response)))

        return response

    def _writeBytes(self, data):
        self._remote.sendall(struct.pack('>I', len(data)))
        self._remote.sendall(data)

    def _readBytes(self):
        (resplen,) = struct.unpack('>I', self._recvall(4))
        return self._recvall(resplen)

    def _writeCommand(self, cmd):
        self._remote.sendall(struct.pack('>B', cmd))

    def loadTargets(self):
        self._writeCommand(0x01)

        targets = []

        (tgtLen,) = struct.unpack('>I', self._recvall(4))
        for i in range(tgtLen):
            targets.append(str(self._readBytes()))

        return targets

    def searchForFile(self, name):
        self._writeCommand(0x02)

        self._writeBytes(name)

        (found,) = struct.unpack('>?', self._recvall(1))
        if found:
            return self._readBytes()

    def write(self, cname, data):
        self._writeCommand(0x03)

        self._writeBytes(cname)
        self._writeBytes(data)

    def __enter__(self): return self

    def __exit__(self, *args):
        self._writeCommand(0x04)
