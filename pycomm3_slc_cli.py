
'''
The pycomm3_slc_cli application is intended to encaspulate all of the pycomm3 
commands into a single directly executable program.  Using pyinstaller,
pycomm3_slc_cli can be packaged into an .exe file that can be run on any Windows
computer without the need for installing Python.  This can be particularly
handy for systems where an end-user does not have the Rockwell software, but
needs to update a value, set the time on the controller or read or write
settings from or to the target PLC.

Execution of the application will take the form of a single command or a shell
console application allowing multiple commands to be executed.

Single command syntax:
pycomm3_slc_cli 192.168.1.10 Read N9:0
n9:0, 21809, N, None

Console app example:
pycomm3_slc_cli 192.168.1.10
> Read N9:0
n9:0, 21809, N, None
> quit

- or -

pycomm3_slc_cli
> Read CurrentScreen
ERROR - No IPAdress specified.  Use IPAddress command.
> IPAddress 192.168.1.10
> Read N9:0
n9:0, 21809, N, None
> quit

'''

import sys
import datetime
import time

from pycomm3 import SLCDriver
from pathlib import Path
version = "0.1.0"
comm = None
output_format = "raw"
output_formats = ["raw", "readable", "minimal"]
show_timing = False

#region HELPER FUNCTIONS
def getTagValues(tags):
    outData = []
    for tag in tags:
        if len(tag) > 0:
            try:
                result = comm.read(tag)
            except Exception as error:
                print("Error reading: " + tag + " - " + str(error))
                tag_value = tag + "=!ERROR!"
                outData += [tag + "=!ERROR!"]
                continue
            outData += [tag + "=" + str(result.value)]
    return outData

def convertToWordBit(tag):
    if ((not ":" in tag) and ("/" in tag)):
        file = tag.split("/")[0]
        bitPos = int(tag.split("/")[1])
        word = int(bitPos/16)
        bit = bitPos % 16
        converted_tag = file + ":" + str(word) + "/" + bit
    else:
        converted_tag = tag
    return converted_tag

#endregion HELPER FUNCTIONS


#region CONSOLE COMMAND DEFINITIONS
def ipAddress(args):
    #comm.close()
    global comm
    comm = SLCDriver(args)
    comm.open()

def getPLCTime(args):
    if (comm == None):
        print("ERROR - No IPAddress specified.  Use IPAddress command.")
        return
    if (output_format == "raw"):
        print(comm.read('S:37'))
        print(comm.read('S:38'))
        print(comm.read('S:39'))
        print(comm.read('S:40'))
        print(comm.read('S:41'))
        print(comm.read('S:42'))
    elif (output_format == "readable"):
        yr = comm.read('S:37')[1]
        mo = comm.read('S:38')[1]
        dy = comm.read('S:39')[1]
        hh = comm.read('S:40')[1]
        mm = comm.read('S:41')[1]
        ss = comm.read('S:42')[1]
        print('{}/{}/{} {}:{:02d}:{:02d}'.format(mo, dy, yr, hh, mm, ss))

def setPLCTime(args):
    if (comm == None):
        print("ERROR - No IPAddress specified.  Use IPAddress command.")
        return
    current_time = datetime.datetime.now()
    yr = current_time.year
    mo = current_time.month
    dy = current_time.day
    hh = current_time.hour
    mm = current_time.minute
    ss = current_time.second
    comm.write(('S:37', yr))
    comm.write(('S:38', mo))
    comm.write(('S:39', dy))
    comm.write(('S:40', hh))
    comm.write(('S:41', mm))
    comm.write(('S:42', ss))
    print('PLC time set to {}/{}/{} {}:{:02d}:{:02d}'.format(mo, dy, yr, hh, mm, ss))

def read(args):
    if (comm == None):
        print("ERROR - No IPAddress specified.  Use IPAddress command.")
        return
    start_time = time.time()
    ret = comm.read(args)
    exec_time = time.time() - start_time
    if (output_format == "raw"):
        print(ret)
    elif (output_format == "readable"):
        print(ret.value)
    if (show_timing):
        print("Executed in {0:7.3f} seconds.".format(exec_time))
    return

def readTagFile(args):
    if (comm == None):
        print("ERROR - No IPAddress specified.  Use IPAddress command.")
        return
    words = args.split()
    filename = words[0]
    outFile = ""
    tags = []
    if len(words) > 1:
        outFile = words[1]
    try:
        tags = Path(filename).read_text().split("\n")
    except Exception as error:
        print("ERROR - Error opening the file {0}. {1}".format(filename, str(error)))
        return
    start_time = time.time()
    outData = getTagValues(tags)
    exec_time = time.time() - start_time
    if len(outFile) > 0:
        Path(outFile).write_text("\n".join(outData))
    else:
        print("\n".join(outData))
    if (show_timing):
        print("Executed in {0:7.3f} seconds.".format(exec_time))
    return

