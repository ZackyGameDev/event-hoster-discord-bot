import time 
import colorama
from termcolor import cprint as col_print

def cprint(to_print:str, color=None, on_color=None) -> None:
    '''This is the some to termcolor.cprint(), but prints the string line by Line'''
    for line in to_print.split('\n'):
        col_print(line, color, on_color)

def console_log(to_log:str, color=None, on_color=None) -> None:
    '''Same as data.custom.functions.cprint(), but puts a timestamp before printing the line, and also puts the line into logs.txt'''
    logs = open("logs.txt", "a")
    for line in to_log.split('\n'):
        to_print = f'[{time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())}] {line}'
        col_print(to_print, color, on_color)
        logs.write(to_print+'\n')
    logs.close()
                        
def read_file(filename):
    '''Just reads a file and returns the content in it'''
    f = open(filename)
    content = f.read()
    f.close()
    return content
