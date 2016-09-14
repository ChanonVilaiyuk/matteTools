#Import python modules
import os, sys
import sqlite3

#Import GUI
from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools
from shiboken import wrapInstance

# Import Maya module
import maya.OpenMayaUI as mui
import maya.cmds as mc
import maya.mel as mm

# import pipeline modules 
from tool.utils import mayaTools, pipelineTools
from tool.utils import entityInfo
from tool.utils import projectInfo
reload(projectInfo)

from tool.matte import create_db as db
reload(db)
from tool.matte import presets
reload(presets)

moduleFile = sys.modules[__name__].__file__
moduleDir = os.path.dirname(moduleFile)
sys.path.append(moduleDir)


def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is not  None:
        # ptr = mui.MQtUtil.mainWindow()
        return wrapInstance(long(ptr), QtGui.QMainWindow)

class MyForm(QtGui.QMainWindow):

    def __init__(self, parent=None):
        self.count = 0
        #Setup Window
        super(MyForm, self).__init__(parent)

        self.mayaUI = 'dbViewerWindow'
        deleteUI(self.mayaUI)

        # read .ui directly
        loader = QtUiTools.QUiLoader()
        loader.setWorkingDirectory(moduleDir)

        f = QtCore.QFile("%s/dbViewer.ui" % moduleDir)
        f.open(QtCore.QFile.ReadOnly)

        self.myWidget = loader.load(f, self)
        self.ui = self.myWidget

        f.close()

        self.ui.show()
        self.ui.setWindowTitle('PT Matte Viewer')

        # variable 
        self.asset = entityInfo.info()
        self.project = projectInfo.info()

        # project filters 
        self.projectPrefix = ['Lego_', 'TVC_']

        self.objectIDStep = 20
        self.objectIDStart = 100
        self.objectIDRange = 20000

        # icons 
        self.logo = '%s/%s' % (moduleDir, 'icons/logo.png')
        self.logo2 = '%s/%s' % (moduleDir, 'icons/shotgun_logo.png')
        self.okIcon = '%s/%s' % (moduleDir, 'icons/ok_icon.png')
        self.xIcon = '%s/%s' % (moduleDir, 'icons/x_icon.png')
        self.rdyIcon = '%s/%s' % (moduleDir, 'icons/rdy_icon.png')

        # table objectID
        self.idCol = 0 
        self.oIDCol = 1
        self.assetNameCol = 2
        self.assetPathCol = 3
        self.userCol = 4
        self.mIDsCol = 5

        # table matteID
        self.umidCol = 0 
        self.midCol = 1
        self.colorCol = 2
        self.multiMatteCol = 3
        self.vrayMtlCol = 4 

        # color 
        self.dbColor = [0, 20, 60]
        self.presetColor = [0, 20, 100]

        self.initFunctions()
        self.initSignals()


    def initFunctions(self) : 
        self.readDb()
        self.setUI()
        self.viewObjectIDTable()


    def initSignals(self) : 
        self.ui.project_comboBox.currentIndexChanged.connect(self.projectAction)
        self.ui.objectID_tableWidget.itemSelectionChanged.connect(self.viewMatteIDTable)

        # button 
        self.ui.delete_pushButton.clicked.connect(self.deleteObjectID)
        self.ui.delete2_pushButton.clicked.connect(self.deleteMatteID)


    def readDb(self) : 
        project = str(self.ui.project_comboBox.currentText())
        dbResult = db.readDatabase(project)
        self.ui.dbPath_lineEdit.setText(db.dbPath(project))

        self.dbData = dbResult

    def setUI(self) : 
        self.setProject()

    def setProject(self) : 
        projs = self.project.listProjects()
        projects = []

        for project in projs : 
            for prefix in self.projectPrefix : 
                if prefix in project : 
                    projects.append(project)

        self.ui.project_comboBox.addItems(projects)

        # current project
        currProject = self.asset.project()
        checkProject = [a.lower() for a in projects]

        if currProject.lower() in checkProject : 
            row = checkProject.index(currProject.lower())
            self.ui.project_comboBox.setCurrentIndex(row)
            self.readDb()


    def getDbData(self, col) : 
        return [a[col] for a in self.dbData]


    def viewObjectIDTable(self) : 
        # re read DB
        self.readDb()
        widget = 'objectID_tableWidget'
        widget2 = 'matteID_tableWidget'
        height = 20
        row = 0

        self.clearTable(widget)
        self.clearTable(widget2)
        
        for each in self.dbData : 
            ID = str(each[self.idCol])
            oID = str(each[self.oIDCol])
            assetName = str(each[self.assetNameCol])
            assetPath = str(each[self.assetPathCol])
            user = str(each[self.userCol])
            mIDs = str(each[self.mIDsCol])

            self.insertRow(row, height, widget)
            self.fillInTable(row, self.idCol, ID, widget, [1, 1, 1])
            self.fillInTable(row, self.oIDCol, oID, widget, [1, 1, 1])
            self.fillInTable(row, self.assetNameCol, assetName, widget, [1, 1, 1])
            self.fillInTable(row, self.assetPathCol, assetPath, widget, [1, 1, 1])
            self.fillInTable(row, self.userCol, user, widget, [1, 1, 1])
            self.fillInTable(row, self.mIDsCol, mIDs, widget, [1, 1, 1])

            row += 1 

        self.ui.objectID_tableWidget.resizeColumnToContents(self.idCol)
        self.ui.objectID_tableWidget.resizeColumnToContents(self.oIDCol)
        self.ui.objectID_tableWidget.resizeColumnToContents(self.assetNameCol)
        # self.ui.objectID_tableWidget.resizeColumnToContents(self.assetPathCol)
        self.ui.objectID_tableWidget.resizeColumnToContents(self.userCol)
        self.ui.objectID_tableWidget.resizeColumnToContents(self.mIDsCol)


    def viewMatteIDTable(self) : 
        # sel item 
        selMatteID = self.getDataFromSelectedRange(self.mIDsCol, 'objectID_tableWidget')
        selMatteIDList = [a for a in eval(selMatteID[0])]

        # re read DB
        # self.readDb()
        matteIDs = self.getMatteIDValue(selMatteID)
        presetMatteIDs = presets.extraPreset

        row = 0 
        widget = 'matteID_tableWidget'
        height = 20

        if matteIDs : 

            self.clearTable(widget)

            for eachItem in matteIDs : 
                self.umidCol 
                self.midCol
                self.colorCol
                self.multiMatteCol
                self.vrayMtlCol

                ID = str(eachItem[self.umidCol ])
                mID = str(eachItem[self.midCol])
                color = str(eachItem[self.colorCol])
                multiMatte = str(eachItem[self.multiMatteCol])
                vrayMtl = str(eachItem[self.vrayMtlCol])

                self.insertRow(row, height, widget)
                self.fillInTable(row, self.umidCol, ID, widget, self.dbColor)
                self.fillInTable(row, self.midCol, mID, widget, self.dbColor)
                self.fillInTable(row, self.colorCol, color, widget, self.dbColor)
                self.fillInTable(row, self.multiMatteCol, multiMatte, widget, self.dbColor)
                self.fillInTable(row, self.vrayMtlCol, vrayMtl, widget, self.dbColor)

                row += 1 

            for mID in selMatteIDList : 
                if mID in presetMatteIDs : 
                    mm = presetMatteIDs[mID]['mm']
                    color = ''
                    vrayMtl = ''

                    self.insertRow(row, height, widget)
                    self.fillInTable(row, self.umidCol, str(mID), widget, self.presetColor)
                    self.fillInTable(row, self.midCol, str(mID), widget, self.presetColor)
                    self.fillInTable(row, self.colorCol, color, widget, self.presetColor)
                    self.fillInTable(row, self.multiMatteCol, mm, widget, self.presetColor)
                    self.fillInTable(row, self.vrayMtlCol, vrayMtl, widget, self.presetColor)

                    row += 1 


            self.ui.matteID_tableWidget.resizeColumnToContents(self.umidCol )
            self.ui.matteID_tableWidget.resizeColumnToContents(self.midCol)
            self.ui.matteID_tableWidget.resizeColumnToContents(self.colorCol)
            self.ui.matteID_tableWidget.resizeColumnToContents(self.multiMatteCol)
            self.ui.matteID_tableWidget.resizeColumnToContents(self.vrayMtlCol)



    def getMatteIDValue(self, matteIDs) : 

        if matteIDs : 
            mIDs = eval(matteIDs[0])
            project = str(self.ui.dbPath_lineEdit.text())
            conn = sqlite3.connect(project)
            matteIDValue = []

            for eachID in mIDs : 
                result = db.getMatteID(conn, eachID)

                for each in result : 
                    if not each in matteIDValue : 
                        matteIDValue.append(each)

            return matteIDValue



    def projectAction(self) : 
        self.readDb()
        self.viewObjectIDTable()


    # button action 
    def deleteObjectID(self) : 
        conn = sqlite3.connect(str(self.ui.dbPath_lineEdit.text()))
        oIDs = self.getDataFromSelectedRange(self.oIDCol, 'objectID_tableWidget')
        mIDs = self.getDataFromSelectedRange(self.mIDsCol, 'objectID_tableWidget')
        db.deleteObjectID(conn, oIDs)
        db.deleteMatteID(conn, eval(mIDs[0]))
        conn.commit()
        conn.close()

        self.viewObjectIDTable()

    def deleteMatteID(self) : 
        conn = sqlite3.connect(str(self.ui.dbPath_lineEdit.text()))
        mIDs = self.getDataFromSelectedRange(self.midCol, 'matteID_tableWidget')
        db.deleteMatteID(conn, mIDs)
        conn.commit()
        conn.close()

        self.viewMatteIDTable()

    # Table Functions 

    def insertRow(self, row, height, widget) : 
        cmd1 = 'self.ui.%s.insertRow(row)' % widget
        cmd2 = 'self.ui.%s.setRowHeight(row, height)' % widget

        eval(cmd1)
        eval(cmd2)


    def fillInTable(self, row, column, text, widget, color = [1, 1, 1]) : 
        item = QtGui.QTableWidgetItem()
        item.setText(text)
        item.setBackground(QtGui.QColor(color[0], color[1], color[2]))
        cmd = 'self.ui.%s.setItem(row, column, item)' % widget
        eval(cmd)


    def fillInTableIcon(self, row, column, text, iconPath, widget, color = [1, 1, 1]) : 
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        item = QtGui.QTableWidgetItem()
        item.setText(str(text))
        item.setIcon(icon)
        item.setBackground(QtGui.QColor(color[0], color[1], color[2]))
        
        cmd = 'self.ui.%s.setItem(row, column, item)' % widget
        eval(cmd)


    def getAllData(self, columnNumber, widget) : 
        count = eval('self.ui.%s.rowCount()' % widget)
        items = []

        for i in range(count) : 
            item = str(eval('self.ui.%s.item(i, columnNumber).text()' % widget))
            items.append(item)


        return items


    def getDataFromSelectedRange(self, columnNumber, widget) : 
        lists = eval('self.ui.%s.selectedRanges()' % widget)

        if lists : 
            topRow = lists[0].topRow()
            bottomRow = lists[0].bottomRow()
            leftColumn = lists[0].leftColumn()
            rightColumn = lists[0].rightColumn()

            items = []

            for i in range(topRow, bottomRow + 1) : 
                item = str(eval('self.ui.%s.item(i, columnNumber)' % widget).text())
                items.append(item)


            return items


    def getSelectionRows(self, widget) : 
        lists = eval('self.ui.%s.selectedRanges()' % widget)

        if lists : 
            topRow = lists[0].topRow()
            bottomRow = lists[0].bottomRow()
            leftColumn = lists[0].leftColumn()
            rightColumn = lists[0].rightColumn()

            return [topRow, bottomRow, leftColumn, rightColumn]



    def clearTable(self, widget) : 
        cmd = 'self.ui.%s.rowCount()' % widget
        rows = eval(cmd)
        # self.ui.asset_tableWidget.clear()

        for each in range(rows) : 
            cmd2 = 'self.ui.%s.removeRow(0)' % widget
            eval(cmd2)



def deleteUI(ui) : 
    if mc.window(ui, exists = True) : 
        mc.deleteUI(ui)