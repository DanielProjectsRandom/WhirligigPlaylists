#!/usr/bin/python3

from collections import OrderedDict
import os, time, functions, pathlib, glob, sys, winsound, logging

def monitoringStuff():
    rootdir = os.path.dirname(os.path.realpath(__file__))

    pid = os.getpid()
    windowsUsername = os.getlogin()
    pathPID = pathlib.Path(rootdir + "/monitorPID.txt")
    filePID = open(pathPID, "w")
    filePID.write("{}".format(pid))
    filePID.close()

    loggingPath = rootdir + '/monitorLogMonitor.txt'
    loggerMonitor = logging.getLogger(__name__)
    loggerMonitor.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(loggingPath, "a")
    formatter = logging.Formatter('%(asctime)s, %(name)s %(funcName)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    loggerMonitor.addHandler(file_handler)

    tempPath = rootdir + "/temp.txt"
    if os.path.exists(tempPath):
        f = open(tempPath, "r")
        playlistName = f.read().rstrip()
        f.close()
        playlistName = playlistName.replace("_", " ")
    else:
        playlistName = "bestof.plt"

    print("Playlist Name: " + playlistName)
    loggerMonitor.info(f'Using playlist name: {playlistName}')
    checkingInis = True
    folderPathInis = pathlib.Path(f"C:/Users/{windowsUsername}/AppData/Roaming/Whirligig/production/menu")
    folderPathVideoInis = pathlib.Path(f"C:/Users/{windowsUsername}/AppData/Roaming/Whirligig/production/menu/inis")
    folderPathPlaylists = pathlib.Path(f"C:/Users/{windowsUsername}/AppData/Roaming/Whirligig/production/Playlists")
    #scriptStartTime = time.time()

    print("Checking....")
    loggerMonitor.info("Starting monitor loop")
    t = time.localtime()
    current_time = time.strftime("%H-%M-%S", t)
    r = pathlib.Path(rootdir)
    check = r / "checks"
    p = check / "{}.txt".format(str(current_time))
    checkFile = open(p, "w")
    checkFile.write("Starting at" + current_time + "\n")
    checkFile.close()
    counter = 0

    while checkingInis:
        time.sleep(0.5)

        counter = counter + 1
        if counter > 10:
            t = time.localtime()
            current_time = str(time.strftime("%H:%M:%S", t))
            checkFile = open(p, "a")
            checkFile.write(current_time + "\n")
            checkFile.close()
            counter = 0

        checkIni = folderPathInis / "player.ini"
        isNewIni = False
        playerIniModTime = os.path.getmtime(checkIni)
        testTime = time.time()
        timeDifference = testTime - playerIniModTime
        if timeDifference < 0.0:
            timeDifference = 2.0

        if timeDifference < 1.0:
            loggerMonitor.info("Modified")
            rawFile = open(checkIni, "r", encoding="utf8")
            iniInfo = rawFile.readlines()
            iniDict = functions.listToDict(iniInfo)
            rawFile.close()
            loggerMonitor.info("Read player.ini")
            iniName = iniDict["mediafile"] + ".ini"
            videoIniPath = folderPathVideoInis / iniName
            videoIniModTime = os.path.getctime(videoIniPath)
            loggerMonitor.info(f'Got mod time for {iniName}')
            timeDifferenceVideoIni = testTime - videoIniModTime
            if timeDifferenceVideoIni < 1.0:
                isNewIni = True


            if iniDict["Subtitles"] == "on":
                loggerMonitor.info("Trying to add \"{}\" to playlist".format(iniDict["mediafile"]))
                functions.addToPlaylist(folderPathPlaylists, playlistName, iniDict["mediafolder"], iniDict["mediafile"], iniDict["dometype"])
                if isNewIni:
                    loggerMonitor.info("The file does not have its own ini")
                    winsound.Beep(1000, 800)
                else:
                    loggerMonitor.info("The file has its own ini")
                    winsound.Beep(2500, 400)
                    time.sleep(0.2)
                    winsound.Beep(2500, 200)
                functions.changePlayerSetting("Subtitles", "off", "on", str(checkIni))
                loggerMonitor.info("Turned subtitles off in player.ini")
                functions.changePlayerSetting("Subtitles", "off", "on", videoIniPath)
                loggerMonitor.info("Turned subs off for video ini: " + os.path.basename(videoIniPath))

monitoringStuff()


