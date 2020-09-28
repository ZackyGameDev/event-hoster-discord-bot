import time 
import colorama
from termcolor import cprint

def console_log(to_log:str, color=None, on_color=None) -> None:
    for line in to_log.split('\n'):
        to_print = f'[{time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())}] {line}'
        cprint(to_print, color, on_color)
                        
def read_file(filename):
    f = open(filename)
    content = f.read()
    f.close()
    return content