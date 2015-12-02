# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'O:\systemTool\python\lightTools\matteTool\importUI.ui'
#
# Created: Wed Dec 02 13:26:53 2015
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from qtshim import QtCore, QtGui
from qtshim import Signal
from qtshim import wrapinstance


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_importMatteTool(object):
    def setupUi(self, importMatteTool):
        importMatteTool.setObjectName(_fromUtf8("importMatteTool"))
        importMatteTool.resize(545, 534)
        self.centralwidget = QtGui.QWidget(importMatteTool)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_7 = QtGui.QLabel(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_4.addWidget(self.label_7, 2, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_4.addWidget(self.label_6, 1, 0, 1, 1)
        self.dbFile2_lineEdit = QtGui.QLineEdit(self.frame)
        self.dbFile2_lineEdit.setObjectName(_fromUtf8("dbFile2_lineEdit"))
        self.gridLayout_4.addWidget(self.dbFile2_lineEdit, 2, 1, 1, 1)
        self.dbFile_lineEdit = QtGui.QLineEdit(self.frame)
        self.dbFile_lineEdit.setObjectName(_fromUtf8("dbFile_lineEdit"))
        self.gridLayout_4.addWidget(self.dbFile_lineEdit, 1, 1, 1, 1)
        self.project_comboBox = QtGui.QComboBox(self.frame)
        self.project_comboBox.setMaximumSize(QtCore.QSize(160, 16777215))
        self.project_comboBox.setObjectName(_fromUtf8("project_comboBox"))
        self.gridLayout_4.addWidget(self.project_comboBox, 0, 1, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout_4)
        self.id_tableWidget = QtGui.QTableWidget(self.frame)
        self.id_tableWidget.setMinimumSize(QtCore.QSize(220, 0))
        self.id_tableWidget.setObjectName(_fromUtf8("id_tableWidget"))
        self.id_tableWidget.setColumnCount(5)
        self.id_tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.id_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.id_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.id_tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.id_tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.id_tableWidget.setHorizontalHeaderItem(4, item)
        self.verticalLayout_4.addWidget(self.id_tableWidget)
        self.selected_checkBox = QtGui.QCheckBox(self.frame)
        self.selected_checkBox.setObjectName(_fromUtf8("selected_checkBox"))
        self.verticalLayout_4.addWidget(self.selected_checkBox)
        self.refresh_pushButton = QtGui.QPushButton(self.frame)
        self.refresh_pushButton.setMinimumSize(QtCore.QSize(0, 30))
        self.refresh_pushButton.setObjectName(_fromUtf8("refresh_pushButton"))
        self.verticalLayout_4.addWidget(self.refresh_pushButton)
        self.create_pushButton = QtGui.QPushButton(self.frame)
        self.create_pushButton.setMinimumSize(QtCore.QSize(0, 30))
        self.create_pushButton.setObjectName(_fromUtf8("create_pushButton"))
        self.verticalLayout_4.addWidget(self.create_pushButton)
        self.horizontalLayout_4.addLayout(self.verticalLayout_4)
        self.horizontalLayout_4.setStretch(0, 1)
        self.verticalLayout.addWidget(self.frame)
        importMatteTool.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(importMatteTool)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 545, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        importMatteTool.setMenuBar(self.menubar)

        self.retranslateUi(importMatteTool)
        QtCore.QMetaObject.connectSlotsByName(importMatteTool)

    def retranslateUi(self, importMatteTool):
        importMatteTool.setWindowTitle(QtGui.QApplication.translate("importMatteTool", "Import MatteID Window", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("importMatteTool", "DB Prop file : ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("importMatteTool", "Project : ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("importMatteTool", "DB file : ", None, QtGui.QApplication.UnicodeUTF8))
        item = self.id_tableWidget.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("importMatteTool", "status", None, QtGui.QApplication.UnicodeUTF8))
        item = self.id_tableWidget.horizontalHeaderItem(1)
        item.setText(QtGui.QApplication.translate("importMatteTool", "Asset", None, QtGui.QApplication.UnicodeUTF8))
        item = self.id_tableWidget.horizontalHeaderItem(2)
        item.setText(QtGui.QApplication.translate("importMatteTool", "ObjectID", None, QtGui.QApplication.UnicodeUTF8))
        item = self.id_tableWidget.horizontalHeaderItem(3)
        item.setText(QtGui.QApplication.translate("importMatteTool", "MatteID Range", None, QtGui.QApplication.UnicodeUTF8))
        item = self.id_tableWidget.horizontalHeaderItem(4)
        item.setText(QtGui.QApplication.translate("importMatteTool", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.selected_checkBox.setText(QtGui.QApplication.translate("importMatteTool", "Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh_pushButton.setText(QtGui.QApplication.translate("importMatteTool", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.create_pushButton.setText(QtGui.QApplication.translate("importMatteTool", "Create Object / MatteID", None, QtGui.QApplication.UnicodeUTF8))

