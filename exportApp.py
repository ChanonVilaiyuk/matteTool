import os, sys,  shutil
import maya.mel as mm
import maya.cmds as mc

from datetime import datetime

from qtshim import QtCore, QtGui
from qtshim import Signal
from qtshim import wrapinstance

#Custom import modules
from tools import fileUtils, mayaTools, getInfo, info, calculate
reload(fileUtils)

from lightTools.matteTool import exportUI as ui
from lightTools.matteTool import mayaInfo
from lightTools.mayaVray import utils as vrayUtils
reload(ui)
reload(mayaInfo)
reload(vrayUtils)

# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is None:
        raise RuntimeError('No Maya window found.')
    window = wrapinstance(ptr)
    assert isinstance(window, QtGui.QMainWindow)
    return window

import maya.OpenMayaUI as mui
getMayaWindow()


class MyForm(QtGui.QMainWindow) : 
	def __init__(self, parent=None) : 

		# Setup Window
		super(MyForm, self).__init__(parent)
		self.ui = ui.Ui_matteTools()
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

		# column name
		self.objectIDColumn = 0
		self.assetColumn = 1
		self.userColumn = 2
		self.assetPathColumn = 3
		self.shortNameColumn = 4

		self.matteIDColumn = 0
		self.vrayMtlColumn = 1
		self.multiMatteColumn = 2
		self.colorColumn = 3

		self.initFunctions()
		self.initConnections()


	def initFunctions(self) : 
		self.settingInfo = self.readSetting()

		if self.settingInfo : 
			if self.mayaInfo : 
				self.listProject()
				self.setDbPath()
				self.listAllData()

			else : 
				self.messageBox('Error', 'Scene is not in the pipeline')

		else : 
			print 'No Setting Found, cannot continue'



	def initConnections(self) : 
		self.ui.showAll_checkBox.stateChanged.connect(self.listDataUI)
		self.ui.id_tableWidget.itemSelectionChanged.connect(self.listMatteIDUI)
		self.ui.assignMatteID_pushButton.clicked.connect(self.assignMatteId)
		self.ui.assignObjectID_pushButton.clicked.connect(self.assignObjectId)
		self.ui.createMultiMatte_pushButton.clicked.connect(self.assignMultiMatte)
		self.ui.export_pushButton.clicked.connect(self.exportDatabase)
		self.ui.clearObjectID_pushButton.clicked.connect(self.clearObjectId)
		self.ui.project_comboBox.currentIndexChanged.connect(self.listAllData)



	def readSetting(self) : 
		if os.path.exists(self.settingFile) : 
			setting = fileUtils.ymlLoader(self.settingFile)

			return setting


	def listAllData(self) : 
		self.setDbPath()
		self.readDatabase()
		self.setupUI()


	def setDbPath(self) : 
		# project = self.mayaInfo['project']
		project = str(self.ui.project_comboBox.currentText())
		dbPath =  self.settingInfo['databasePath']
		drive = self.mayaInfo['drive']

		# construct db path
		dbPath = ('/').join([drive, project, dbPath])

		self.ui.dbFile_lineEdit.setText(dbPath)

	

	def getDbPath(self) : 
		
		dbPath = str(self.ui.dbFile_lineEdit.text())

		return dbPath


	def readDatabase(self) : 

		# construct db path
		dbPath = self.getDbPath()

		if os.path.exists(dbPath) : 
			data = fileUtils.ymlLoader(dbPath)

			return data

		# not exists, create database
		else : 
			result = self.createDefaultDatabase(dbPath)
			print 'default database created'


	def createDefaultDatabase(self, dbPath) : 
		dictInfo = {0: {'assetName': 'defaultAsset', 'user': '-', 'assetPath': '-', 
					'matteId': {
							1: {'vrayMtl': 'vrayMtl1', 'color': 'red', 'multiMatte': 'Matte01'}, 
							2: {'vrayMtl': 'vrayMtl2', 'color': 'red', 'multiMatte': 'Matte02'}
								}
						
						}
					}
		dirname = os.path.dirname(dbPath)

		if not os.path.exists(dirname) : 
			os.makedirs(dirname)

		result = fileUtils.ymlDumper(dbPath, dictInfo)

		return result
		

	def getAllId(self) : 
		i = 0 
		allAssetId = []
		startRange = self.idRange[0]
		endRange = self.idRange[-1]

		calRange = range(startRange/self.idAssetRange, endRange/self.idAssetRange)

		for i in calRange : 
			allAssetId.append(i*self.idAssetRange)


		return allAssetId



	def occupiedId(self) : 
		data = self.readDatabase()
		if data : 
			occupiedIdList = [i for i in sorted(data.keys())]

			return occupiedIdList


	def availableId(self) : 
		occupiedIdList = self.occupiedId()
		allAssetId = self.getAllId()

		# if some assets occupied id
		if occupiedIdList : 
			availableId = allAssetId

			for eachId in occupiedIdList : 
				if eachId in availableId : 
					availableId.remove(eachId)

			return availableId

		# if no occupied id mean all ids are free, return allId
		else : 
			return self.allAssetId

	# UI read

	def setupUI(self) : 
		self.setBasicTableProperties()
		self.listDataUI()
		self.setMultiMatteName()
		self.setAssetName()


	def setBasicTableProperties(self) : 
		self.ui.id_tableWidget.horizontalHeader().setStretchLastSection(True)
		self.ui.matteID_tableWidget.horizontalHeader().setStretchLastSection(True)
		self.ui.assignObjectID_pushButton.setEnabled(True)
		self.ui.assignMatteID_pushButton.setEnabled(False)
		self.ui.createMultiMatte_pushButton.setEnabled(False)


	def listProject(self) : 
		drive = self.mayaInfo['drive']
		exceptions = ['.', 'test', 'system', 'archive', 'temp']
		projects = fileUtils.listFolder('%s/' % drive)
		currentProject = self.mayaInfo['project']

		# projects = [p for p in projects if not p in exceptions]

		self.ui.project_comboBox.clear()

		for each in projects : 
			for exception in exceptions : 
				if exception in each : 
					break
					
				self.ui.project_comboBox.addItem(each)
				break

		self.setComboBoxItem(currentProject, 'project_comboBox')


	def setMultiMatteName(self) : 
		assetName = self.mayaInfo['assetName']

		if self.ui.auto_checkBox.isChecked() : 
			self.ui.multiMatteName_lineEdit.setText(assetName)


	def setAssetName(self) : 
		assetName = self.mayaInfo['assetName']
		renderAssetPath = self.mayaInfo['renderAssetPath']

		if self.ui.autoName_checkBox.isChecked() : 
			self.ui.name_lineEdit.setText(assetName)
			self.ui.path_lineEdit.setText(renderAssetPath)



	def listDataUI(self) : 

		row = 0
		column = 0
		height = 20
		widget = 'id_tableWidget'
		showAll = self.ui.showAll_checkBox.isChecked()
		showId = []
		crrProject = self.mayaInfo['project']
		data = self.readDatabase()
		assetName = '-'
		user = '-'
		assetPath = '-'

		if not showAll : 
			showId = self.availableId()

		else : 
			showId = self.getAllId()


		self.clearTable(widget)

		for each in showId : 
			text = str(each)
			self.insertRow(row, height, widget)
			self.fillInTable(row, column, text, widget, color = [1, 1, 1]) 
			if int(each) in data.keys() : 
				if 'assetName' in data[int(each)].keys() : 
					assetName = data[int(each)]['assetName']
				
				if 'user' in data[int(each)].keys() : 
					user = data[int(each)]['user']

				if 'assetPath' in data[int(each)].keys() : 
					assetPath = data[int(each)]['assetPath']

				self.fillInTable(row, self.assetColumn, assetName, widget, color = [1, 60, 1])
				self.fillInTable(row, self.userColumn, user, widget, color = [1, 60, 1])
				self.fillInTable(row, self.assetPathColumn, assetPath, widget, color = [1, 60, 1])

			else : 
				self.fillInTable(row, self.assetColumn, '-', widget, color = [0, 0, 0])
				self.fillInTable(row, self.userColumn, '-', widget, color = [0, 0, 0])
				self.fillInTable(row, self.assetPathColumn, '-', widget, color = [0, 0, 0])

			row+=1

		self.ui.id_tableWidget.resizeColumnToContents(self.userColumn)
		self.ui.id_tableWidget.resizeColumnToContents(self.assetPathColumn)


	def listMatteIDUI(self) : 
		data = self.readDatabase()
		strId = self.getDataFromSelectedRange(self.objectIDColumn, 'id_tableWidget')
		assetName = self.getDataFromSelectedRange(self.assetColumn, 'id_tableWidget')
		assetPath = str()
		
		widget = 'matteID_tableWidget'
		self.clearTable(widget)


		if strId : 
			id = int(strId[0])
			if id in data.keys() : 
				self.readOnlyIdAction(id)
				
				# lock assign button
				self.ui.assignObjectID_pushButton.setEnabled(False)

				
				# set asset name and path
				assetPath = data[int(strId[0])]['assetPath']
				self.ui.name_lineEdit.setText(assetName[0])
				self.ui.path_lineEdit.setText(assetPath)

			else : 
				# id available
				self.availableIdAction(id)
				self.setAssetName()


				

				# re lock button
				self.ui.createMultiMatte_pushButton.setEnabled(False)

				if self.assignObjectIdStatus : 
					self.ui.assignObjectID_pushButton.setEnabled(False)

				else : 
					self.ui.assignObjectID_pushButton.setEnabled(True)


				self.ui.matteID_tableWidget.resizeColumnToContents(0)
				self.ui.matteID_tableWidget.resizeColumnToContents(1)


				self.startPadding = 1



	def listMultiMatteUI(self) : 
		widget = 'matteID_tableWidget'
		allMultiMattes = self.getAllData(self.multiMatteColumn, widget)
		multiMatteNames = sorted(self.removeDuplicateList(allMultiMattes))
		self.ui.multiMatte_listWidget.clear()

		for each in multiMatteNames : 
			self.ui.multiMatte_listWidget.addItem(each)



	def readOnlyIdAction(self, id) : 
		widget = 'matteID_tableWidget'

		row = 0
		height = 20

		data = self.readDatabase()

		data[id]

		for each in data[id]['matteId'] : 
			matteId = each
			color = data[id]['matteId'][matteId]['color']
			multiMatte = data[id]['matteId'][matteId]['multiMatte']
			vrayMtl = data[id]['matteId'][matteId]['vrayMtl']
			displayColor = self.colorCode(color)

			self.insertRow(row, height, widget)
			self.fillInTable(row, 0, str(matteId), widget, color = [0, 0, 0])
			self.fillInTable(row, 1, vrayMtl, widget, color = [0, 0, 0]) 
			self.fillInTable(row, 3, color, widget, displayColor) 
			self.fillInTable(row, 2, multiMatte, widget, color = [0, 0, 0]) 

			row += 1

		self.listMultiMatteUI()


	def colorCode(self, color) : 
		code = None

		if color == 'red' : 
			code = [200, 0, 0]

		if color == 'green' : 
			code = [0, 200, 0]

		if color == 'blue' : 
			code = [0, 0, 200]

		return code


	def availableIdAction(self, id) : 
		allVrayNodes = self.listVrayMtlNode()
		widget = 'matteID_tableWidget'
		if allVrayNodes : 
			row = 0
			height = 20
			color = [1, 1, 1]

			for eachNode in sorted(allVrayNodes.keys()) : 
				idColor = [100, 0, 0]
				node = eachNode
				matteId = str(id + row + 1)
				previousId = str(mc.getAttr('%s.vrayMaterialId' % node))

				# print previousId
				# print matteId

				if previousId == matteId : 
					idColor = [0, 100, 0]

				self.insertRow(row, height, widget)
				self.fillInTable(row, 1, node, widget, color) 
				self.fillInTable(row, 0, matteId, widget, idColor) 
				self.fillInTable(row, 2, '-', widget, color) 
				self.fillInTable(row, 3, '-', widget, color) 

				row += 1

	
	def createVrayProps(self, nodeName, objectId) : 
		namespace = self.settingInfo['defaultNamespace']
		rigGrp =  self.settingInfo['rigGrp']
		obj = '%s:%s' % (namespace, rigGrp)
		vrayNodeName = '%s_VrProp' % nodeName

		createNode = self.ui.createVrayObjProp_checkBox.isChecked()

		# check vrayProps exists 
		nodes = mc.listConnections(obj, d = True)
		vrayObjProps = []

		if nodes : 
			for eachNode in nodes : 
				if mc.objectType(eachNode, isType = 'VRayObjectProperties') : 
					vrayObjProps.append(eachNode) 

		if vrayObjProps : 
			mc.setAttr('%s.objectID' % vrayObjProps[0], objectId)
			print 'set ID %s to %s' % (vrayObjProps[0], objectId)

			return 1

		else : 
			if createNode : 
				node = vrayUtils.createVrayObjProperties(obj, objectId)
				result = mc.rename(node, vrayNodeName)
				print 'create vrayProp %s and set ID to %s' % (vrayNodeName, objectId)

				return 2


	# button action ===================================================================================

	def assignObjectId(self) : 
		assetName = str(self.ui.name_lineEdit.text())
		row = self.ui.id_tableWidget.currentRow()
		widget = 'id_tableWidget'
		allAssetData = self.getAllData(self.assetColumn, widget)
		allAssetId = self.getAllData(self.objectIDColumn, widget)
		allAssetPath = self.getAllData(self.assetPathColumn, widget)
		assetPath = str(self.ui.path_lineEdit.text())
		user = mc.optionVar(q = 'PTuser')

		occupiedIdList = self.occupiedId()

		text = assetName
		column = 1
		assetExists = False
		assetExistingId = 0

		# check for assigning duplicate asset
		loopRow = 0
		duplicateRow = []
		for eachAsset in allAssetData : 
			dataAssetPath = allAssetPath[loopRow]

			if eachAsset == assetName or assetPath == dataAssetPath : 
				objectId = int(allAssetId[loopRow])

				if not objectId in occupiedIdList :
					if not loopRow in duplicateRow : 
						duplicateRow.append(loopRow)

				else : 
					assetExists = True
					assetExistingId = objectId

			loopRow += 1


		# remove duplicate asset
		if duplicateRow : 
			for each in duplicateRow : 
				self.fillInTable(each, self.assetColumn, '-', widget, color = [1, 1, 1])
				self.fillInTable(each, self.userColumn, '-', widget, color = [1, 1, 1])
				self.fillInTable(each, self.assetPathColumn, '-', widget, color = [1, 1, 1])


		if not assetExists : 
			# fill data
			self.fillInTable(row, self.assetColumn, text, widget, color = [1, 1, 1])
			self.fillInTable(row, self.userColumn, user, widget, color = [1, 1, 1])
			self.fillInTable(row, self.assetPathColumn, assetPath, widget, color = [1, 1, 1])

			self.ui.assignMatteID_pushButton.setEnabled(True)
			self.ui.createMultiMatte_pushButton.setEnabled(False)
			self.ui.assignObjectID_pushButton.setEnabled(False)

			self.ui.id_tableWidget.resizeColumnToContents(self.userColumn)
			self.ui.id_tableWidget.resizeColumnToContents(self.assetPathColumn)

			self.assignObjectIdStatus = True

		else : 
			self.messageBox('Asset already exists', '"%s" or "%s" already in database. id "%s".' % (assetName, assetPath, assetExistingId))

			if self.ui.vrayProp_checkBox.isChecked() : 
				self.createVrayProps(assetName, assetExistingId)


	def clearObjectId(self) : 
		widget = 'id_tableWidget'
		selAsset = self.getDataFromSelectedRange(self.assetColumn, widget)
		selId = int(self.getDataFromSelectedRange(self.objectIDColumn, widget)[0])
		currentRow = self.ui.id_tableWidget.currentRow()

		occupiedIdList = self.occupiedId()
		currentData = self.readDatabase()
		allId = self.getAllId()

		# if this item is in database, ask to remove
		if selId in occupiedIdList : 
			dialogResult = self.confirmDialog('Confirm', 'Are you sure you want to delete this item from database?')

			if dialogResult == QtGui.QMessageBox.Ok : 
				result = self.removeData(selId)


		# if not, just remove from table
		else : 
			self.fillInTable(currentRow, self.assetColumn, '-', widget, color = [1, 1, 1])
			self.fillInTable(currentRow, self.userColumn, '-', widget, color = [1, 1, 1])
			self.fillInTable(currentRow, self.assetPathColumn, '-', widget, color = [1, 1, 1])
			self.assignObjectIdStatus = False

		self.listDataUI()
		self.ui.assignObjectID_pushButton.setEnabled(True)




	def assignMatteId(self) : 
		widget = 'matteID_tableWidget'
		vrayMtls = self.getAllData(1, widget)
		ids = self.getAllData(0, widget)

		i = 0
		for each in vrayMtls : 
			mtr = each
			id = ids[i]

			# print mtr, id

			if mc.objExists('%s.vrayMaterialId' % mtr) : 
				mc.setAttr('%s.vrayMaterialId' % mtr, int(id))

			i += 1


		self.listMatteIDUI()
		self.ui.assignMatteID_pushButton.setEnabled(True)
		self.ui.createMultiMatte_pushButton.setEnabled(True)


	def assignMultiMatte(self) : 
		column = 0
		widget = 'matteID_tableWidget'
		valid = True
		currentRow = 0

		if self.ui.auto_checkBox.isChecked() : 
			ids = self.getAllData(column, widget)

		else : 
			if self.ui.matteID_tableWidget.currentItem() : 
				ids = self.getDataFromSelectedRange(column, widget)
				rows = self.getSelectionRows(widget)
				currentRow = rows[0]

			else : 
				title = 'Error'
				message = 'Select at lease 1 item'
				self.messageBox(title, message)
				valid = False

		
		if valid : 
			multiMatteNodes = []
			multiMatteNode = str()
			multiMatteName = str(self.ui.multiMatteName_lineEdit.text())

			if ids : 
				for i in range(len(ids)) : 
					id = ids[i]
					row = i + currentRow
					column = 2

					value = i%3

					# red
					if value == 0 : 
						multiMatteNode = '%s_%02d_mm' % (multiMatteName, self.startPadding)
						multiMatteNodes.append(multiMatteNode)
						self.fillInTable(row, column, multiMatteNode, widget, color = [1, 1, 1])
						self.fillInTable(row, 3, 'red', widget, color = [100, 1, 1])
						self.startPadding += 1

					# green
					if value == 1 : 
						self.fillInTable(row, column, multiMatteNode, widget, color = [1, 1, 1])
						self.fillInTable(row, 3, 'green', widget, color = [1, 100, 1])

					# blue
					if value == 2 : 
						self.fillInTable(row, column, multiMatteNode, widget, color = [1, 1, 1])
						self.fillInTable(row, 3, 'blue', widget, color = [1, 1, 100])



				# list multimattes
				self.listMultiMatteUI()


			self.ui.matteID_tableWidget.resizeColumnToContents(2)
			self.ui.export_pushButton.setEnabled(True)



	def exportDatabase(self) : 
		# get object ID

		widget = 'id_tableWidget'
		if self.ui.id_tableWidget.currentItem() : 
			objectId = int(str(self.getDataFromSelectedRange(self.objectIDColumn, widget)[0]))
			assetName = self.getDataFromSelectedRange(self.assetColumn, widget)[0]
			user = self.getDataFromSelectedRange(self.userColumn, widget)[0]

			widget = 'matteID_tableWidget'
			matteIDs = self.getAllData(self.matteIDColumn, widget)
			vrayMtls = self.getAllData(self.vrayMtlColumn, widget)
			multiMattes = self.getAllData(self.multiMatteColumn, widget)
			colors = self.getAllData(self.colorColumn, widget)

			assetPath = str(self.ui.path_lineEdit.text())


			# loop through data
			i = 0
			matteIdDict = dict()

			for i in range(len(matteIDs)) : 
				matteID = int(matteIDs[i])
				vrayMtl = vrayMtls[i]
				multiMatte = multiMattes[i]
				color = colors[i]

				matteIdDict[matteID] = {'vrayMtl': vrayMtl, 'color': color, 'multiMatte': multiMatte}

			currentData = self.readDatabase()

			# check if it does not have this id in database already

			if not objectId in currentData.keys() : 
				result = self.writeData(objectId, assetName, user, assetPath, matteIdDict)

				# create vray object properties
				result2 = self.createVrayProps(assetName, objectId)
				messageAdd = str()

				if result2 == 1 : 
					messageAdd = '\nand Set objectID success'

				if result2 == 2 : 
					messageAdd = '\nand Create VRayObjectProperties and set objectID success'

				if result : 
					title = 'Success'
					message = '%s with id : %s was successfully saved in database.' % (assetName, objectId)

					if messageAdd : 
						message+= messageAdd

					self.messageBox(title, message)

					self.listDataUI()

					self.ui.export_pushButton.setEnabled(False)



	def writeData(self, id, assetName, user, assetPath, matteIdDict) : 
		# data structure
		'''
		dictInfo = {0: {'assetName': 'defaultAsset', 'assetPath': assetPath, matteId': {
					1: {'vrayMtl': 'vrayMtl1', 'color': 'red', 'multiMatte': 'Matte01'}, 
					2: {'vrayMtl': 'vrayMtl2', 'color': 'red', 'multiMatte': 'Matte02'}}}}
		'''

		# assign current data
		writeBackData = self.readDatabase()

		writeBackData.update({id: {'assetName': assetName, 'assetPath': assetPath, 'user': user, 'matteId': matteIdDict}})

		dbPath = self.getDbPath()

		result = fileUtils.ymlDumper(dbPath, writeBackData)

		return result


	def removeData(self, id) : 
		currentData = self.readDatabase()
		dbPath = self.getDbPath()

		if id in currentData.keys() : 
			del currentData[id]

			result = fileUtils.ymlDumper(dbPath, currentData)

			return result


	def listVrayMtlNode(self) : 
		nodes = mc.ls(type = 'VRayMtl') + mc.ls(type = 'VRayBlendMtl')
		vrayNode = dict()

		for eachNode in nodes : 
			attr = '%s.vrayMaterialId' % eachNode

			if not mc.objExists(attr) : 
				mm.eval('vray addAttributesFromGroup %s vray_material_id 1' % eachNode)

			id = mc.getAttr('%s.vrayMaterialId' % eachNode)

			vrayNode[eachNode] = id


		return vrayNode


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


	def removeDuplicateList(self, inputList) : 
		newList = []

		for each in inputList : 
			if not each in newList : 
				newList.append(each)

		return newList


	def messageBox(self, title, description) : 
		result = QtGui.QMessageBox.question(self,title,description,QtGui.QMessageBox.Ok)

		return result


	def confirmDialog(self, title, description) : 
		result = QtGui.QMessageBox.question(self,title,description,QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)

		return result


	def choiceDialog(self, title, description) : 
		result = QtGui.QMessageBox.question(self,title,description,QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

		return result





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
