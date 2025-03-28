import re

class AccdbParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.page_size = 4096  # default ACE page size
        self.pages = []
        self.binary = b''

    def read_file(self):
        with open(self.filepath, 'rb') as f:
            self.binary = f.read()

    def split_pages(self):
        self.pages = [
            self.binary[i:i+self.page_size]
            for i in range(0, len(self.binary), self.page_size)
        ]

    def find_text_strings(self, min_length=4):
        """Extract all printable ASCII strings from the binary."""
        pattern = re.compile(rb'[\x20-\x7E]{' + str(min_length).encode() + rb',}')
        return [match.decode('ascii', errors='ignore') for match in pattern.findall(self.binary)]

    def inspect_header(self):
        header = self.binary[:256]
        magic = header[4:16].decode('ascii', errors='ignore')
        return {
            "magic_header": magic,
            "file_size": len(self.binary),
            "page_count": len(self.pages),
        }

    def parse(self):
        self.read_file()
        self.split_pages()
        return {
            "header": self.inspect_header(),
            "strings": self.find_text_strings()
        }
