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

    def scan_pages_for_strings(self, start=0, end=10):
        results = []
        pattern = re.compile(rb'[\x20-\x7E]{4,40}')
        seen = set()
    
        for page_index in range(start, min(end, len(self.pages))):
            page = self.get_page(page_index)
            matches = pattern.finditer(page)
            for match in matches:
                try:
                    text = match.group().decode('ascii').strip()
                    offset = match.start()
                    if text not in seen and len(text) > 3:
                        seen.add(text)
                        results.append((page_index, offset, text))
                except:
                    continue
    
        self.messages.append(f"Scanned pages {start}–{end}. Found {len(results)} unique text strings.")
        return results

    def search_page_for_keywords(self, page_index, keywords):
        page = self.get_page(page_index)
        if not page:
            return []
    
        pattern = re.compile(rb'[\x20-\x7E]{3,50}')
        matches = pattern.finditer(page)
    
        found = []
    
        for match in matches:
            try:
                text = match.group().decode('ascii', errors='ignore').strip()
                offset = match.start()
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        found.append((offset, text))
            except:
                continue
    
        self.messages.append(f"Keyword scan of page {page_index} found {len(found)} matches.")
        return found

    def parse_table_definition(self, page_index=7):
        page = self.get_page(page_index)
        if not page:
            self.messages.append("Failed to read page for table definition.")
            return []
    
        fields = []
        field_block_start = 1000  # start near where your repeated blocks appeared
        max_scan = 1500           # scan range (adjustable)
    
        self.messages.append("Scanning Page 7 for field records...")
    
        i = field_block_start
        while i < max_scan:
            # Try to read length-prefixed field name
            try:
                name_len = page[i]
                if 1 <= name_len <= 30:
                    raw_name = page[i+1:i+1+name_len]
                    name = raw_name.decode('ascii', errors='ignore').strip()
    
                    # Field type usually comes right after name (adjust offset as needed)
                    field_type = page[i+1+name_len]
                    fields.append({
                        "offset": i,
                        "name": name,
                        "type_code": field_type
                    })
                    i += name_len + 2  # jump to next possible record
                else:
                    i += 1
            except Exception:
                i += 1
    
        self.messages.append(f"Found {len(fields)} field(s) in table definition.")
    
        return fields

    def dump_raw_bytes(self, page_index=7, start=1000, end=1100):
        page = self.get_page(page_index)
        raw_bytes = page[start:end]
        hex_dump = ' '.join(f'{b:02X}' for b in raw_bytes)
        ascii_dump = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in raw_bytes)
        self.messages.append(f"Hex Dump (Page {page_index}, {start}-{end}):")
        self.messages.append(hex_dump)
        self.messages.append(f"ASCII: {ascii_dump}")
    
    def parse(self):
        self.read_file()
        self.split_pages()
        self.dump_raw_bytes(7, 1000, 1100)
        
        return {
            "catalog_preview": self.scan_pages_for_strings(0,10),
            "page_7_keywords": self.search_page_for_keywords(7, ['Table', 'ID', 'Name', 'Field']),
            "table_fields": self.parse_table_definition(7),
            "messages": self.messages
        }
