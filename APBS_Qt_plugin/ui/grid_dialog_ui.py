# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'grid_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import pymol.Qt.QtCore as QtCore
import pymol.Qt.QtGui as QtGui
import pymol.Qt.QtWidgets as QtWidgets

class Ui_grid_dialog(object):
    def setupUi(self, grid_dialog):
        grid_dialog.setObjectName("grid_dialog")
        grid_dialog.resize(446, 432)
        self.gridLayout_2 = QtWidgets.QGridLayout(grid_dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(grid_dialog)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.use_custom_checkBox = QtWidgets.QCheckBox(grid_dialog)
        self.use_custom_checkBox.setObjectName("use_custom_checkBox")
        self.gridLayout.addWidget(self.use_custom_checkBox, 1, 0, 1, 1, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.dialog_buttons = QtWidgets.QDialogButtonBox(grid_dialog)
        self.dialog_buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.dialog_buttons.setObjectName("dialog_buttons")
        self.gridLayout.addWidget(self.dialog_buttons, 4, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(grid_dialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setTextFormat(QtCore.Qt.PlainText)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.auto_method_comboBox = QtWidgets.QComboBox(self.groupBox)
        self.auto_method_comboBox.setEnabled(False)
        self.auto_method_comboBox.setObjectName("auto_method_comboBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.auto_method_comboBox)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setTextFormat(QtCore.Qt.PlainText)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.memory_lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.memory_lineEdit.setEnabled(False)
        self.memory_lineEdit.setObjectName("memory_lineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.memory_lineEdit)
        self.calculate_button = QtWidgets.QPushButton(self.groupBox)
        self.calculate_button.setEnabled(False)
        self.calculate_button.setObjectName("calculate_button")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.calculate_button)
        self.gridLayout_3.addLayout(self.formLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 2, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(grid_dialog)
        self.groupBox_2.setCheckable(False)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.grid_tableWidget = QtWidgets.QTableWidget(self.groupBox_2)
        self.grid_tableWidget.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grid_tableWidget.sizePolicy().hasHeightForWidth())
        self.grid_tableWidget.setSizePolicy(sizePolicy)
        self.grid_tableWidget.setObjectName("grid_tableWidget")
        self.grid_tableWidget.setColumnCount(3)
        self.grid_tableWidget.setRowCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.grid_tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.grid_tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.grid_tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.grid_tableWidget.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.grid_tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.grid_tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.grid_tableWidget.setHorizontalHeaderItem(2, item)
        self.grid_tableWidget.horizontalHeader().setDefaultSectionSize(65)
        self.verticalLayout_2.addWidget(self.grid_tableWidget)
        self.gridLayout.addWidget(self.groupBox_2, 3, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.label_4.setBuddy(self.memory_lineEdit)

        self.retranslateUi(grid_dialog)
        QtCore.QMetaObject.connectSlotsByName(grid_dialog)

    def retranslateUi(self, grid_dialog):
        _translate = QtCore.QCoreApplication.translate
        grid_dialog.setWindowTitle(_translate("grid_dialog", "Dialog"))
        self.label.setText(_translate("grid_dialog", "Options for detailed specification of APBS grid parameters"))
        self.use_custom_checkBox.setText(_translate("grid_dialog", "Use Custom Grid"))
        self.groupBox.setTitle(_translate("grid_dialog", "Automatic Grid Generation"))
        self.label_2.setText(_translate("grid_dialog", "Method:"))
        self.label_4.setText(_translate("grid_dialog", "Memory Ceiling (MB):"))
        self.calculate_button.setText(_translate("grid_dialog", "Calculate"))
        self.groupBox_2.setTitle(_translate("grid_dialog", "Grid Parameters"))
        item = self.grid_tableWidget.verticalHeaderItem(0)
        item.setText(_translate("grid_dialog", "Coarse Grid"))
        item = self.grid_tableWidget.verticalHeaderItem(1)
        item.setText(_translate("grid_dialog", "Fine Grid"))
        item = self.grid_tableWidget.verticalHeaderItem(2)
        item.setText(_translate("grid_dialog", "Grid Center"))
        item = self.grid_tableWidget.verticalHeaderItem(3)
        item.setText(_translate("grid_dialog", "Grid Points"))
        item = self.grid_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("grid_dialog", "x"))
        item = self.grid_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("grid_dialog", "y"))
        item = self.grid_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("grid_dialog", "z"))
