import urllib.request
import json
import time
import datetime
import threading
import os
import re
import shlex
import configparser
import sys

# times for miners name:time
times = {}

#all availible commands
commands = {}

# workers dict from nicehash api
workers = None
# time before new time
prevTimes = dict(times)
now = datetime.datetime.now()
# interval to query nicehash api
updateTime = 60
address = None

script_dir = os.path.dirname(__file__)

zero = False

# filenames
start = str(now.strftime("%Y-%m-%d %H-%M"))
timesFile = 'current times - ' + start + '.json'
currFile = 'current.json'

running = False

first = True

subFolder = ''

def loadConfig(): # load variables from cfg
    global address, updateTime
    config = configparser.ConfigParser()
    config.read(os.path.join(script_dir, 'mining.cfg'))
    address = config['DEFAULT']['address']
    updateTime = config['DEFAULT'].getint('updateTime')

def loadFromJson(jsonFile): # load info from previous mining session (json) into dicts
    global times, prevTimes

    jsonFileObject = open(os.path.join(script_dir, jsonFile))
    jsonStr = jsonFileObject.read()
    times = json.loads(jsonStr)
    prevTimes = times.copy()


def saveToDict(n, t):# calculate how much time a worker has been mining and add it to times dict
    global prevTimes, times

    # add to times array if it is not already there
    if (n not in times):
        times[n] = 0
        prevTimes[n] = t

    # if algo changes, add lost time to times dict (usually 1 for some reason, probably nicehash api weird stuff)
    if not (first) and (t < prevTimes[n]):
        times[n] += (updateTime/60)

    # if miner has mined more
    if(t > prevTimes[n]):
        #if miner has mined more than possible i.e. multiple workers issue
        if (t > (prevTimes[n] + updateTime/60 + 1)) and not (first):
            # update prevTimes to be inline with new t value (1 min before t)
            prevTimes[n] = t - 1
        # add the delta mining time to times dict
        times[n] += (t-prevTimes[n])

    prevTimes[n] = t

def saveToJson(writeFile, jsonFile):# save times dict to json
    global subFolder
    try:
        os.mkdir(subFolder)
    except:
        pass
    with open(os.path.join(script_dir, writeFile), 'w') as f:
        json.dump(jsonFile, f)
        f.close()

def getAPI(): # Get information from nicehash API
    global workers
    try:
        with urllib.request.urlopen("https://api.nicehash.com/api?method=stats.provider.workers&addr="+address) as url:
            data = json.loads(url.read().decode())
            workers = (data['result']['workers'])
            url.close()
    except:
        print("Could not request API")

def recordTimes(): # main loop
    global first, times, updateTime, running
    running = True

    while(running):

        getAPI()
        # list of workers done in this iteration
        completedWorkers = []
        try:
            # record all workers times
            for i in range(0, len(workers)):
                wName = workers[i][0]
                wTime = workers[i][2]

                # remove duplicates (from multiple algos, cpu mining)
                if (not (wName in completedWorkers)):
                    completedWorkers.append(wName)
                    saveToDict(wName, wTime)

            saveToJson(timesFile, times)
            saveToJson(currFile, times)

            # wait
            time.sleep(updateTime)
            first = False
        except:
            print("Could not run main loop")

def getRaw():# get raw info as per nicehash
    global workers
    raw = ''
    for i in range(0, len(workers)):
        raw += '\n'
        for j in range(0, len(workers[i])):
            if (j == 0):
                raw += (workers[i][j] + ' - ')
            elif (j==2):
                raw += str(workers[i][j])
    return raw

def parseCommand(c):# command functionality
    split = c.split(' ', 1)
    if (split[0] in commands):
        try:
            commands[split[0]](split[1:][0])
        except:
            try:
                commands[split[0]](None)
            except:
                print("Could not run command")
    else:
        print('Not a command')

def printCmdOutput(o): # print nicely formatted
    print(datetime.datetime.now().strftime("%H-%M") + ' > ', end="")
    print(o)

def cmdTimes(args): # return current times
    printCmdOutput(times)

def cmdUpdateInterval(args):# update interval which api is checked at
    global updateTime
    updateTime = int(args)
    printCmdOutput("Time interval updated")

def cmdGetUpdateInterval(args):# get interval which api is checked at
    printCmdOutput(updateTime)

def cmdExit(args):# quit program
    global running
    running = False
    printCmdOutput('Terminated')

def cmdStart(args): # start recording
    global subFolder, zero

    # split into items seperated by spaces while preserving items within ""
    splitArgs = []
    try:
        if (args != None):
             splitArgs = shlex.split(args)
    except:
        print('Error while applying regex to arguments');

    try:

        # start with (s)ource
        if ('-s' in splitArgs):
            try:
                loadFromJson(splitArgs[splitArgs.index('-s')+1])
                zero = True
                printCmdOutput('Starting with json starting point')
            except:
                printCmdOutput('Error in syntax of "-s" or source file may not exist');

        # no source
        else:
            printCmdOutput('Starting without json starting point')
            zero = True
    except:
        printCmdOutput('An unknown error occured during start command process');

    thread.start()

def cmdRaw(args):# print raw
    printCmdOutput(getRaw())

def cmdClear(args):# clear
    os.system('cls')

    printCmdOutput("Subfolder: /" + subFolder);

def cmdResume(args): # resume last session
    cmdStart(' -s "current.json"')

thread = threading.Thread(target=recordTimes)
thread.daemon = True

loadConfig()


commands = { "times": cmdTimes, "updateinterval": cmdUpdateInterval, "getinterval": cmdGetUpdateInterval, "exit": cmdExit, "start": cmdStart, "raw" : cmdRaw, "clear" : cmdClear, "resume": cmdResume }

try:
    if sys.argv[1] == '-r':
        parseCommand('resume')

except:
    pass
while(True):# input loop
    command = input('>')
    parseCommand(command)
