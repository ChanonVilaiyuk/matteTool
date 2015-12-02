import os, sys, shutil
import maya.mel as mm
import maya.cmds as mc

from datetime import datetime
# from PyQt4 import QtCore, QtGui

# #Import GUI
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *

from qtshim import QtCore, QtGui
from qtshim import Signal
from qtshim import wrapinstance

#Custom import modules
from tools import fileUtils, mayaTools, getInfo, info, calculate
reload(fileUtils)

from lightTools.matteTool import importUI as ui 
from lightTools.matteTool import mayaInfo
from lightTools.mayaVray import utils as vrayUtils
reload(ui)
reload(mayaInfo)
reload(vrayUtils)

import maya.OpenMayaUI as mui

# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is None:
        raise RuntimeError('No Maya window found.')
    window = wrapinstance(ptr)
    assert isinstance(window, QtGui.QMainWindow)
    return window


class MyForm(QtGui.QMainWindow) : 
	def __init__(self, parent=None) : 

		# Setup Window
		super(MyForm, self).__init__(parent)
		self.ui = ui.Ui_importMatteTool()
		self.ui.setupUi(self)

		self.settingFile = 'O:/systemTool/python/lightTools/matteTool/setting.yml'
		self.settingInfo = dict()
		self.mayaInfo = mayaInfo.sceneInfo()
		self.idRange = [0, 10000]
		self.idAssetRange = 20
		self.allAssetId = []
		self.startPadding = 1
		self.setItemStatus = False
		self.assignObjectIdStatus = False
		self.createMatteInfo = []

		# column name
		self.statusColumn = 0
		self.assetColumn = 1
		self.objectIDColumn = 2
		self.matteIdRange = 3
		self.assetPathColumn = 4

		self.matteIDColumn = 0
		self.vrayMtlColumn = 1
		self.multiMatteColumn = 2
		self.colorColumn = 3

		self.initFunctions()
		self.initConnections()


	def initFunctions(self) : 
		self.settingInfo = self.readSetting()

		if self.settingInfo : 
			self.setupUI()
		# 	self.listProject()
		# 	self.setDbPath()
		# 	self.listAllData()

		else : 
			self.messageBox('Error', 'No database file, Cannot continue')



	def initConnections(self) : 
		self.ui.refresh_pushButton.clicked.connect(self.setupUI)
		self.ui.project_comboBox.currentIndexChanged.connect(self.refreshUI)
		self.ui.create_pushButton.clicked.connect(self.doCreate)



	def readSetting(self) : 
		if os.path.exists(self.settingFile) : 
			setting = fileUtils.ymlLoader(self.settingFile)

			return setting


	def setupUI(self) : 
		self.listProject()
		self.refreshUI()



	def refreshUI(self) : 
		self.setDbPath()
		self.listObjectUI()


	def listProject(self) : 
		if self.mayaInfo : 
			drive = self.mayaInfo['drive']
			currentProject = self.mayaInfo['project']

		else : 
			drive = 'P:'
			currentProject = ''

		exceptions = ['.', 'test', 'system', 'archive', 'temp']
		projects = fileUtils.listFolder('%s/' % drive)

		self.ui.project_comboBox.clear()

		for each in projects : 
			for exception in exceptions : 
				if exception in each : 
					break
					
				self.ui.project_comboBox.addItem(each)
				break

		self.setComboBoxItem(currentProject, 'project_comboBox')


	def setDbPath(self) : 
		# project = self.mayaInfo['project']
		project = str(self.ui.project_comboBox.currentText())
		dbPath =  self.settingInfo['databasePath']
		dbPath2 =  self.settingInfo['databasePath2']
		drive = 'P:'
		
		if self.mayaInfo : 
			drive = self.mayaInfo['drive']

		# construct db path
		dbPath = ('/').join([drive, project, dbPath])
		dbPath2 = ('/').join([drive, project, dbPath2])

		self.ui.dbFile_lineEdit.setText(dbPath)
		self.ui.dbFile2_lineEdit.setText(dbPath2)

	

	def getDbPath(self, db = 1) : 
		
		if db == 1 : 
			dbPath = str(self.ui.dbFile_lineEdit.text())

		if db == 2 : 
			dbPath = str(self.ui.dbFile2_lineEdit.text())

		return dbPath


	def readDatabase(self, db = 1) : 

		# construct db path
		if db == 1 : 
			dbPath = self.getDbPath(1)

		if db == 2 : 
			dbPath = self.getDbPath(2)

		if os.path.exists(dbPath) : 
			data = fileUtils.ymlLoader(dbPath)

			return data

	# data part ===================================================================================

	''' translate data from database 

	matteIds = {'multiMatte01': [0, 1, 2], 'multiMatte02': [3, 4]}
	info = {assetPath : {'assetName': assetName, 'objectId': objectId, 'matteIds': matteIdInfo}}

	'''

	def getDataInfo(self, db = 1) : 
		info = dict()

		if db == 1 : 
			data = self.readDatabase(1)

			if data : 
				for eachId in data.keys() : 
					objectId = eachId
					path = data[eachId]['assetPath']

					matteIds = data[eachId]['matteId']

					assetName = data[eachId]['assetName']
					matteIdInfo = dict()

					for matteId in matteIds : 
						multiMatte = matteIds[matteId]['multiMatte']

						if multiMatte in matteIdInfo.keys() : 
							matteIdInfo[multiMatte].append(matteId)

						else : 
							matteIdInfo.update({multiMatte: [matteId]})


					info[path] = {'assetName': assetName, 'objectId': objectId, 'matteIds': matteIdInfo}


				return info

		if db == 2 : 
			data = self.readDatabase(2)

			if data : 
				for eachId in data.keys() : 
					objectId = eachId
					path = data[eachId]['assetPath']
					assetName = data[eachId]['assetName']
					matteIdInfo = None

					info[path] = {'assetName': assetName, 'objectId': objectId, 'matteIds': matteIdInfo}


				return info




	# button command =============================================================================

	def doCreate(self) : 

		# create multiMatte
		multiMattes = []
		for eachInfo in self.createMatteInfo : 
			for assetName in eachInfo.keys() : 
				eachAsset = eachInfo[assetName]

				for eachMatte in eachAsset : 
					matteName = eachMatte
					ids = eachAsset[eachMatte]
					enableMaterialId = True

					if not mc.objExists(matteName) : 

						multiMatteNode = vrayUtils.createMultiMatte(matteName, enableMaterialId, ids)
						multiMattes.append(multiMatteNode)

					else : 
						print '%s exists, skip create node' % matteName

				self.setStatus(assetName)
			
		# create objectMatte
		self.createObjectID()

		return multiMattes


	# ui command ==================================================================================

	def listObjectUI(self) : 
		# read from dababase 1 -> character
		info = self.getDataInfo(1)
		data = self.readDatabase(1)

		# read from database 2 -> props
		info2 = self.getDataInfo(2)
		data2 = self.readDatabase(2)

		createMatteInfo = []

		assets = self.listAllReference()
		widget = 'id_tableWidget'

		self.clearTable(widget)

		row = 0
		height = 20
		messages = []

		# if info has data
		if info and info2 : 

			for each in assets : 
				path = os.path.dirname(each)

				if path in info.keys() : 
					objectId = str(info[path]['objectId'])
					matteIds = data[int(objectId)]['matteId']
					assetName = info[path]['assetName']
					idRange = []
					matteInfo = info[path]['matteIds']
					tmpDict = dict()
					matteIdRange = '-'

					for id in matteIds : 
						idRange.append(id)


					if idRange : 
						matteIdRange = '%s-%s' % (sorted(idRange)[0], sorted(idRange)[-1])

					else : 
						messages.append('%s data not complete (objectId %s)' % (assetName, objectId))

					self.insertRow(row, height, widget)
					self.fillInTable(row, self.objectIDColumn, objectId, widget, color = [1, 1, 1]) 
					self.fillInTable(row, self.assetColumn, assetName, widget, color = [1, 100, 1]) 
					self.fillInTable(row, self.matteIdRange, matteIdRange, widget, color = [1, 1, 1]) 
					self.fillInTable(row, self.assetPathColumn, path, widget, color = [1, 1, 1]) 

					tmpDict[assetName] = matteInfo
					createMatteInfo.append(tmpDict)


				# read from props db
				elif path in info2.keys() : 
					objectId = str(info2[path]['objectId'])
					assetName = info2[path]['assetName']

					self.insertRow(row, height, widget)
					self.fillInTable(row, self.objectIDColumn, objectId, widget, color = [1, 1, 1]) 
					self.fillInTable(row, self.assetColumn, assetName, widget, color = [1, 100, 1]) 
					self.fillInTable(row, self.matteIdRange, '-', widget, color = [1, 1, 1]) 
					self.fillInTable(row, self.assetPathColumn, '-', widget, color = [1, 1, 1]) 

				# not in any database
				else : 

					# path = P:/Lego_Friends/asset/3D/character/main/frd_andreaBeach/ref
					assetName = path.split('/3D/')[-1].split('/')[2]
					self.insertRow(row, height, widget)
					self.fillInTable(row, self.objectIDColumn, '-', widget, color = [1, 1, 1]) 
					self.fillInTable(row, self.assetColumn, assetName, widget, color = [100, 1, 1]) 
					self.fillInTable(row, self.matteIdRange, '-', widget, color = [1, 1, 1]) 
					self.fillInTable(row, self.assetPathColumn, path, widget, color = [1, 1, 1]) 

				row += 1

			self.ui.id_tableWidget.horizontalHeader().setStretchLastSection(True)

			# make global var to pass this to doCreate function
			self.createMatteInfo = createMatteInfo

			if messages : 
				message = 'There are some error, please check\n'
				message += ('\n').join(messages)
				title = 'Error'
				description = message
				self.messageBox(title, description)



	def setStatus(self, asset) : 
		widget = 'id_tableWidget'
		okIcon = self.settingInfo['okIcon']
		naIcon = self.settingInfo['naIcon']
		allData = self.getAllData(self.assetColumn, widget)
		text = ''

		i = 0 
		row = 0
		for each in allData : 
			if asset == each : 
				row = i

			i+= 1 

		self.fillInTableIcon(row, self.statusColumn, text, okIcon, widget, color = [1, 1, 1])
		self.ui.id_tableWidget.resizeColumnToContents(self.statusColumn)
		QtGui.QApplication.processEvents()


	# vray command ================================================================================
	
	def createObjectID(self) : 
		widget = 'id_tableWidget'
		assets = self.getAllData(self.assetColumn, widget)
		objectIds = self.getAllData(self.objectIDColumn, widget)

		i = 0
		count = 1
		multiMatte = None
		enableMaterialId = False

		for eachId in objectIds : 
			if not eachId == '-' : 
				# channel = i%3
				channel = 0
				assetName = assets[i]

				if channel == 0 : 
					# create multiMatte node
					# TA Change this on 12-06-2015 because naming characters exceed 29 chars 
					# matteName = '%s_multiMatte' % (assetName)
					matteName = '%s_mm' % (assetName)

					if not mc.objExists(matteName) : 
						print 'createMultiMatte objectID'
						multiMatte = vrayUtils.createMultiMatte(matteName, enableMaterialId)

						# set id
						redId = int(eachId)
						mc.setAttr('%s.vray_redid_multimatte' % multiMatte, redId)

						count+=1


				# if channel == 1 : 
				# 	greenId = int(eachId)
				# 	mc.setAttr('%s.vray_greenid_multimatte' % multiMatte, greenId)


				# if channel == 2 : 
				# 	blueId = int(eachId)
				# 	mc.setAttr('%s.vray_blueid_multimatte' % multiMatte, blueId)

				self.setStatus(assetName)

			i += 1


	# maya command ================================================================================

	def listAllReference(self) : 
		return mc.file(q = True, r = True)


	# widget area =================================================================================

	def getComboBoxAllItems(self, widget) : 
		cmd = 'self.ui.%s.count()' % widget
		count = eval(cmd)

		items = []

		for i in range(count) : 
			cmd2 = 'str(self.ui.%s.itemText(i))' % widget
			text = eval(cmd2)

			items.append(text)

		return items



	def setComboBoxItem(self, itemName, widget) : 
		allItems = self.getComboBoxAllItems(widget)
		index = 0
		i = 0
		for each in allItems : 
			if each == itemName : 
				index = i
			i += 1

		cmd = 'self.ui.%s.setCurrentIndex(index)' % widget
		eval(cmd)



	# table functions

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



	def messageBox(self, title, description) : 
		result = QtGui.QMessageBox.question(self,title,description,QtGui.QMessageBox.Ok)

		return result