#!C:\Python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'rdfextras==0.2','console_scripts','rdfpipe'
__requires__ = 'rdfextras==0.2'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('rdfextras==0.2', 'console_scripts', 'rdfpipe')()
    )
