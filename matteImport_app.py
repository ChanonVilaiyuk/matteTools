#Import python modules
import os, sys
import sqlite3
from collections import Counter

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
from tool.utils import entityInfo2 as entityInfo
from tool.utils import projectInfo
from tool.utils.vray import vray_utils as vr
reload(projectInfo)
reload(vr)
reload(pipelineTools)

from tool.matte import create_db as db
reload(db)
from tool.matte import presets, customWidget
reload(presets)
reload(customWidget)

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

        self.mayaUI = 'matteImportWin'
        deleteUI(self.mayaUI)

        # read .ui directly
        loader = QtUiTools.QUiLoader()
        loader.setWorkingDirectory(moduleDir)

        f = QtCore.QFile("%s/matteImport_ui.ui" % moduleDir)
        f.open(QtCore.QFile.ReadOnly)

        self.myWidget = loader.load(f, self)
        self.ui = self.myWidget

        f.close()

        self.ui.show()
        self.ui.setWindowTitle('PT Vray Matte Import v.1.0')

        # variable 
        self.asset = entityInfo.info()
        self.project = projectInfo.info()

        # project filters 
        self.projectPrefix = ['Lego_', 'TVC_']

        # char ID 
        self.objectIDStep = 20
        self.objectIDStart = 1000
        self.objectIDRange = 20000


        # prop ID 
        self.propIDStep = 10
        self.propIDStart = 100000
        self.propIDRange = 110000

        # icons 
        self.logo = '%s/%s' % (moduleDir, 'icons/logo.png')
        self.logo2 = '%s/%s' % (moduleDir, 'icons/logo2.png')
        self.okIcon = '%s/%s' % (moduleDir, 'icons/ok_icon.png')
        self.xIcon = '%s/%s' % (moduleDir, 'icons/x_icon.png')
        self.rdyIcon = '%s/%s' % (moduleDir, 'icons/rdy_icon.png')
        self.redIcon = '%s/%s' % (moduleDir, 'icons/red2_icon.png')

        self.openStatus = 'Open           '
        self.assignStatus = 'Assigned      '
        self.duplicatedStatus = 'Duplicated ID'
        self.readyStatus = 'Ready'
        self.inDb = 'In DataBase'
        self.wrongIDStatus = 'Wrong ID Setting'
        self.extraPresetStatus = 'Extra Preset'

        # target rigGrp
        self.rigGrp = 'Rig_Grp'
        self.geoGrp = 'Geo_Grp'

        # table objectID
        self.statusCol = 0 
        self.assetCol = 1
        self.noCol = 2
        self.oIDCol = 3
        self.mIDsCol = 4
        self.pathCol = 5

        # table colors
        self.red = [60, 0, 0]
        self.green = [0, 60, 0]
        self.blue = [20, 40, 100]
        self.lightGreen = [40, 100, 0]

        self.initFunctions()
        self.initSignals()


    def initFunctions(self) : 
        self.readDb()
        self.setUI()


    def initSignals(self) : 
        self.ui.project_comboBox.currentIndexChanged.connect(self.projectAction)

        # button 
        self.ui.dbView_pushButton.clicked.connect(self.runDBView)
        self.ui.create_pushButton.clicked.connect(self.doCreate)

        # table widget 
        # self.ui.tableWidget.itemSelectionChanged.connect(self.tableAction)


    def readDb(self) : 
        project = str(self.ui.project_comboBox.currentText())
        dbResult = db.readDatabase(project)
        self.ui.db_lineEdit.setText(db.dbPath(project))

        self.dbData = dbResult

    def setUI(self) : 
        self.setLogo()
        self.setProject()
        self.setAssetListUI()
        self.checkStatus()


    def refreshUI(self) : 
        self.setAssetListUI()


    def setLogo(self) : 
        self.ui.logo_label.setPixmap(QtGui.QPixmap(self.logo).scaled(200, 60, QtCore.Qt.KeepAspectRatio))
        self.ui.logo2_label.setPixmap(QtGui.QPixmap(self.logo2).scaled(126, 60, QtCore.Qt.KeepAspectRatio))



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

        if currProject in projects : 
            row = projects.index(currProject)
            self.ui.project_comboBox.setCurrentIndex(row)
            self.readDb()


    def getDbData(self, col) : 
        return [a[col] for a in self.dbData]

    def getAssetNameDb(self, assetName) : 
        dbPath = str(self.ui.db_lineEdit.text())
        conn = sqlite3.connect(dbPath)
        result = db.getAssetName(conn, assetName)
        assetNames = [a for a in result]
        conn.close()

        return assetNames

    def projectAction(self) : 
        self.readDb()


    def setStatus(self, status) : 
        if status == 'booked' : 
            iconPath = self.okIcon

        if status == 'ready' : 
            iconPath = self.rdyIcon

        self.ui.status_label.setPixmap(QtGui.QPixmap(iconPath).scaled(16, 16, QtCore.Qt.KeepAspectRatio))


    def setAssetListUI(self) : 
        row = 0 
        height = 20 
        widget = 'tableWidget'
        assetInfo = self.getAssetInfo()

        for eachItem in sorted(assetInfo.keys()) : 
            oID = assetInfo[eachItem]['oID']
            assetName = assetInfo[eachItem]['assetName']
            assetPath = assetInfo[eachItem]['assetPath']
            user = assetInfo[eachItem]['user']
            matteIDs = assetInfo[eachItem]['matteIDs']
            no = assetInfo[eachItem]['No']
            db = assetInfo[eachItem]['db']
            iconPath = self.xIcon
            statusMessage = 'Not in DB'
            color = [60, 0, 0]

            if db : 
                iconPath = self.rdyIcon
                statusMessage = 'Ready'
                color = [0, 60, 0]

            self.insertRow(row, height, widget)
            self.fillInTable(row, self.oIDCol, str(oID), widget, [1, 1, 1])
            self.fillInTable(row, self.assetCol, str(assetName), widget, [0, 0, 0])
            self.fillInTable(row, self.pathCol, assetPath, widget, [0, 0, 0])
            self.fillInTable(row, self.mIDsCol, str(matteIDs), widget, [0, 0, 0])
            self.fillInTable(row, self.noCol, str(no), widget, [0, 0, 0])
            self.fillInTableIcon(row, self.statusCol, statusMessage, iconPath, widget, color)

                

            row += 1 

        self.ui.tableWidget.resizeColumnToContents(self.pathCol)
        self.ui.tableWidget.resizeColumnToContents(self.noCol)
        self.ui.tableWidget.resizeColumnToContents(self.mIDsCol)
        self.ui.tableWidget.resizeColumnToContents(self.assetCol)



    def getAssetInfo(self) : 
        # list asset from reference
        refs = mc.file(q = True, r = True)
        rigGrp = mc.ls('*:Rig_Grp')

        assetInfo = dict()

        for eachRef in refs : 
            if pipelineTools.checkPipelinePath(eachRef, mode = 'asset') : 
                asset = entityInfo.info(eachRef)
                assetName = asset.name()
                assetPath = asset.getPath('ref')
                record = self.getObjectIDRecord(assetName)
                
                if assetName and record : 
                    oID = record[1]
                    dbAssetName = record[2]
                    dbAssetPath = record[3]
                    dbUser = record[4]
                    dbMatteRange = record[5]

                    if not assetName in assetInfo.keys() : 
                        assetInfo.update({assetName: {'db': True, 'oID': oID, 'assetName': dbAssetName, 'assetPath': dbAssetPath, 'user': dbUser, 'matteIDs': dbMatteRange, 'No': 1}})

                    else : 
                        assetInfo[assetName]['No'] += 1

                else : 
                    if not assetName in assetInfo.keys() : 
                        assetInfo.update({assetName: {'db': False, 'oID': None, 'assetName': assetName, 'assetPath': assetPath, 'user': None, 'matteIDs': None, 'No': 1}})



        return assetInfo


    # button action 

    def doCreate(self) : 
        assets = self.getDataFromSelectedRange(self.assetCol, 'tableWidget')
        selMID = self.getDataFromSelectedRange(self.mIDsCol, 'tableWidget')
        oIDs = self.getDataFromSelectedRange(self.oIDCol, 'tableWidget')

        info = self.checkMultiMatte()

        if assets : 
            for i in range(len(assets)) : 
                assetName = assets[i]

                if assetName in info.keys() : 
                    mmInfo = info[assetName]['info']

                    for mm in mmInfo : 
                        mmName = mm
                        materialId = mmInfo[mm]['materialId']
                        colors = mmInfo[mm]['color']

                        for color in colors : 
                            mID = colors[color]
                            vr.assignMultiMatte(mmName, color, int(mID), materialId)
                            
        # assign object ID 
        self.assignObjectIDCmd()

        self.checkStatus()


    def assignObjectIDCmd(self) : 
        assets = self.getDataFromSelectedRange(self.assetCol, 'tableWidget')
        oIDs = self.getDataFromSelectedRange(self.oIDCol, 'tableWidget')

        assetGrps = mc.ls('*:%s' % self.geoGrp)

        assetInfo = dict()
        for geoGrp in assetGrps : 
            attr = '%s.assetName' % geoGrp

            if mc.objExists(attr) : 
                assetName = mc.getAttr(attr)

                upperGrp = mc.listRelatives(geoGrp, p = True)

                if upperGrp : 
                    if not assetName in assetInfo.keys() : 
                        assetInfo.update({assetName: [upperGrp[0]]})

                    else : 
                        assetInfo[assetName].append(upperGrp[0])

        if assets and oIDs : 
            for i in range(len(assets)) : 
                asset = assets[i]
                oID = oIDs[i]

                if asset in assetInfo.keys() : 
                    assignGrps = assetInfo[asset]
                    
                    for eachGrp in assignGrps : 
                        self.assignObjectID(eachGrp, oID)


    def assignObjectID(self, target, objectID) : 
        """ set objectID to Rig_Grp """

        vr.addVrayObjectID(target, 1)
        mc.setAttr('%s.vrayObjectID' % target, int(objectID))
        trace('assign %s to %s' % (objectID, target))

        return True


    def checkStatus(self) : 

        info = self.checkMultiMatte()

        for eachAsset in info : 
            mms = info[eachAsset]['info']
            status = info[eachAsset]['status']
            print status

            self.setStatusAsset(eachAsset, status)


            # for mm in mms : 
            #     print mm


    def checkMultiMatte(self) : 
        assets = self.getAllData(self.assetCol, 'tableWidget')
        selMID = self.getAllData(self.mIDsCol, 'tableWidget')
        conn = sqlite3.connect(str(self.ui.db_lineEdit.text()))
        oIDs = self.getAllData(self.oIDCol, 'tableWidget')
        statuses = self.getAllData(self.statusCol, 'tableWidget')

        assetInfo = self.getAssetInfo()

        info = dict()

        if assetInfo : 
            for each in assetInfo : 
                tmpDict = dict()
                assetName = assetInfo[each]['assetName']
                ommName = assetName.split('_')[-1]
                mIDs = assetInfo[each]['matteIDs']
                oID = assetInfo[each]['oID']
                omm = 'mm_%s' % ommName
                db = assetInfo[each]['db']
                mmExists = mc.objExists(omm)
                status = True

                if db : 
                    tmpDict.update({omm: {'color': {'red': oID}, 'exists': mmExists, 'materialId': False}})
                    # vr.assignMultiMatte(omm,'red', int(oID), materialId = False)
                    if not mmExists : 
                        status = False

                    for mID in eval(mIDs) : 
                        result = self.getDbMatteID(conn, mID)

                        if result : 
                            mID = result[1]
                            color = result[2]
                            mm = result[3]

                            mmExists = mc.objExists(mm)

                            if not mm in tmpDict.keys() : 
                                tmpDict.update({mm: {'exists': mmExists, 'materialId': True, 'color': {color: mID}}})

                            else : 
                                tmpDict[mm]['color'].update({color: mID})


                            if not mmExists : 
                                satatus = False

                            # vr.assignMultiMatte(mm, color, mID, materialId = True)
                            

                        else : 
                            # look in presets 
                            if int(mID) in presets.extraPreset.keys() : 
                                result = presets.extraPreset[mID]
                                mID = int(mID)
                                color = result['color']
                                mm = result['mm']

                                mmExists = mc.objExists(mm)

                                if not mm in tmpDict.keys() : 
                                    tmpDict.update({mm: {'exists': mmExists, 'materialId': True, 'color': {color: mID}}})

                                else : 
                                    tmpDict[mm]['color'].update({color: mID})

                                if not mmExists : 
                                    status = False

                                # vr.assignMultiMatte(mm, color, mID, materialId = True)

                        # print result

                    info.update({assetName: {'info': tmpDict, 'status': status}})

        conn.close()

        return info



    def setStatusAsset(self, asset, status) : 
        allAssets = self.getAllData(self.assetCol, 'tableWidget')

        if asset in allAssets : 
            row = allAssets.index(asset)

            if status : 
                iconPath = self.okIcon
                text = 'OK'

            else : 
                iconPath = self.rdyIcon
                text = 'Ready'

            self.fillInTableIcon(row, self.statusCol, text, iconPath, 'tableWidget', [1, 1, 1])


    # connect database
    def getDbMatteID(self, conn, mID) : 
        result = db.getMatteID(conn, mID)
        info = []

        if result : 
            for each in result : 
                info.append(each)

            if len(info) == 1 : 
                return info[0]

            if len(info) > 1 : 
                trace('More than one id match %s' % mID)
                return info[0]

        
    def getObjectIDRecord(self, assetName) : 
        conn = sqlite3.connect(str(self.ui.db_lineEdit.text()))
        result = db.getAssetName(conn, assetName)
        data = []

        for each in result : 
            data.append(each)

        conn.close()

        if len(data) == 1 : 
            return data[0]

        if len(data) > 1 :
            trace('More than 1 asset match name')
            return data[0]


    def getAllDbMatteID(self) : 
        conn = sqlite3.connect(str(self.ui.db_lineEdit.text()))
        result = db.getAllMID(conn)
        ids = []

        for each in result : 
            ids.append(each[0])

        conn.close()

        return ids


    def getAllDbOId(self) : 
        conn = sqlite3.connect(str(self.ui.db_lineEdit.text()))
        result = db.getAllOID(conn)
        ids = []
        
        for each in result : 
            ids.append(each[0])

        conn.close()

        return ids


    def getAllDbMId(self) : 
        conn = sqlite3.connect(str(self.ui.db_lineEdit.text()))
        result = db.getAllOID(conn)
        ids = []
        
        for each in result : 
            ids.append(each[0])

        conn.close()

        return ids


    def runDBView(self) : 
        from tool.matte import dbViewer_app as app
        reload(app)

        myApp = app.MyForm(app.getMayaWindow())
                    

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



    # customWidget 

    def getAllItems(self) : 
        count = self.ui.preset_listWidget.count()
        itemWidgets = []
        items1 = []
        items2 = []
        items3 = []
        items4 = []

        for i in range(count) : 
            item = self.ui.preset_listWidget.item(i)

            customWidget = self.ui.preset_listWidget.itemWidget(item)
            text1 = customWidget.text1()
            text2 = customWidget.text2()
            text3 = customWidget.text3()
            text4 = customWidget.text4()

            items1.append(text1)
            items2.append(text2)
            items3.append(text3)
            items4.append(text4)
            itemWidgets.append(customWidget)


        return [items1, items2, items3, items4, itemWidgets]


    def getSelectedItem(self) : 
        item = self.ui.preset_listWidget.currentItem()

        if item : 
            customWidget = self.ui.preset_listWidget.itemWidget(item)
            text1 = customWidget.text1()
            text2 = customWidget.text2()
            text3 = customWidget.text3()
            text4 = customWidget.text4()

            return [text1, text2, text3, text4]


    def addCustomShotListWidget(self, text1 = '', text2 = '', text3 = '', text4 = '', statusColor = [40, 120, 40], bgColor = [0, 0, 0], iconPath = '', size = 16) : 
        myCustomWidget = customWidget.customQWidgetItem()
        myCustomWidget.setText1(text1)
        myCustomWidget.setText2(text2)
        myCustomWidget.setText3(text3)
        myCustomWidget.setText4(text4)

        myCustomWidget.setTextColor1([240, 240, 240])
        myCustomWidget.setTextColor2([100, 160, 200])
        myCustomWidget.setTextColor3(statusColor)
        myCustomWidget.setTextColor4([160, 160, 160])

        myCustomWidget.setIcon(iconPath, size)

        item = QtGui.QListWidgetItem(self.ui.preset_listWidget)
        item.setSizeHint(myCustomWidget.sizeHint())
        item.setBackground(QtGui.QColor(bgColor[0], bgColor[1], bgColor[2]))

        self.ui.preset_listWidget.addItem(item)
        self.ui.preset_listWidget.setItemWidget(item, myCustomWidget)



    def messageBox(self, title, description) : 
        result = QtGui.QMessageBox.question(self,title,description,QtGui.QMessageBox.Ok)

        return result



def deleteUI(ui) : 
    if mc.window(ui, exists = True) : 
        mc.deleteUI(ui)


def trace(message) : 
    mm.eval('trace "%s\\n";' % message)
    print '%s' % message
