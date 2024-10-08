
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
version = "0.2.1"
comm = None
output_format = "raw"
output_formats = ["raw", "readable", "minimal"]
show_timing = False

# CONSTANTS
NOTFOUND = -1


#region HELPER FUNCTIONS
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getNumber(s):
    assert isNumber(s), "Expected a number, got {0}".format(s)
    if isinstance(s, str):
        if s.isnumeric():
            return int(s)
        else: 
            return float(s)
    else:
        return s
        
#endregion HELPER FUNCTIONS

#region DATA HELPER FUNCTIONS
def getTagValues(tags):
    outData = []
    for tag in tags:
        if len(tag) > 0:
            try:
                result = comm.read(tag)
            except Exception as error:
                #print("Error reading: " + tag + " - " + str(error))
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
        converted_tag = file + ":" + str(word) + "/" + str(bit)
    else:
        converted_tag = tag
    return converted_tag

def foundFile(file, files):
    result = [i for i in range(len(files)) if files[i]["file"] == file]
    if (len(result) > 0):
        return result[0]
    else:
        return -1

def getOptimizedTag(file, maxElements):
    length = file["end_word"] - file["start_word"] + 1
    outData = []
    start_word = file["start_word"]
    loop = length / maxElements
    while loop > 1:
        outData.append(file["file"] + ":" + str(start_word) \
            + "{" + str(maxElements) + "}")
        start_word += maxElements
        loop -= 1
    outData.append(file["file"] + ":" + str(start_word) \
        + "{" + str(file["end_word"] - start_word + 1) + "}")
    return outData

def getTagValuesFromFile(filename):
    tags = []
    try:
        tags = Path(filename).read_text().split("\n")
    except Exception as error:
        print("ERROR - Error opening the file {0}. {1}".format(filename, str(error)))
        return []
    outData = getTagValues(tags)
    return outData

def getTagParts(tag):
    tag = convertToWordBit(tag)
    file = tag.split(":")[0]
    word = NOTFOUND
    bit = NOTFOUND
    if "/" in tag:
        word = int(tag.split(":")[1].split("/")[0])
        bit = int(tag.split("/")[1])
    elif tag.split(":")[1].isnumeric():
        word = int(tag.split(":")[1])
    return {"file": file, "word": word, "bit": bit}

def getDataParts(data):
    file = data.split(":")[0]
    wordString = data.split(":")[1].split("{")[0]
    word = NOTFOUND
    if wordString.isnumeric():
        word = int(wordString)
    dataString = data.split("=")[1]
    dataArray = []
    if "[" in dataString:
        dataStringArray = dataString.split("[")[1].split("]")[0].split(",")
        if file.startswith("F"):
            dataArray = [float(i) for i in dataStringArray]
        else:
            dataArray = [int(i) for i in dataStringArray]
    elif not isNumber(dataString):
        dataArray = [dataString]
    else:
        dataArray = [int(dataString)]
    length = len(dataArray)
    end_word = word + length - 1
    return {"file": file, "start_word": word, "length": length, 
            "end_word": end_word ,"data": dataArray}

def getTagValueFromData(tag, tagData):
    tagParts = getTagParts(tag)
    for data in tagData:
        dataParts = getDataParts(data)
        if tagParts["file"] == dataParts["file"]:
            if tagParts["word"] >= dataParts["start_word"] and tagParts["word"] <= dataParts["end_word"]:
                wordPos = tagParts["word"] - dataParts["start_word"]
                if dataParts["data"][0] == "!ERROR!":
                    return "!ERROR!"
                wordData = getNumber(dataParts["data"][wordPos])
                if "/" in tag and tagParts["bit"] != NOTFOUND:
                    return (wordData & 2**tagParts["bit"]) == 2**tagParts["bit"]
                else:
                    return wordData                    
    return "NONE"

#endregion DATA HELPER FUNCTIONS


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
    start_time = time.time()
    outData = getTagValuesFromFile(filename)
    if len(outData) > 0:
        outFile = ""
        if len(words) > 1:
            outFile = words[1]
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
        if len(tag) > 0:
            file = tag.split(":")[0]
            address = tag.split("/")[0]
            field = address.split(":")[1]
            if field.isnumeric():
                word = int(field)
                foundIndex = foundFile(file, files)
                if foundIndex == NOTFOUND:
                    files.append({"file": file, "start_word": word, "end_word": word})
                else:
                    if files[foundIndex]["start_word"] > word:
                        files[foundIndex]["start_word"] = word
                    if files[foundIndex]["end_word"] < word:
                        files[foundIndex]["end_word"] = word
            else:
                files.append({"file": file, "address": field})
    # Create new tag list from file grouped tags.
    outData = []
    for file in files:
        if "start_word" in file.keys():
            if file["file"].startswith("F"):
                outData += getOptimizedTag(file, 60)     
            elif file["file"].startswith("N") or file["file"].startswith("B"):
                outData += getOptimizedTag(file, 120)     
            else:
                outData.append(file["file"] + ":" + str(file["start_word"]) \
                    + "{" + str(file["end_word"] - file["start_word"] + 1) + "}")
        else:
            outData.append(file["file"] + ":" + file["address"])
    exec_time = time.time() - start_time
    if len(outFile) > 0:
        Path(outFile).write_text("\n".join(outData))
    else:
        print("\n".join(outData))
    if (show_timing):
        print("Executed in {0:7.3f} seconds.".format(exec_time))
    return


def readOptimizedTagFile(args):
    if (comm == None):
        print("ERROR - No IPAddress specified.  Use IPAddress command.")
        return
    words = args.split()
    if len(words) < 2:
        print("ERROR - Invalid number of arguments.  See help for more info.")
        return
    tagfilename = words[0]
    opttagfilename = words[1]
    outFile = ""
    if len(words) > 2:
        outFile = words[2]
    start_time = time.time()
    tagData = getTagValuesFromFile(opttagfilename)
    if len(tagData) > 0:
        # Open the tagfile, loop through the tags and find the value for each in the tagData.
        try:
            tags = Path(tagfilename).read_text().split("\n")
        except Exception as error:
            print("ERROR - Error opening the file {0}. {1}".format(tagfilename, str(error)))
            return
        outData = []
        for tag in tags:
            if len(tag) > 0:
                tagValue = str(getTagValueFromData(tag, tagData))
                outData.append(tag + "=" + tagValue)
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
          
    Multi-Tag Commands: (Filenames are case sensitive.)
        ReadTagFile <filename> [<outfile>]
            - Returns the values of the tags from the file.
        OptimizeTagFile <filename> [<outfile>]
            - Returns an optimized tag list from the source file.
        ReadOptimizedTagFile <tagfilename> <optimizedtagfilename> [<outfile>]
            - Returns the values of the tags from the file using the optimized tag list.
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
        elif (words[0] == "readoptimizedtagfile"):
            readOptimizedTagFile(getAdditionalArgs(command))
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
                comm.close()
            else:
                commandLoop()
                comm.close()
        else:
            parseCommand(" ".join(arguments[1:]))
    else:
        commandLoop()
        comm.close()
    return

#endregion MAIN

main()
