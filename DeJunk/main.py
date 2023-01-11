import os
import sys
import platform
import time
from idlelib.query import Goto

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence,
                           QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *
from sklearn.metrics import mean_squared_error
from math import sqrt
from os.path import join
# from PyQt5.QtWidgets import QLineEdit
# from PyQt5 import QtCore, QtWidgets
# from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit
# from PyQt5.QtWidgets import QPushButton
# from PyQt5.QtCore import QSize
import cv2
import numpy as np
import shutil
from pymongo import MongoClient
import gridfs
import stat
# GUI FILE
from app_modules import *

folder = ""


def mongo_conn():
    try:
        conn = MongoClient(host='127.0.0.1', port=27017)
        print("MongoDB connected", conn)
        return conn.deJunk
    except Exception as e:
        print("Error in mongo connection:", e)


os.environ["PATH"] += os.pathsep + os.getcwd()


def getBwLittleImgs(datasetPath):
    # Find all classes paths in directory and iterate over it
    for (i, classPath) in enumerate(os.listdir(datasetPath)):
        if classPath == "detected" or classPath == "bwdir":
            continue

        # Construct detected directory with images from MobileNET SSD
        imgDir = join(datasetPath, classPath)
        print(imgDir)
        # Construct directory to write 32x32 pix images
        bwDir = join(datasetPath, "bwdir")

        # Create bwDir patch or delete existing!
        if not os.path.exists(bwDir):
            os.makedirs(bwDir)
        # else:
        #     # shutil.rmtree(bwDir)
        #     os.makedirs(bwDir)

        # Iterate over all images in detected directory
        if os.path.isfile(imgDir):
            print("inside")
            imgPath = imgDir
            print("inside-->" + imgPath)
            image = cv2.imread(imgPath, cv2.IMREAD_GRAYSCALE)

            if image is not None:
                # Resize opened image
                resized_image = cv2.resize(image, (32, 32))
                resized_image = np.array(resized_image)
                # Save image to bwdir. Name should be the same as name in "detected" directory
                print("write path-->" + os.path.join(bwDir, classPath))
                cv2.imwrite(os.path.join(bwDir, classPath), resized_image)
            else:
                # remove a file that is not an image. I don't need it.
                print(imgPath)
                os.remove(imgPath)
        else:
            for (j, imgName) in enumerate(os.listdir(imgDir)):
                print("inside 2")
                print(imgName)
                # Construct patch to single image
                imgPath = join(imgDir, imgName)
                # Read image using OpenCV as grayscale
                image = cv2.imread(imgPath, cv2.IMREAD_GRAYSCALE)

            # Check if we opened an image.
            if image is not None:
                # Resize opened image
                resized_image = cv2.resize(image, (32, 32))
                resized_image = np.array(resized_image)
                # Save image to bwdir. Name should be the same as name in "detected" directory
                cv2.imwrite(os.path.join(bwDir, imgName), resized_image)
            else:
                # remove a file that is not an image. I don't need it.
                print(imgPath)
                os.remove(imgPath)

def findDelDuplBw(searchedName, bwDir):
    # Join path to orginal image that we are looking duplicates
    searchedImg = join(bwDir, searchedName)

    # Start iterate over all bw images
    for (j, cmpImageName) in enumerate(os.listdir(bwDir)):

        if cmpImageName == searchedName:
            # If name in bwDir is equal to searched image - pass. I don't wan to deletde searched image in bw dir
            pass
        else:
            # If name is different - concatenate path to image
            cmpImageBw = join(bwDir, cmpImageName)

            try:
                # Open image in bwDir - The searched image
                searchedImageBw = np.array(cv2.imread(searchedImg, cv2.IMREAD_GRAYSCALE))
                # Open image to be compared
                cmpImage = np.array(cv2.imread(cmpImageBw, cv2.IMREAD_GRAYSCALE))
                # Count root mean square between both images (RMS)
                rms = sqrt(mean_squared_error(searchedImageBw, cmpImage))
            except:
                continue

            # If RMS is smaller than 3 - this means that images are simmilar or the same
            if rms < 9.5:
                # Delete compared image in BW dir
                os.remove(cmpImageBw)
                print(searchedImg, cmpImageName, rms)


