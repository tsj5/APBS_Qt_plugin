# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'custom_path_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from pymol.Qt import (QtCore, QtGui, QtWidgets)

class Ui_CustomPathWidget(object):
    def setupUi(self, CustomPathWidget):
        CustomPathWidget.setObjectName("CustomPathWidget")
        CustomPathWidget.resize(440, 69)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CustomPathWidget.sizePolicy().hasHeightForWidth())
        CustomPathWidget.setSizePolicy(sizePolicy)
        CustomPathWidget.setMinimumSize(QtCore.QSize(200, 60))
        self.gridLayout_2 = QtWidgets.QGridLayout(CustomPathWidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.browse_label = QtWidgets.QLabel(CustomPathWidget)
        self.browse_label.setTextFormat(QtCore.Qt.PlainText)
        self.browse_label.setObjectName("browse_label")
        self.gridLayout.addWidget(self.browse_label, 0, 0, 1, 1)
        self.browse_lineEdit = QtWidgets.QLineEdit(CustomPathWidget)
        self.browse_lineEdit.setObjectName("browse_lineEdit")
        self.gridLayout.addWidget(self.browse_lineEdit, 1, 0, 1, 3)
        self.browse_toolButton = QtWidgets.QToolButton(CustomPathWidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.browse_toolButton.setFont(font)
        self.browse_toolButton.setObjectName("browse_toolButton")
        self.gridLayout.addWidget(self.browse_toolButton, 0, 2, 1, 1)
        self.validated_label = QtWidgets.QLabel(CustomPathWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.validated_label.sizePolicy().hasHeightForWidth())
        self.validated_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.validated_label.setFont(font)
        self.validated_label.setTextFormat(QtCore.Qt.PlainText)
        self.validated_label.setObjectName("validated_label")
        self.gridLayout.addWidget(self.validated_label, 0, 1, 1, 1, QtCore.Qt.AlignRight)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.browse_label.setBuddy(self.browse_toolButton)

        self.retranslateUi(CustomPathWidget)
        QtCore.QMetaObject.connectSlotsByName(CustomPathWidget)

    def retranslateUi(self, CustomPathWidget):
        _translate = QtCore.QCoreApplication.translate
        CustomPathWidget.setWindowTitle(_translate("CustomPathWidget", "GroupBox"))
        self.browse_label.setText(_translate("CustomPathWidget", "TextLabel"))
        self.browse_toolButton.setText(_translate("CustomPathWidget", "Browse..."))
        self.validated_label.setText(_translate("CustomPathWidget", "???"))
