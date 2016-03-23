''' 
v.1.0 stable function 
v.1.1 add preset files


'''

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
from tool.utils import mayaTools, pipelineTools, fileUtils
from tool.utils import entityInfo2 as entityInfo
from tool.utils import projectInfo
from tool.utils.vray import vray_utils as vr
reload(projectInfo)
reload(vr)

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

        self.mayaUI = 'matteExportWin'
        deleteUI(self.mayaUI)

        # read .ui directly
        loader = QtUiTools.QUiLoader()
        loader.setWorkingDirectory(moduleDir)

        f = QtCore.QFile("%s/matteExport_ui.ui" % moduleDir)
        f.open(QtCore.QFile.ReadOnly)

        self.myWidget = loader.load(f, self)
        self.ui = self.myWidget

        f.close()

        self.ui.show()
        self.ui.setWindowTitle('PT Vray Matte Export v.1.1')

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
        self.rigGrp = ['Rig_Grp', 'Rig:Rig_Grp']

        # matte presets 
        self.charPresetPath = 'P:/Library/lookdev/mattePresets/charPreset'
        self.propPresetPath = 'P:/Library/lookdev/mattePresets/propPreset'
        self.presetData = dict()

        # table objectID
        self.idCol = 0 
        self.oIDCol = 1
        self.assetNameCol = 2
        self.assetPathCol = 3
        self.userCol = 4
        self.mIDsCol = 5

        # table material list 
        self.vrayMtlCol = 0 
        self.oID2Col = 1
        self.tagCol = 2
        self.statusCol = 3
        self.MultiMatteCol = 4
        self.colorCol = 5

        # table colors
        self.red = [60, 0, 0]
        self.green = [0, 60, 0]
        self.blue = [20, 40, 100]
        self.lightGreen = [40, 100, 0]

        self.colorMap = {'red': [100, 0, 0], 'green': [0, 100, 0], 'blue': [0, 0, 100], None: [0, 0, 0]}

        self.initFunctions()
        self.initSignals()


    def initFunctions(self) : 
        self.readDb()
        self.setUI()


    def initSignals(self) : 
        self.ui.project_comboBox.currentIndexChanged.connect(self.projectAction)

        # button 
        self.ui.export_pushButton.clicked.connect(self.doExport)
        self.ui.assign_pushButton.clicked.connect(self.doAssign)
        self.ui.dbView_pushButton.clicked.connect(self.runDBView)
        self.ui.auto_pushButton.clicked.connect(self.autoAssign)

        # radioButton 
        self.ui.char_radioButton.clicked.connect(self.refreshUI)
        self.ui.prop_radioButton.clicked.connect(self.refreshUI)
        self.ui.normal_checkBox.stateChanged.connect(self.refreshUI)
        self.ui.extra_checkBox.stateChanged.connect(self.refreshUI)

        # table widget 
        self.ui.tableWidget.itemSelectionChanged.connect(self.tableAction)

        # comboBox
        self.ui.preset_comboBox.currentIndexChanged.connect(self.presetComboBoxAction)


    def readDb(self) : 
        project = str(self.ui.project_comboBox.currentText())
        dbResult = db.readDatabase(project)
        self.ui.db_lineEdit.setText(db.dbPath(project))

        self.dbData = dbResult

    def setUI(self) : 
        self.customUI()
        self.setLogo()
        self.setProject()
        self.setAssetName()
        self.setMode()
        self.setPresetFiles()
        self.setPresetData()
        self.setObjectID()
        self.setVrayMtlUI()
        self.setPresets()


    def refreshUI(self) : 
        self.setMode()
        self.setPresetFiles()
        self.setPresetData()
        self.setObjectID()
        self.setVrayMtlUI()
        self.setPresets()



    def customUI(self) : 
        self.ui.save_pushButton.setVisible(False)


    def setLogo(self) : 
        self.ui.logo_label.setPixmap(QtGui.QPixmap(self.logo).scaled(200, 60, QtCore.Qt.KeepAspectRatio))
        self.ui.logo2_label.setPixmap(QtGui.QPixmap(self.logo2).scaled(126, 60, QtCore.Qt.KeepAspectRatio))


    def setMode(self) : 
        self.charPreset = self.ui.char_radioButton.isChecked()
        self.propPreset = self.ui.prop_radioButton.isChecked()
        self.normalPreset = self.ui.normal_checkBox.isChecked()
        self.extraPreset = self.ui.extra_checkBox.isChecked()


    def presetComboBoxAction(self) : 
        self.setPresetData()
        self.setObjectID()
        self.setVrayMtlUI()
        self.setPresets()


    def setPresetData(self) : 
        if self.charPreset : 
            path = self.charPresetPath
            preset = presets.charPresets

        if self.propPreset : 
            path = self.propPresetPath
            preset = presets.propPresets

        presetFile = str(self.ui.preset_comboBox.currentText())

        if presetFile : 
            filePath = '%s/%s' % (path, presetFile)

            if os.path.exists(filePath) : 
                f = open(filePath, 'r')
                data = eval(f.read())
                f.close()
                print 'preset from %s' % filePath
                self.presetData = data

                return data

        else : 
            print 'preset from presets.py'
            self.presetData = preset
            return preset


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
        projectCheck = [a.lower() for a in projects]

        if currProject.lower() in projectCheck : 
            row = projectCheck.index(currProject.lower())
            self.ui.project_comboBox.setCurrentIndex(row)
            self.readDb()

    def setAssetName(self) : 
        assetName = self.asset.name()
        self.ui.assetName_label.setText(assetName)

        # display name 
        if assetName : 
            displayName = assetName.split('_')[1]
            self.ui.display_lineEdit.setText(displayName)


    def setObjectID(self) : 
        # read database 
        assetName = str(self.ui.assetName_label.text())
        assetNameDb = self.getDbData(self.assetNameCol)

        if assetName in assetNameDb : 
            assetInfo = self.getAssetNameDb(assetName)
            assetOID = assetInfo[0][self.oIDCol]
            self.setStatus('booked')
            self.ui.id_label.setText(str(assetOID))

        else : 
            # read existing 
            dbPath = str(self.ui.db_lineEdit.text())
            avId = self.getAvailableID()
            self.ui.id_label.setText(str(avId))
            self.setStatus('ready')

    def getAvailableID(self) : 
        """ find availble ID """

        # connect to db 
        dbPath = str(self.ui.db_lineEdit.text())
        conn = sqlite3.connect(dbPath)
        data = db.queryObjectIDTable(conn)

        exIds = []

        # find existing ID 
        for each in data : 
            exIds.append(each[1])

        # get ID range 
        if self.charPreset : 
            idStart = self.objectIDStart
            idRange = self.objectIDRange
            idStep = self.objectIDStep

        if self.propPreset : 
            idStart = self.propIDStart
            idRange = self.propIDRange
            idStep = self.propIDStep

        print idStart
        print idRange
        print idStep


        allIds = [a for a in xrange(idStart, idRange, idStep)]
        avIds = [a for a in allIds if not a in exIds]
        self.avIds = avIds
        pickId = avIds[0]
        self.matteIds = [a for a in xrange((pickId + 1), (pickId + idStep), 1)]

        return pickId


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


    def setVrayMtlUI(self) : 
        vrayMtls = self.listVrayMtlNode()
        row = 0 
        height = 20 
        widget = 'tableWidget'

        presetID = self.getPresetID('dynamic')
        presetExtraID = self.getPresetID('fixed')

        dbMID = self.getAllDbMatteID()

        self.clearTable(widget)

        # store previous entry to check if there are duplicated IDs
        tmpList = [vrayMtls[a] for a in vrayMtls]

        # remove from extra ID 
        tmpList = [a for a in tmpList if not a in presetExtraID]

        # dup list 
        dupList = [k for k,v in Counter(tmpList).items() if v>1]

        for vrayMtl in vrayMtls : 
            mID = vrayMtls[vrayMtl]
            idColor = self.red
            statusColor = self.red
            status = self.wrongIDStatus
            tag = ''
            mmName = self.getPresetInfo('mm', mID)
            tag = self.getPresetInfo('tag', mID)
            color = self.getPresetInfo('color', mID)

            dbStatus = False
            presetStatus = False 
            dupStatus = False

            if mmName : 
                mmName = mmName.replace(presets.presetKey, str(self.ui.display_lineEdit.text()))  

            # if in database 
            if mID in dbMID : 
                status = self.inDb
                statusColor = self.blue

            else : 
                statusColor = self.green
                dbStatus = True

            # if in range
            if mID in presetID : 
                idColor = self.green
                presetStatus = True

            elif mID in presetExtraID : 
                idColor = self.lightGreen
                presetStatus = False
                status = self.extraPresetStatus
                statusColor = self.blue

            else : 
                statusColor = self.red

            # if id are duplicated
            if mID in dupList : 
                idColor = self.blue
                status = self.duplicatedStatus
                dupStatus = True 
                statusColor = self.red

            else : 
                dupStatus = True

            if dbStatus and presetStatus and dupStatus : 
                status = self.readyStatus
                statusColor = self.green
                

            self.insertRow(row, height, widget)
            self.fillInTable(row, self.vrayMtlCol, vrayMtl, widget, [1, 1, 1])
            self.fillInTable(row, self.oID2Col, str(mID), widget, idColor)
            self.fillInTable(row, self.tagCol, tag, widget, [0, 0, 0])
            self.fillInTable(row, self.MultiMatteCol, mmName, widget, [0, 0, 0])
            self.fillInTable(row, self.statusCol, status, widget, statusColor)
            self.fillInTable(row, self.colorCol, color, widget, self.colorMap[color])

            row += 1 

        # self.ui.tableWidget.resizeColumnToContents(self.vrayMtlCol)
        # self.ui.tableWidget.resizeColumnToContents(self.oID2Col)
        self.ui.tableWidget.resizeColumnToContents(self.tagCol)


    def listVrayMtlNode(self) : 
        """ list vray material """

        nodes = mc.ls(type = 'VRayMtl') + mc.ls(type = 'VRayBlendMtl')
        vrayNode = dict()

        for eachNode in nodes : 
            attr = '%s.vrayMaterialId' % eachNode

            if mc.listConnections(eachNode, t = 'shadingEngine') : 
                if not mc.objExists(attr) : 
                    mm.eval('vray addAttributesFromGroup %s vray_material_id 1' % eachNode)

                id = mc.getAttr('%s.vrayMaterialId' % eachNode)

                vrayNode[eachNode] = id

        return vrayNode


    def setPresets(self) : 

        # read preset 
        presets = []

        if self.normalPreset : 
            preset = self.getPreset()
            presets.append(preset)

        if self.extraPreset : 
            preset2 = self.getPreset('fixed')
            presets.append(preset2)

        # get UI info
        currentID = int(str(self.ui.id_label.text()))
        display = str(self.ui.display_lineEdit.text())
        assignVrayMID = [int(a) for a in self.getAllData(self.oID2Col, 'tableWidget')]

        # clear UI 
        self.ui.preset_listWidget.clear()

        for preset in presets : 
            for each in sorted(preset.keys()) : 
                mID = each
                tag = preset[each]['tag']
                mm = preset[each]['mm']

                icon = self.okIcon
                status = self.assignStatus
                statusColor = [40, 120, 40]

                if not mID in assignVrayMID : 
                    status = self.openStatus
                    statusColor = [120, 40, 40]
                    icon = self.redIcon
                
                self.addCustomShotListWidget(str(mID), tag, status, mm, statusColor, [0, 0, 0], icon, 16)



    def setPresetFiles(self) : 
        if self.charPreset : 
            path = self.charPresetPath

        if self.propPreset : 
            path = self.propPresetPath

        files = fileUtils.listFile(path, 'txt')

        if files : 
            self.ui.preset_comboBox.clear()
            self.ui.preset_comboBox.addItems(files)


    def getPresetID(self, mode = 'dynamic') : 
        objID = int(str(self.ui.id_label.text()))
        preset = self.getPreset(mode)
        ids = [a for a in sorted(preset.keys())]

        return ids 


    def getPresetInfo(self, key, mID) : 
        objID = int(str(self.ui.id_label.text()))
        preset = dict()

        preset1 = self.getPreset('dynamic')
        preset2 = self.getPreset('fixed')
        mIDKey = mID

        preset.update(preset1)
        preset.update(preset2)

        if mIDKey in preset.keys() : 
            result = preset[mIDKey][key]

            return result


    def getPreset(self, mode = 'dynamic') : 
        # tmpDict 
        tmpDict = dict()
        # get current ID
        currentID = int(str(self.ui.id_label.text()))
        display = str(self.ui.display_lineEdit.text())

        extraPreset = presets.extraPreset

        if self.charPreset : 
            # preset = presets.charPresets
            preset = self.presetData

        if self.propPreset : 
            # preset = presets.propPresets
            preset = self.presetData

        if mode == 'dynamic' : 
            for each in preset : 
                mID = each + currentID
                tag = preset[each]['tag']
                mm = preset[each]['mm'].replace(presets.presetKey, display)
                presetName = preset[each]['presetName']
                color = preset[each]['color']
                tmpDict.update({mID: {'tag': tag, 'mm': mm, 'presetName': presetName, 'type': 'dynamic', 'color': color}})

        if mode == 'fixed' : 
            for each in extraPreset : 
                mID = each
                tag = extraPreset[each]['tag']
                mm = extraPreset[each]['mm']
                presetName = extraPreset[each]['presetName']
                color = extraPreset[each]['color']
                tmpDict.update({mID: {'tag': tag, 'mm': mm, 'presetName': presetName, 'type': 'fixed', 'color': color}})


        return tmpDict


    # button action 

    def doExport(self) : 
        """ export to database """ 
        trace('-------  Start Export --------')

        # get data 
        dbPath = str(self.ui.db_lineEdit.text())
        conn = sqlite3.connect(dbPath)

        # get objectID data 
        oId = int(str(self.ui.id_label.text()))
        assetName = str(self.ui.assetName_label.text())
        assetPath = self.asset.getPath('ref')
        user = mc.optionVar(q = 'PTuser')

        # get matteID data
        mIDs = self.getAllData(self.oID2Col, 'tableWidget')
        statuses = self.getAllData(self.statusCol, 'tableWidget')
        multiMattes = self.getAllData(self.MultiMatteCol, 'tableWidget')
        vrayMtls = self.getAllData(self.vrayMtlCol, 'tableWidget')
        colors = self.getAllData(self.colorCol, 'tableWidget')

        # check if objectID exists in DB 
        dbOId = self.getAllDbOId()

        if not oId in dbOId : 

            # assign objectID to Rig_Grp
            self.assignObjectID()

            # filter mIDs 
            validMIDs = [int(mIDs[i]) for i in range(len(mIDs)) if statuses[i] == self.readyStatus or statuses[i] == self.extraPresetStatus]
            validMIDs = sorted(list(set(validMIDs)))

            # add objectID to database 
            db.addObjectIDValue(conn, oId, assetName, assetPath, user, str(validMIDs))

            trace('Add %s %s %s %s %s to database' % (oId, assetName, assetPath, user, str(mIDs)))

            tmpDict = dict()
            for i in range(len(mIDs)) : 
                mID = mIDs[i]
                status = statuses[i] 
                multiMatte = multiMattes[i]
                vrayMtl = vrayMtls[i]
                color = colors[i]

                if not mID in tmpDict.keys() : 
                    tmpDict.update({mID: {'mID': mID, 'status': status, 'mm': multiMatte, 'vrayMtl': [vrayMtl], 'color': color}})

                else : 
                    tmpDict[mID]['vrayMtl'].append(vrayMtl)


            for each in tmpDict.keys() : 
                mID = each 
                status = tmpDict[each]['status']
                color = tmpDict[each]['color']
                multiMatte = tmpDict[each]['mm']
                vrayMtl = tmpDict[each]['vrayMtl']

                if status == self.readyStatus : 
                    db.addMatteIDValue(conn, mID, color, multiMatte, str(vrayMtl))
                    trace('Write %s %s %s %s to Database' % (mID, color, multiMatte, vrayMtl))

                else : 
                    trace('Not export to Databse! %s %s %s %s to Database' % (mID, color, multiMatte, vrayMtl))


            conn.commit()

            self.readDb()
            self.setObjectID()
            self.setVrayMtlUI()
            trace('Export complete')
            self.messageBox('Success', 'Export ID %s to Database complete' % oId)

        else : 
            self.messageBox('Warning', 'ID %s exists in Database' % oId)

        conn.close()


    def doAssign(self) : 
        """ assign matte id to vray material """
        item = self.getSelectedItem()
        vrayMtrs = self.getDataFromSelectedRange(self.vrayMtlCol, 'tableWidget')

        if item and vrayMtrs : 

            # assign matteID 
            vrayAttr = '%s.vrayMaterialId' % vrayMtrs[0]
            mID = int(item[0])
            # result = mc.setAttr(vrayAttr, mID)
            result = self.setID(vrayAttr, mID)

            self.setVrayMtlUI()
            self.setPresets()


    def autoAssign(self) : 
        """ auto assign material from preset """
        presets = self.getPreset()
        matchs = []

        if presets : 
            for each in presets : 
                mID = each
                mtrName = presets[each]['presetName']
                match = mc.ls('%s_VRay*' % mtrName)

                if match : 
                    vrayAttr = '%s.vrayMaterialId' % match[0]

                    if mc.objExists(vrayAttr) : 
                        # result = mc.setAttr(vrayAttr, mID)
                        self.setID(vrayAttr, mID)
                        matchs.append(mtrName)

            self.setVrayMtlUI()
            self.setPresets()

        if not matchs : 
            self.messageBox('Information', 'No material match preset')



    def checkMatteIDRecord(self, matteIds) : 
        conn = sqlite3.connect(str(self.ui.db_lineEdit.text()))

        result = db.getAllMID(conn)
        rMatteIDs = [a[0] for a in result]

        allow = True
        ex = []

        for eachId in matteIds : 
            if eachId in rMatteIDs : 
                allow = False
                result = db.getMatteID(conn, eachId)

                print 'Existing record ...'

                for each in result : 
                    print each

        conn.close()

        return allow


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


    def assignObjectID(self) : 
        """ set objectID to Rig_Grp """
        currentID = int(str(self.ui.id_label.text()))

        # rig grp
        for target in self.rigGrp : 
            if mc.objExists(target) : 
                vr.addVrayObjectID(target, 1)
                # mc.setAttr('%s.vrayObjectID' % target, currentID)
                self.setID('%s.vrayObjectID' % target, currentID)

                trace('assign %s to %s' % (currentID, target))


    def setID(self, attr, value) : 
        # mc.setAttr(attr, l = False)
        mc.setAttr(attr, value)
        # mc.setAttr(attr, l = True)


    def runDBView(self) : 
        from tool.matte import dbViewer_app as app
        reload(app)

        myApp = app.MyForm(app.getMayaWindow())


    def tableAction(self) : 
        """ select object from material """
        if self.ui.select_checkBox.isChecked() : 
            mtrs = self.getDataFromSelectedRange(self.vrayMtlCol, 'tableWidget')

            sels = []

            if mtrs : 
                for each in mtrs : 
                    if mc.objExists(each) : 
                        mc.hyperShade(objects = each)
                        objs = mc.ls(sl = True)

                        for obj in objs : 
                            if not obj in sels : 
                                sels.append(obj)

                mc.select(cl = True)
                mc.select(sels)
                    

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
