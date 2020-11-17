#!/usr/bin/python3

from collections import OrderedDict
import os, pathlib, fileinput, sys

def listToDict(list):
    d = OrderedDict()
    for s in list:
        k, v = s.split("=")
        d[k] = v.rstrip()

    return d

def getIniDict(pathIni):
    fileIni = open(pathIni, "r", encoding="utf8")
    settingsList = fileIni.read().rstrip().split("\n")
    fileIni.close()
    d = listToDict(settingsList)
    return d

def displayDict(d):
    for k, v in d.items():
        print("{} = {}".format(k, v))

def deleteVideoFromPlaylist(playlistPath, deletePath):
    f = open(playlistPath, "r", encoding="utf8")
    paths = f.readlines()
    f.close()
    newPathsList = []
    for path in paths:
        if not path == deletePath:
            newPathsList.append(path)
    f = open(playlistPath, "w", encoding="utf8")
    f.writelines(newPathsList)
    f.close()

def getPlaylistContents(playlistPath):
    f = open(playlistPath, "r", encoding="utf8")
    paths = f.readlines()
    f.close()
    d = []
    for path in paths:
        fileName = os.path.basename(path)
        folder = os.path.dirname(path)
        fileNameBase, fileNameExt = os.path.splitext(fileName)
        d.append({"Path": path, "Base": fileNameBase, "Name": fileName})
    return d

def removePlaylistDuplicates(playlistPath):
    f = open(playlistPath, "r", encoding="utf8")
    lines = f.readlines()
    if len(lines[-1]) < 4:
        del lines[-1]
    f.close()
    d = OrderedDict()
    for l in lines:
        d[l] = ""
    lines = list(d.keys())
    lines.append("\n")
    f = open(playlistPath, "w", encoding="utf8")
    f.writelines(lines)
    f.close()

def sortByFileNameAlphabetically(paths):
    d = {}
    sortedPaths = []
    for path in paths:
        fileName = os.path.basename(path)
        folder = os.path.dirname(path)
        d[fileName] = folder
    filesNames = list(d.keys())
    filesNames.sort()
    for f in filesNames:
        sortedPaths.append(d[f] + "/" + f)
    return sortedPaths

def checkIfSubsOnInIni(pathIni):
    fileIni = open(pathIni, "r", encoding="utf8")
    settingsList = fileIni.read().rstrip().split("\n")
    fileIni.close()
    d = listToDict(settingsList)
    if d["Subtitles"] == "on":
        return True
    else:
        return False

def removeFromList(list, itemToRemove):
    newList = []
    for i in list:
        if not i == itemToRemove:
            newList.append(i)
    return newList


def addToPlaylist(playlistsFolderPath, playlistName, folderPath, fileName, domeType):
    selectedFilePath = folderPath + fileName
    playlistPath = str(playlistsFolderPath) + "/" + playlistName
    if os.path.exists(playlistPath):
        playlistFile = open(playlistPath, "r", encoding="utf8")
        playlistString = playlistFile.read().rstrip()
        playlistVideoPaths = playlistString.split("\n")
        playlistVideoPaths.append(selectedFilePath)

        playlistFile.close()
        pathsString = "\n".join(playlistVideoPaths) + "\n"
    else:
        pathsString = selectedFilePath + "\n"
    playlistFile = open(playlistPath, "w", encoding="utf8")
    playlistFile.write(pathsString)
    print("Added: " + fileName)
    playlistFile.close()


def changePlayerSetting(settingKey, settingValueNew, settingValueOld, settingPath):
    if os.path.exists(settingPath):
        oldSetting = settingKey + "=" + settingValueOld
        newSetting = settingKey + "=" + settingValueNew
        for line in fileinput.input(settingPath, inplace = 1):
            if oldSetting in line:
                line = line.replace(oldSetting, newSetting)
            sys.stdout.write(line)
    else:
        print("Settings path does not exist:")
        print(settingPath)

