#!/usr/bin/python3

import sys, os, functions, random, subprocess, time, glob, logging, psutil
import winsound
from pathlib import Path
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class WhirligigGUI(QWidget):
    def __init__(self, parent = None):
        super(WhirligigGUI, self).__init__(parent)

        self.rootdir = os.path.dirname(os.path.realpath(__file__))
        loggingPath = os.path.dirname(os.path.realpath(__file__)) + '/monitorLog.txt'
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(loggingPath, "a")
        formatter = logging.Formatter('%(asctime)s, %(name)s %(funcName)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.rootdir = Path(os.path.dirname(os.path.realpath(__file__)))
        username = psutil.users()[0][0]
        self.playlistsFolderPath = "C:/Users/" + username + "/AppData/Roaming/Whirligig/production/Playlists"
        self.selectedPlaylistName = ""

        self.shortcutDelete = QShortcut(QKeySequence("Del"), self)
        self.shortcutDelete.activated.connect(self.deleteVideoFromPlaylist)

        self.levelTop = QHBoxLayout()
        self.level0h = QVBoxLayout()
        self.level1g = QGridLayout()

        self.scriptStatusLabel = QLabel("Waiting to start")
        self.level1g.addWidget(self.scriptStatusLabel, 0, 2)

        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.startScript)
        self.level1g.addWidget(self.startButton, 1, 0)

        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(self.stopScript)
        self.level1g.addWidget(self.stopButton, 1, 1)

        self.bRemoveDuplicates = QPushButton("Remove Duplicates")
        self.bRemoveDuplicates.clicked.connect(self.removeDuplicates)
        self.level1g.addWidget(self.bRemoveDuplicates, 1, 2)

        self.bSortRandom = QPushButton("Sort Random")
        self.bSortRandom.clicked.connect(self.sortRandom)
        self.level1g.addWidget(self.bSortRandom, 1, 3)

        self.bSortAlpha = QPushButton("Sort Alphabetically")
        self.bSortAlpha.clicked.connect(self.sortAlpha)
        self.level1g.addWidget(self.bSortAlpha, 1, 4)

        self.bSortReverse = QPushButton("Sort Reverse")
        self.bSortReverse.clicked.connect(self.sortReverse)
        self.level1g.addWidget(self.bSortReverse, 1, 5)

        self.playlistNameLabel = QLabel("Playlist Name")
        self.level1g.addWidget(self.playlistNameLabel, 2, 0)

        self.playlistNameInput = QLineEdit("")
        self.level1g.addWidget(self.playlistNameInput, 2, 1, 1, 2)
        self.level0h.addLayout(self.level1g)

        self.bUpdateList = QPushButton("Update")
        self.bUpdateList.clicked.connect(self.addPlaylistsToList)
        self.level1g.addWidget(self.bUpdateList, 2, 3)

        self.levelBottom = QHBoxLayout()

        self.lwPlaylist = QListWidget()
        self.lwPlaylist.setFixedWidth(200)
        self.addPlaylistsToList()
        self.lwPlaylist.itemSelectionChanged.connect(self.selectedPlaylist)
        self.lwPlaylist.itemDoubleClicked.connect(self.renamePlaylist)
        self.levelBottom.addWidget(self.lwPlaylist)
        #self.levelBottom.addStretch()
        self.lwPlaylistContents = QListWidget()
        self.lwPlaylistContents.itemSelectionChanged.connect(self.selectedVideo)
        self.levelBottom.addWidget(self.lwPlaylistContents)
        self.level0h.addLayout(self.levelBottom)

        #self.level0h.addStretch()

        self.levelTop.addLayout(self.level0h)


        self.setLayout(self.levelTop)
        self.setWindowTitle("Whirligig Monitor GUI")
        self.setWindowIcon(QIcon(str(self.rootdir / 'icons' / 'r.svg')))
        self.setGeometry(2200, 250, 800, 500)
        self.logger.info("Opened GUI")

    def renamePlaylist(self):
        self.logger.info("Rename playlist")
        newName, okPressed = QInputDialog.getText(self, "Rename Playlist", "New Name:", QLineEdit.Normal, "")
        if okPressed and not newName == '':
            originalIndex = self.selectedPlaylistIndex
            self.logger.info(f'Change name to: {newName}')
            basePath = Path(self.playlistsFolderPath)
            oldPlaylistName = self.selectedPlaylistName + ".plt"
            newPlaylistName = newName + ".plt"
            oldPlaylistPath = basePath / oldPlaylistName
            newPlaylistPath = basePath / newPlaylistName
            os.rename(oldPlaylistPath, newPlaylistPath)
            self.addPlaylistsToList()
            if originalIndex > -1:
                item = self.lwPlaylist.item(originalIndex)
                self.lwPlaylist.setCurrentItem(item)


    def selectedVideo(self):
        if self.lwPlaylistContents.selectedItems() and len(self.lwPlaylistContents.selectedItems()) < 2:
            si = self.lwPlaylistContents.selectedItems()[0]
            i = self.lwPlaylistContents.row(si)
            self.selectedVideoName = str(si.text())
            self.selectedVideoIndex = i
            self.logger.info("Playlist {} selected".format(si.text()))
            self.logger.info("Index {} selected".format(i))
        else:
            self.selectedVideoName = ""
            self.selectedVideoIndex = -1

    def selectedPlaylist(self):
        if self.lwPlaylist.selectedItems() and len(self.lwPlaylist.selectedItems()) < 2:
            si = self.lwPlaylist.selectedItems()[0]
            i = self.lwPlaylist.row(si)
            self.selectedPlaylistName = str(si.text())
            self.selectedPlaylistIndex = i
            playlistName = self.selectedPlaylistName + ".plt"
            basePath = Path(self.playlistsFolderPath)
            playlistPath = basePath / playlistName
            self.playlistContents = functions.getPlaylistContents(str(playlistPath))
            self.lwPlaylistContents.clear()
            self.logger.info("Playlist {} selected".format(si.text()))
            for fileDict in self.playlistContents:
                self.lwPlaylistContents.addItem(fileDict["Base"])
        else:
            self.lwPlaylistContents.clear()
            self.selectedPlaylistName = ""
            self.selectedPlaylistIndex = -1
            self.playlistContents = []

    def deleteVideoFromPlaylist(self):
        if self.selectedVideoIndex > -1:
            fileBaseName = self.playlistContents[self.selectedVideoIndex]["Base"]
            self.logger.info("Trying to delete {}".format(fileBaseName))
            playlistName = self.selectedPlaylistName + ".plt"
            basePath = Path(self.playlistsFolderPath)
            playlistPath = basePath / playlistName
            deletePath = self.playlistContents[self.selectedVideoIndex]["Path"]
            buttonReply = QMessageBox.question(self, 'Confirm Delete', "Are you sure you want to delete {}".format(fileBaseName),
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                functions.deleteVideoFromPlaylist(playlistPath, deletePath)
                self.selectedPlaylist()

    def addPlaylistsToList(self):
        self.lwPlaylist.clear()
        self.logger.info("Playlists cleared")
        playlistPaths = glob.glob(self.playlistsFolderPath + "/*.plt")
        playlistPaths.sort(key=os.path.getmtime, reverse=True)
        for path in playlistPaths:
            fullFileName = os.path.basename(path)
            baseName, extension = os.path.splitext(fullFileName)
            self.lwPlaylist.addItem(baseName)
        self.logger.info("Playlists added to list")

    def removeDuplicates(self):
        if self.selectedPlaylistName:
            playlistPath = self.playlistsFolderPath + "/" + self.selectedPlaylistName + ".plt"
            try:
                functions.removePlaylistDuplicates(playlistPath)
            except:
                self.logger.exception("Removing duplicates failed")
            else:
                self.scriptStatusLabel.setText("Removed duplicates for: " + self.selectedPlaylistName)
                self.logger.info("Removed duplicates for: " + self.selectedPlaylistName)
                self.selectedPlaylist()

    def sortRandom(self):
        if self.selectedPlaylistName:
            self.logger.info("Start randomize process")
            playlistPath = self.playlistsFolderPath + "/" + self.selectedPlaylistName + ".plt"
            try:
                playlistFile = open(playlistPath, "r", encoding="utf8")
            except:
                self.logger.exception("Failed to open")
            else:
                self.logger.info("Successfully opened")
            try:
                playlistString = playlistFile.read().rstrip()
            except:
                self.logger.exception("Failed to read")
            else:
                self.logger.info("Successfully read")
            playlistFile.close()
            try:
                playlistVideoPaths = playlistString.split("\n")
            except:
                self.logger.exception("Failed to split")
            else:
                self.logger.info('Successfully split total items {}'.format(len(playlistVideoPaths)))
            if playlistVideoPaths:
                try:
                    random.seed()
                    random.shuffle(playlistVideoPaths)
                    random.seed(3)
                    random.shuffle(playlistVideoPaths)
                except:
                    self.logger.exception("Shuffle failed")
                else:
                    self.logger.info('Successfully shuffled total items {}'.format(len(playlistVideoPaths)))
                    pathsString = "\n".join(playlistVideoPaths) + "\n"
                    self.logger.info('Joined total chars {}'.format(len(pathsString)))
                    playlistFile = open(playlistPath, "w", encoding="utf8")
                    playlistFile.write(pathsString)
                    playlistFile.close()
                    self.scriptStatusLabel.setText("Randomized: " + self.selectedPlaylistName)
                    self.logger.info("Randomized: " + self.selectedPlaylistName)
                    self.selectedPlaylist()

    def sortAlpha(self):
        if self.selectedPlaylistName:
            playlistPath = self.playlistsFolderPath + "/" + self.selectedPlaylistName + ".plt"
            playlistFile = open(playlistPath, "r", encoding="utf8")
            playlistString = playlistFile.read().rstrip()
            playlistFile.close()
            playlistVideoPaths = playlistString.split("\n")
            try:
                playlistVideoPaths = sorted(playlistVideoPaths, key=os.path.basename)
            except:
                self.logger.exception("Failed to sort alphabetically")
            else:
                pathsString = "\n".join(playlistVideoPaths) + "\n"
                playlistFile = open(playlistPath, "w", encoding="utf8")
                playlistFile.write(pathsString)
                playlistFile.close()
                self.scriptStatusLabel.setText("Alphabeticalized: " + self.selectedPlaylistName)
                self.logger.info("Alphabeticalized: " + self.selectedPlaylistName)
                self.selectedPlaylist()

    def sortReverse(self):
        if self.selectedPlaylistName:
            playlistPath = self.playlistsFolderPath + "/" + self.selectedPlaylistName + ".plt"
            playlistFile = open(playlistPath, "r", encoding="utf8")
            playlistString = playlistFile.read().rstrip()
            playlistFile.close()
            playlistVideoPaths = playlistString.split("\n")

            playlistVideoPaths.reverse()

            pathsString = "\n".join(playlistVideoPaths) + "\n"
            playlistFile = open(playlistPath, "w", encoding="utf8")
            playlistFile.write(pathsString)
            playlistFile.close()
            self.scriptStatusLabel.setText("Reversed: " + self.selectedPlaylistName)
            self.logger.info("Reversed: " + self.selectedPlaylistName)
            self.selectedPlaylist()

    def stopScript(self):
        f = open(str(self.rootdir) + "/tempStop.txt", "w")
        f.write("Stop")
        f.close()
        print("Stop")

        self.logger.info("Script set to stopped")

        pathPID = self.rootdir / "monitorPID.txt"
        filePID = open(str(pathPID), "r")
        raw = filePID.read().rstrip()
        pid = int(raw)
        filePID.close()
        info = f'Process ID to search for: {pid}'
        self.logger.info(info)

        if psutil.pid_exists(pid):
            info = f'Killing process ID {pid}'
            self.logger.info(info)
            for proc in psutil.process_iter():
                try:
                    processID = proc.pid
                    processName = proc.name()
                except:
                    self.logger.debug("No access")
                else:
                    if proc.pid == pid:
                        info = f'{processName}: {processID}'
                        self.logger.info(info)
                        self.logger.info("Trying to kill")
                        proc.kill()
                        self.scriptStatusLabel.setText("Script stopped")
                        self.startButton.setDisabled(False)
                        break
        else:
            info = f'Process ID {pid} does not exist'
            self.logger.error(info)
            self.scriptStatusLabel.setText("Failed to stop script")


    def startScript(self):
        playlistName = self.playlistNameInput.text() + ".plt"
        #playlistName = playlistName.replace(" ", "_")

        f = open(str(self.rootdir) + "/tempStop.txt", "w")
        f.write("Start")
        f.close()
        f = open(str(self.rootdir) + "/temp.txt", "w")
        f.write(playlistName)
        f.close()
        try:
            launchPath = self.rootdir + "\\launcher.py"
            subprocess.Popen(launchPath, shell=True)
        except:
            self.logger.exception("Script failed to execute")
            self.scriptStatusLabel.setText("Script failed to execute")
        else:
            self.logger.info("Started Launcher from GUI")
            self.scriptStatusLabel.setText("Script Running")
            self.startButton.setDisabled(True)





loggingPath = os.path.dirname(os.path.realpath(__file__)) + '/monitorLog.txt'
loggerGUI = logging.getLogger(__name__)
loggerGUI.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(loggingPath)
formatter = logging.Formatter('%(asctime)s, %(name)s %(funcName)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
loggerGUI.addHandler(file_handler)



def main():
    app = QApplication(sys.argv)
    ex = WhirligigGUI()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()
    except:
        loggerGUI.exception("Main failed")