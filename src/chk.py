class CHK:
    def __init__(self):
        self.sections = {}

    def loadchk(self, b: bytes):
        self.sections = {}

        if len(b) < 0:
            raise ValueError("Error caused while load chk.")

        index = 0
        while index < len(b):
            sectionname = str(b[index : index + 4], "utf-8")
            sectionlength = int.from_bytes(b[index + 4 : index + 8], "little")

            section = b[index + 8 : index + 8 + sectionlength]
            index += sectionlength + 8

            self.sections[sectionname] = section

        return True
