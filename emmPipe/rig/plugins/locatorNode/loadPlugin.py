import os
import sys
import telnetlib

port = 20240

if len(sys.argv) > 1:
    port = sys.argv[1]

nodeName = os.getcwd().split("\\")[-1]

try:
    tn = telnetlib.Telnet("localhost", port)
    tn.write('catchQuiet(`loadPlugin "{}"`);'.format(nodeName).encode())
    tn.close()

    print("LOAD SUCCESS")
except:
    print("LOAD FAIL")
