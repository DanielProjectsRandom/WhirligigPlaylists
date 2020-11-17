#!/usr/bin/python3

import subprocess, os, winsound, pathlib, time, logging, sys

def launcher():
    print("Started launcher")
    rootdir = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))

    loggingPath = os.path.dirname(os.path.realpath(__file__)) + '/monitorLogLauncher.txt'
    loggerLauncher = logging.getLogger(__name__)
    loggerLauncher.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(loggingPath, "a")
    formatter = logging.Formatter('%(asctime)s, %(name)s %(funcName)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    loggerLauncher.addHandler(file_handler)

    count = 0
    path = rootdir / "WhirligigMonitorV2.py"
    tempPath = rootdir / "tempStop.txt"
    tempPlaylistNamePath = rootdir / "temp.txt"
    f = open(tempPath, "r")
    s = f.read().rstrip()
    print("\"{}\"".format(s))
    f.close()
    while s == "Start":
        count = count + 1
        print("Starting count: {}".format(count))
        p = subprocess.Popen([sys.executable, str(path)])
        loggerLauncher.info(f'Starting script from launcher: {count}')
        p.wait()

        #winsound.Beep(2600, 200)
        #winsound.Beep(1200, 300)
        #winsound.Beep(2600, 200)
        #winsound.Beep(1200, 300)
        #winsound.Beep(2600, 300)

        f = open(tempPath, "r")
        s = f.read().rstrip()

        f.close()
        if s == "Start":
            loggerLauncher.error(f'Script crashed after running {count} times')
        else:
            loggerLauncher.info(f'Script closed properly after running {count} times')

    os.remove(str(tempPlaylistNamePath))
launcher()