def optimizeTagFile(args):
    # This function returns or writes an optimized tag list based on the supplied tag list file.
    words = args.split()
    filename = words[0]
    outFile = ""
    tags = []
    if len(words) > 1:
        outFile = words[1]
    try:
        tags = Path(filename).read_text().split("\n")
    except Exception as error:
        print("ERROR - Error opening the file {0}. {1}".format(filename, str(error)))
        return
    start_time = time.time()
    # Sort the file alphabetically.
    tags.sort()
    outData = []
    # Convert all bit tag formats to word/bit format.
    for tag in tags:
        outData.append(convertToWordBit(tag))
    # Group tags from like files.
    files = []
    for tag in outData:
        file = tag.split(":")[0]
        address = tag.split("/")[0]
        word = int(address.split(":")[1])
        if not file in files[file]:
            files.append([file, word, word]]"file": file, "start_word": word, "end_word": word})
        else:
            index = 


    exec_time = time.time() - start_time
    if len(outFile) > 0:
        Path(outFile).write_text("\n".join(outData))
    else:
        print("\n".join(outData))
    if (show_timing):
        print("Executed in {0:7.3f} seconds.".format(exec_time))

    return

def write(args):
    if (comm == None):
        print("ERROR - No IPAddress specified.  Use IPAddress command.")
        return
    words = args.split()
    start_time = time.time()
    ret = comm.write((words[0], words[1]))
    exec_time = time.time() - start_time
    print(ret)
    if (show_timing):
        print("Executed in {0:7.3f} seconds.".format(exec_time))
    return

def getHelp(args):
    print('''
    Commands: (Not case sensitive.)
        Help                        - Displays this list of commands.
        IPAddress <ip address>      - Sets the IP address for the target PLC.
        Quit                        - Leave console application.
        GetPLCTime                  - Returns the PLC time.
        SetPLCTime                  - Sets the PLC time to the current time.
        Read <tag>                  - Returns the specified tag's value from the target PLC.
        Write <tag> <value>         - Sets the specified tag's value in the target PLC.
        Output (Raw | Readable)     - Sets the output format.  Raw is the default.
        ShowTiming (On | Off)       - Turns on or off the time to execute feedback.
        ReadTagFile <filename> [<outfile>]
                                    - Returns the values of the tags from the file.
        OptimizeTagFile <filename> [<outfile>]
                                    - Returns an optimized tag list from the source file.
    ''')
    return

def output(args):
    global output_format
    if (args in output_formats):
        output_format = args
        print("Output format set to {}".format(args))
    else:
        print("Invalid output format")
    return

def showTiming(args):
    global show_timing
    if (args in ["on", "off"]):
        show_timing = args == "on"
        print("ShowTiming set to " + args + ".")
    else:
        print("Invalid ShowTiming argument.  Valid arguments are 'on' or 'off'.")
    return

#endregion CONSOLE COMMAND DEFINITIONS

#region COMMAND LOOP
def parseCommand(command):
    words = command.casefold().split()
    if (len(words) > 0):
        if (words[0] == "help"):
            getHelp(command)
        elif (words[0] == "ipaddress"):
            ipAddress(words[1])
        elif (words[0] == "getplctime"):
            getPLCTime(getAdditionalArgs(command))
        elif (words[0] == "setplctime"):
            setPLCTime(getAdditionalArgs(command))
        elif (words[0] == "read"):
            read(getAdditionalArgs(command))
        elif (words[0] == "readtagfile"):
            readTagFile(getAdditionalArgs(command))
        elif (words[0] == "optimizetagfile"):
            optimizeTagFile(getAdditionalArgs(command))
        elif (words[0] == "write"):
            write(getAdditionalArgs(command))
        elif (words[0] == "output"):
            output(getAdditionalArgs(command))
        elif (words[0] == "showtiming"):
            showTiming(getAdditionalArgs(command))
        else:
            print("ERROR - Unrecognized command.  Enter Help for a list of commands.")
    return

def commandLoop():
    command = input("pycomm3_slc_cli> ")
    while (command.casefold() != "quit"):
        parseCommand(command)
        command = input("pycomm3_slc_cli> ")
    return

#endregion COMMAND LOOP

#region HELPER FUNCTIONS
def isIPAddress(value):
    return len(value.split(".")) == 4

def getAdditionalArgs(command):
    words = command.split()
    if (len(words) > 1):
        return " ".join(words[1:])
    else:
        return ""

#endregion HELPER FUNCTIONS

#region MAIN
def main():
    global comm
    arguments = sys.argv
    if (len(arguments) > 1):
        if (isIPAddress(arguments[1])):
            ipAddress(arguments[1])
            if (len(arguments) > 2):
                parseCommand(" ".join(arguments[2:]))
            else:
                commandLoop()
    else:
        commandLoop()
    comm.close()
    return

#endregion MAIN

main()
