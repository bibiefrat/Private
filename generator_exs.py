import re
 
parsers = {
    'itf': re.compile(r'(?P<res>\w+): flags'),
    'inet': re.compile(r'inet (?P<res>\d+\.\d+\.\d+\.\d+)'),
    'status': re.compile('status: (?P<res>\w+)'),
    'ether': re.compile('ether (?P<res>[a-f0-9:]+)'),
}
 
def set_thing_in_dictionary(dict, line, thing):
    if parsers[thing].search(line):
        dict[thing] = parsers[thing].search(line).group('res')
 
 
class Parser:
    def __init__(self):
        self.blocks = []
        self.current_block = None
        self.new_block = re.compile('^\w')
 
    def finalize(self):
        if self.current_block is not None:
            self.blocks.append(self.current_block)
 
        self.current_block = {}
 
    def read_blocks(self, f):
        for line in f:
            if self.new_block.search(line):
                self.finalize()
 
            yield self.current_block, line
 
 
parser = Parser()
 
with open('input.txt') as f:
    for current_block, line in parser.read_blocks(f):
        # current_block is a dictionary
        # and this code fills it
        for thing in parsers.keys():
            set_thing_in_dictionary(current_block, line, thing)
 
 
# [
#     { 'itf': 'lo0', 'inet': '127.0.0.1' },
#     { 'itf': 'en0', 'inet': '127.0.0.1', 'status': 'active' },
# ]
parser.finalize()
print(parser.blocks)