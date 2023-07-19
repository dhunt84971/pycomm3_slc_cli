# pycomm3_slc_cli

The pycomm3_slc_cli application is intended to encaspulate many of the pycomm3 commands, using the SLCDriver, into a single directly executable program.  Using pyinstaller, pycomm3_slc_cli is packaged into an .exe file that can be run on any Windows computer without the need for installing Python.  This can be particularly
handy for systems where an end-user does not have the Rockwell software, but needs to update a value, set the time on the controller or read or write settings from or to the target PLC.

Warning!  PLCs control industrial equipment and writing values to a PLC that is actively operating equipment should be done with great care and is at your own risk.

Execution of the application will take the form of a single command or a shell console application allowing multiple commands to be executed.

## Examples of Usage
Single command syntax example:
```
pycomm3_slc_cli 192.168.1.10 Read N9:0
n9:0, 21229, N, None
```

Console app example:
```
pycomm3_slc_cli 192.168.1.10
pycomm3_slc_cli> Read N9:1
n9:1, 314, N, None
pycomm3_slc_cli> quit
```

OR
```
pycomm3_slc_cli
pycomm3_slc_cli> Read N9:2
ERROR - No IPAddress specified.  Use IPAddress command.
pycomm3_slc_cli> IPAddress 192.168.1.10
pycomm3_slc_cli> Read N9:2
n9:2, 12, N, None
pycomm3_slc_cli> quit
```

Read an array:
```
pycomm3_slc_cli 192.168.1.10 Read N9:0{5}
n9:0, [1, 2, 3, 4, 5], N, None
```

## Commands
The following commands are not case-sesnitive.
    - Help                        - Displays this list of commands.
    - IPAddress <ip address>      - Sets the IP address for the target PLC.
    - Quit                        - Leave console application.
    - GetPLCTime                  - Returns the PLC time.
    - SetPLCTime                  - Sets the PLC time to the current time.
    - Read <tag>                  - Returns the specified tag's value from the target PLC.
    - Write <tag> <value>         - Sets the specified tag's value in the target PLC.
    - Output (Raw | Readable)     - Sets the output format.  Raw is the default.
    - ShowTiming (On | Off)       - Turns on or off the time to execute feedback.
          
### Multi-Tag Commands:
Filenames are case sensitive.
    - ReadTagFile <filename> [<outfile>]
        - Returns the values of the tags from the file.
    - OptimizeTagFile <filename> [<outfile>]
        - Returns an optimized tag list from the source file.
    - ReadOptimizedTagFile <tagfilename> <optimizedtagfilename> [<outfile>]
        - Returns the values of the tags from the tagfile using the optimizedtagfile to retrieve the values.

## The pycomm3 Project
This application is a command line wrapper to ease the use of the many functions of the pycomm3 library.  The pyinstaller program is used to create an executable package on Windows that does not require the installation of Python.

For more information and documentation:
https://github.com/ottowayi/pycomm3

**Special thanks to ruscito, ottowayi and all the contributors that make pycomm3 possible.**

## Development Environment
In order to build the executable using pyinstaller, first clone this repository and then install both pylogix and pyinstaller using pip.

```
git clone https://github.com/dhunt84971/pycomm3_slc_cli.git
cd pycomm3_slc_cli
pip install pycomm3
pip install pyinstaller
```

### Building the Executable
In order to build the executable for the Windows platform it is necessary to run pyinstaller on a Windows computer.  Keep in mind that Python 3.9+ cannot run on Windows 7.  For this reason it is recommended that a Windows 7 system with Python installed be used to create the executable in order to ensure compatability with Windows 7 and newer versions of Windows.
 
```
pyinstaller -F pycomm3_slc_cli.py
```

## License

This project is licensed under the MIT License.
