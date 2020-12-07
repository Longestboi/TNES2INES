# TNES2INES
### Description
A tool to convert the proprietary TNES NES rom format (used in the 3ds VC NES releases and more) to INES 1.0. It can also extract the prg and chr sections from TNES roms and the FDS bios and .qd's from .tds files

**This script does _not_ convert .qd's to .fds files**. If you need to convert from qd to fds, use [qd2fds.py](https://gist.github.com/einstein95/6545066905680466cdf200c4cc8ca4f0) from [@einstein95](https://github.com/einstein95)

##### An aside:
I'm still a beginner with python. I've definitely used the wrong coding conventions in this script, but hey... it works :)<br />
This is also my first attempt to use git CLI; It's not relevant to the project in any way, but I wanted to write this somewhere. 

## Usage
```
usage: tnes2ines.py [-h] [-i | -x | -c] Input

Convert TNES roms to INES roms

positional arguments:
  Input          TNES Rom

optional arguments:
  -h, --help     show this help message and exit
  -i, --romInfo  Show TNES rom info
  -x, --extract  Extract PRG and CHR roms (or FDS bios and FDS .qd, if input
                 is a FDS game) from TNES input
  -c, --convert  Convert TNES rom to INES
```
## References
[INES Format](https://wiki.nesdev.com/w/index.php/INES) - Nesdev<br />
[TNES Format](https://wiki.nesdev.com/w/index.php/TNES) - Nesdev
