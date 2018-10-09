# NiceHash Mining Timer
NiceHash mining timer is a command line tool for recording individual workers mining times while mining using NiceHash.

## Getting Started
To setup this tool just clone the repo using `git clone https://github.com/ColeFaraday/mining-timer`. Change the mining.cfg `address` variable to the address of your nicehash wallet. You can also change other variables for different configuration options (see configuration section)

To  open the program run main.py with `python3 main.py`. This will enter you into a prompt where you can enter commands. To start a new recording session enter `start`. This will begin recording the times for each worker.

### All commands
Below is a list of all of the availible commands, their options, and their usage

- `start` - Starts recording the times of the workers
    - `-s /path/to/source.json` option - Specifies the source json file which the recording will use as a starting point. This is used to continue after a system crash, etc.
- `resume` - Starts recording using the last generated mining times as a starting point
- `times` - Outputs a list of all of the current times of the workers
- `raw` - Outputs a list of the raw values of each workers continuous mining time directly from the NiceHash API

