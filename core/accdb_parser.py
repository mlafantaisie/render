import struct
import re

class AccdbParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.page_size = 4096
        self.binary = b''
        self.pages = []
        self.messages = []  # <-- collect status/info here

    def read_file(self):
        try:
            with open(self.filepath, 'rb') as f:
                self.binary = f.read()
            self.messages.append(f"Loaded file: {self.filepath} ({len(self.binary)} bytes)")
        except Exception as e:
            self.messages.append(f"Error reading file: {e}")

    def split_pages(self):
        self.pages = [
            self.binary[i:i+self.page_size]
            for i in range(0, len(self.binary), self.page_size)
        ]
        self.messages.append(f"Split into {len(self.pages)} pages (page size = {self.page_size} bytes)")

    def get_page(self, index):
        if index < len(self.pages):
            self.messages.append(f"Loaded page {index}")
            return self.pages[index]
        self.messages.append(f"Page {index} not found")
        return None

    def inspect_catalog_page(self):
        page = self.get_page(0)
        if not page:
            return []
    
        self.messages.append("Scanning page 0 for distinct printable ASCII strings...")
    
        pattern = re.compile(rb'[\x20-\x7E]{4,40}')  # printable ASCII range, 4–40 chars
        matches = pattern.finditer(page)
    
        catalog_strings = []
        seen = set()
    
        for match in matches:
            try:
                text = match.group().decode('ascii').strip()
                offset = match.start()
    
                # Optional: filter out exact duplicates or repetitive filler
                if text not in seen and not text.startswith('=') and len(text.strip()) > 3:
                    seen.add(text)
                    catalog_strings.append((offset, text))
            except:
                continue
    
        if catalog_strings:
            self.messages.append(f"Found {len(catalog_strings)} unique text strings on page 0.")
        else:
            self.messages.append("No usable strings found on page 0.")
    
        return catalog_strings


    def parse(self):
        self.read_file()
        self.split_pages()

        return {
            "catalog_preview": self.inspect_catalog_page(),
            "messages": self.messages
        }
