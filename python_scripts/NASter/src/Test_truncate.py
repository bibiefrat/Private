import sys
from FileHandler import FileHandler
from Globals import truncate_cfg

if __name__ == '__main__':

    src = FileHandler(sys.argv[1],'rb+')
    size_to_add_in_bytes = (int(truncate_cfg["kb_to_add"])*1024)
    src.check_truncate(src.size + size_to_add_in_bytes)