def findDelDetected(detectedDir, bwDir, folder):
    # I have to compare bw dir and detected dir.
    # In bw dir I get rid of duplacates. Now I have to
    # get rid of duplicates in detected dir

    # List all bw files in bw dir
    bwFiles = os.listdir(bwDir)

    # Iterate over detected dir
    for file in os.listdir(detectedDir):
        if (file == "detected" or file == "bwdir"):
            continue
        # Check if file in detected dir can be found in bw dir
        if file not in bwFiles:
            # Deletde if not. This means that the duplicate or simillar image is found
            print(file, " to be deleted")

            # upload to mongo as backup
            db = mongo_conn()
            file_location = os.path.join(detectedDir, file)
            file_data = open(file_location, "rb")
            data = file_data.read()
            fs = gridfs.GridFS(db)
            fs.put(data, filename=file, foldername=folder)
            file_data.close()
            print('upload complete\n')
            print(str(file))
            # delete files from local machine
            os.remove(os.path.join(detectedDir, file))


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ## PRINT ==> SYSTEM
        print('System: ' + platform.system())
        print('Version: ' + platform.release())

        ########################################################################
        ## START - WINDOW ATTRIBUTES
        ########################################################################

        ## REMOVE ==> STANDARD TITLE BAR
        UIFunctions.removeTitleBar(True)
        ## ==> END ##

        ## SET ==> WINDOW TITLE
        self.setWindowTitle('DeJunk')
        UIFunctions.labelTitle(self, 'DeJunk')
        UIFunctions.labelDescription(self, 'QuadBytes')
        ## ==> END ##

        ## WINDOW SIZE ==> DEFAULT SIZE
        startSize = QSize(1000, 720)
        self.resize(startSize)
        self.setMinimumSize(startSize)
        # UIFunctions.enableMaximumSize(self, 500, 720)
        ## ==> END ##

        ## ==> CREATE MENUS
        ########################################################################

        ## ==> TOGGLE MENU SIZE
        self.ui.btn_toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 220, True))
        ## ==> END ##

        ## ==> ADD CUSTOM MENUS
        self.ui.stackedWidget.setMinimumWidth(20)
        UIFunctions.addNewMenu(self, "HOME", "btn_home", "url(:/16x16/icons/16x16/cil-home.png)", True)
        # UIFunctions.addNewMenu(self, "Retrieve Files", "btn_new_user", "url(:/16x16/icons/16x16/cil-loop-circular.png)", True)
        # UIFunctions.addNewMenu(self, "Custom Widgets", "btn_widgets", "url(:/16x16/icons/16x16/cil-equalizer.png)", False)
        ## ==> END ##

        # START MENU => SELECTION
        UIFunctions.selectStandardMenu(self, "btn_home")
        ## ==> END ##

        ## ==> START PAGE
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
        ## ==> END ##

        ## USER ICON ==> SHOW HIDE
        UIFunctions.userIcon(self, "DJ", "", True)
        ## ==> END ##

        self.UiComponents()
        self.UiComponents2()

        ## ==> MOVE WINDOW / MAXIMIZE / RESTORE
        ########################################################################
        def moveWindow(event):
            # IF MAXIMIZED CHANGE TO NORMAL
            if UIFunctions.returStatus() == 1:
                UIFunctions.maximize_restore(self)

            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        # WIDGET TO MOVE
        self.ui.frame_label_top_btns.mouseMoveEvent = moveWindow
        ## ==> END ##

        ## ==> LOAD DEFINITIONS
        ########################################################################
        UIFunctions.uiDefinitions(self)
        ## ==> END ##

        ########################################################################
        ## END - WINDOW ATTRIBUTES
        ############################## ---/--/--- ##############################

        ########################################################################
        #                                                                      #
        ## START -------------- WIDGETS FUNCTIONS/PARAMETERS ---------------- ##
        #                                                                      #
        ## ==> USER CODES BELLOW                                              ##
        ########################################################################

        ## ==> QTableWidget RARAMETERS
        ########################################################################
        #  self.ui.stackedWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ## ==> END ##

        ########################################################################
        #                                                                      #
        ## END --------------- WIDGETS FUNCTIONS/PARAMETERS ----------------- ##
        #                                                                      #
        ############################## ---/--/--- ##############################

        ## SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        ## ==> END ##

    ########################################################################
    ## MENUS ==> DYNAMIC MENUS FUNCTIONS
    ########################################################################
    def Button(self):
        # GET BT CLICKED
        btnWidget = self.sender()

        # PAGE HOME
        if btnWidget.objectName() == "btn_home":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
            UIFunctions.resetStyle(self, "btn_home")
            UIFunctions.labelPage(self, "Home")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        # PAGE NEW USER
        if btnWidget.objectName() == "btn_new_user":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
            UIFunctions.resetStyle(self, "btn_new_user")
            UIFunctions.labelPage(self, "Retrieve Files")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        # PAGE WIDGETS
        if btnWidget.objectName() == "btn_widgets":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_widgets)
            UIFunctions.resetStyle(self, "btn_widgets")
            UIFunctions.labelPage(self, "Custom Widgets")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

    ## ==> END ##

    ########################################################################
    ## START ==> APP EVENTS
    ########################################################################

    ## EVENT ==> MOUSE DOUBLE CLICK
    ########################################################################
    def eventFilter(self, watched, event):
        if watched == self.le and event.type() == QtCore.QEvent.MouseButtonDblClick:
            print("pos: ", event.pos())

    ## ==> END ##

    ## EVENT ==> MOUSE CLICK
    ########################################################################
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')
        if event.buttons() == Qt.MidButton:
            print('Mouse click: MIDDLE BUTTON')

    ## ==> END ##

    ## EVENT ==> KEY PRESSED
    ########################################################################
    def keyPressEvent(self, event):
        print('Key: ' + str(event.key()) + ' | Text Press: ' + str(event.text()))

    ## ==> END ##

    ## EVENT ==> RESIZE EVENT
    ########################################################################
    def resizeEvent(self, event):
        self.resizeFunction()
        return super(MainWindow, self).resizeEvent(event)

    def resizeFunction(self):
        print('Height: ' + str(self.height()) + ' | Width: ' + str(self.width()))

    ## ==> END ##

    ########################################################################
    ## END ==> APP EVENTS
    ############################## ---/--/--- ##############################

    # method for widgets
    def UiComponents(self):
        # creating a push button
        button = QPushButton("OPEN DIRECTORY", self)

        # setting geometry of button
        button.setGeometry(400, 350, 250, 40)
        button.setCheckable(True)
        button.setStyleSheet("""
                     QPushButton {background:rgb(0,0,0); color: white;border-radius: 10px} 
                      QPushButton::hover{ background : white;color: black;}
                 """)

        # adding action to a button
        button.clicked.connect(self.clickme)

    def UiComponents2(self):
        # creating a push button
        button = QPushButton("RECOVER DELETED FILES", self)

        # setting geometry of button
        button.setGeometry(400, 450, 250, 40)

        button.setCheckable(True)
        button.setStyleSheet("""
              QPushButton {background:rgb(0,0,0); color: white;border-radius: 10px} 
               QPushButton::hover{ background : white;color: black; } 
               """)

        # adding action to a button
        button.clicked.connect(self.clickme2)

    def clickme(self):
        # printing pressed

        fname = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(fname)

        ret = QMessageBox.question(self, '', "Are you sure to Continue.?", QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            QMessageBox.about(self, "DeJunk", "Scan and Deletion in Progress From Selected Directory")

            datasetPath = fname
            folder = datasetPath.split('/')[-1]

            getBwLittleImgs(datasetPath)

            # Now lets iterate over all classes in data set
            # for (i, classPath) in enumerate(os.listdir(datasetPath)):

            # Join detected by previous script path
            # detectedDir = join(datasetPath, classPath, "detected")
            # print(detectedDir)
            # Join black-white images path
            bwDir = join(datasetPath, "bwdir")

            # Iterate over images in one class - detected images previously by MobileSSD net
            for (i, detectedImg) in enumerate(os.listdir(datasetPath)):
                if detectedImg == "detected" or detectedImg == "bwdir":
                    continue
                # Find duplicated BW images and delete duplicates.
                findDelDuplBw(detectedImg, bwDir)

            # Basing on cleaned BW images, now clean detected direcotry comparing data
            # between detected directory and bwDir directory
            findDelDetected(datasetPath, bwDir, folder)

            # Remove bwDir - we don't need it any more
            # shutil.rmtree(bwDir)
            QMessageBox.about(self, "DeJunk", "Duplicates Deleted! Backup can be found on MongoDB")

    def clickme2(self):
        db = mongo_conn()
        fs = gridfs.GridFS(db)
        folderName = QInputDialog.getText(self, 'Python', "Enter folder Name")
        print(folderName[0])
        data = fs.find({'foldername': folderName[0]})
        for x in data:
            outputdata = x.read()
            print(x.filename)
            download_location = "C:\\Users\\simra\\Desktop\\dejunk_backup\\" + x.filename
            output = open(download_location, "wb")
            output.write(outputdata)
            output.close()
        print("download complete")
        QMessageBox.about(self, "DeJunk", "Images Successfully restored! Backup can be found on C:\\Users\\simra\\Desktop\\dejunk_backup\\")

    #########################################################################


if __name__ == "__main__":
    # app = QApplication(sys.argv)
    app2 = QtWidgets.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = MainWindow()
    sys.exit(app2.exec_())
