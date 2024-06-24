# MPQ
# Almost codes are from eudplib.

from ctypes import (
    WinDLL,
    c_int,
    c_wchar_p,
    c_void_p,
    c_char_p,
    byref,
    get_last_error,
    create_string_buffer,
    POINTER,
    Structure,
)
import logging
import os

logger = logging.getLogger("storm")


class CreateInfo(Structure):
    _fields_ = [  # noqa: RUF012
        ("cbSize", c_int),
        ("dwMpqVersion", c_int),
        ("pvUserData", c_void_p),
        ("cbUserData", c_int),
        ("dwStreamFlags", c_int),
        ("dwFileFlags1", c_int),
        ("dwFileFlags2", c_int),
        ("dwFileFlags3", c_int),
        ("dwAttrFlags", c_int),
        ("dwSectorSize", c_int),
        ("dwRawChunkSize", c_int),
        ("dwMaxFileCount", c_int),
    ]


class StormLib:
    """
    stormlib.dll wrapper class.
    """

    def __init__(self):
        self.mpqh = None
        self.stormlib = WinDLL("./src/lib/StormLib64.dll", use_last_error=True)

        self.stormlib.SFileOpenArchive.restype = c_int
        self.stormlib.SFileCloseArchive.restype = c_int
        self.stormlib.SFileOpenFileEx.restype = c_int
        self.stormlib.SFileGetFileSize.restype = c_int
        self.stormlib.SFileReadFile.restype = c_int
        self.stormlib.SFileCloseFile.restype = c_int

        self.stormlib.SFileOpenArchive.argtypes = [
            c_wchar_p,
            c_int,
            c_int,
            c_void_p,
        ]
        self.stormlib.SFileCloseArchive.argtypes = [c_void_p]
        self.stormlib.SFileOpenFileEx.argtypes = [
            c_void_p,
            c_char_p,
            c_int,
            c_void_p,
        ]
        self.stormlib.SFileGetFileSize.argtypes = [c_void_p, c_void_p]
        self.stormlib.SFileReadFile.argtypes = [
            c_void_p,
            c_char_p,
            c_int,
            c_void_p,
            c_int,
        ]
        self.stormlib.SFileCloseFile.argtypes = [c_void_p]

        # for MpqWrite
        self.stormlib.SFileCompactArchive.restype = c_int
        self.stormlib.SFileCreateArchive2.restype = c_int
        self.stormlib.SFileAddFileEx.restype = c_int
        self.stormlib.SFileGetMaxFileCount.restype = c_int
        self.stormlib.SFileSetMaxFileCount.restype = c_int

        self.stormlib.SFileCompactArchive.argtypes = [c_void_p, c_char_p, c_int]
        self.stormlib.SFileCreateArchive2.argtypes = [
            c_wchar_p,
            POINTER(CreateInfo),
            c_void_p,
        ]
        self.stormlib.SFileAddFileEx.argtypes = [
            c_void_p,
            c_wchar_p,
            c_char_p,
            c_int,
            c_int,
            c_int,
        ]
        self.stormlib.SFileGetMaxFileCount.argtypes = [c_void_p]
        self.stormlib.SFileSetMaxFileCount.argtypes = [c_void_p, c_int]

    def SFileOpenArchive(
        self, szMpqName: c_wchar_p, dwPriority: c_int, dwFlags: c_int, phMPQ: c_void_p
    ):
        return self.stormlib.SFileOpenArchive(szMpqName, dwPriority, dwFlags, phMPQ)

    def SFileCloseArchive(self, hMPQ: c_void_p):
        return self.stormlib.SFileCloseArchive(hMPQ)

    def SFileCreateArchive(self, fname): ...

    def SFileOpenFileEx(
        self,
        hMpq: c_void_p,
        szFileName: c_char_p,
        dwSearchScope: c_int,
        phFile: c_void_p,
    ):
        return self.stormlib.SFileOpenFileEx(hMpq, szFileName, dwSearchScope, phFile)

    def SFileGetFileSize(self, hFile: c_void_p, pdwFileSizeHigh: c_void_p):
        return self.stormlib.SFileGetFileSize(hFile, pdwFileSizeHigh)

    def SFileReadFile(
        self,
        hFile: c_void_p,
        lpBuffer: c_char_p,
        dwToRead: c_int,
        pdwRead: c_void_p,
        lpOverlapped: c_int,
    ):
        return self.stormlib.SFileReadFile(
            hFile, lpBuffer, dwToRead, pdwRead, lpOverlapped
        )

    def SFileCloseFile(self, hFile: c_void_p):
        return self.stormlib.SFileCloseFile(hFile)


class MPQ:
    def __init__(self):
        self.stormlib = StormLib()

    def Open(self, fname):
        logger.info(f"Open file: {fname}")
        h = c_void_p()
        ret = self.stormlib.SFileOpenArchive(fname, 0, 0, byref(h))

        if not ret:
            logger.error(f"Error caused while open MPQ file. Code: ${
                         get_last_error()}")
            self.mpqh = None
            return False

        self.mpqh = h
        return True

    def Close(self, fname):
        if self.mpqh is None:
            logger.error("Closing MPQ file while never opened MPQ.")
            return

        self.stormlib.SFileCloseArchive(self.mpqh)
        self.mpqh = None

    def Get(self, fname):
        fileh = c_void_p()
        n = fname.encode("utf-8")
        ret = self.stormlib.SFileOpenFileEx(self.mpqh, n, 0, byref(fileh))

        if not ret:
            logger.error(
                f"Error caused while reading file {n}, Code: {get_last_error()}"
            )
            return False

        fileSize = self.stormlib.SFileGetFileSize(fileh, 0)

        if not fileSize or fileSize <= 0:
            logger.error(
                f"Error caused while reading file {n}, file size lower than expected."
            )
            return False

        fileData = create_string_buffer(fileSize)
        pfread = c_int()
        self.stormlib.SFileReadFile(fileh, fileData, fileSize, byref(pfread), 0)
        self.stormlib.SFileCloseFile(fileh)

        if pfread.value == fileSize:
            return fileData.raw
        else:
            return None
