# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_main_widget(object):
    def setupUi(self, main_widget):
        main_widget.setObjectName("main_widget")
        main_widget.resize(634, 857)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(main_widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtWidgets.QLabel(main_widget)
        self.label_3.setTextFormat(QtCore.Qt.PlainText)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.selection_comboBox = QtWidgets.QComboBox(main_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selection_comboBox.sizePolicy().hasHeightForWidth())
        self.selection_comboBox.setSizePolicy(sizePolicy)
        self.selection_comboBox.setEditable(True)
        self.selection_comboBox.setObjectName("selection_comboBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.selection_comboBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.pqr_frame = QtWidgets.QFrame(main_widget)
        self.pqr_frame.setObjectName("pqr_frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.pqr_frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.pqr_frame)
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.pqr_prepare_mol_checkBox = QtWidgets.QCheckBox(self.pqr_frame)
        self.pqr_prepare_mol_checkBox.setChecked(True)
        self.pqr_prepare_mol_checkBox.setObjectName("pqr_prepare_mol_checkBox")
        self.gridLayout.addWidget(self.pqr_prepare_mol_checkBox, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)
        self.pqr_output_mol_lineEdit = QtWidgets.QLineEdit(self.pqr_frame)
        self.pqr_output_mol_lineEdit.setObjectName("pqr_output_mol_lineEdit")
        self.gridLayout.addWidget(self.pqr_output_mol_lineEdit, 3, 1, 1, 2, QtCore.Qt.AlignVCenter)
        self.label_4 = QtWidgets.QLabel(self.pqr_frame)
        self.label_4.setTextFormat(QtCore.Qt.PlainText)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        self.pqr_method_stackedWidget = QtWidgets.QStackedWidget(self.pqr_frame)
        self.pqr_method_stackedWidget.setObjectName("pqr_method_stackedWidget")
        self.page_pdb2pqr = Pdb2pqrWidget()
        self.page_pdb2pqr.setObjectName("page_pdb2pqr")
        self.pqr_method_stackedWidget.addWidget(self.page_pdb2pqr)
        self.page_pymol = PqrPyMolWidget()
        self.page_pymol.setObjectName("page_pymol")
        self.pqr_method_stackedWidget.addWidget(self.page_pymol)
        self.gridLayout.addWidget(self.pqr_method_stackedWidget, 2, 0, 1, 3)
        self.pqr_method_comboBox = QtWidgets.QComboBox(self.pqr_frame)
        self.pqr_method_comboBox.setObjectName("pqr_method_comboBox")
        self.gridLayout.addWidget(self.pqr_method_comboBox, 1, 1, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.pqr_frame)
        self.apbs_frame = QtWidgets.QFrame(main_widget)
        self.apbs_frame.setObjectName("apbs_frame")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.apbs_frame)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_5 = QtWidgets.QLabel(self.apbs_frame)
        self.label_5.setTextFormat(QtCore.Qt.PlainText)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 2, 0, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.label_6 = QtWidgets.QLabel(self.apbs_frame)
        self.label_6.setTextFormat(QtCore.Qt.PlainText)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 1, 0, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.apbs_calculate_checkBox = QtWidgets.QCheckBox(self.apbs_frame)
        self.apbs_calculate_checkBox.setCheckable(True)
        self.apbs_calculate_checkBox.setChecked(True)
        self.apbs_calculate_checkBox.setObjectName("apbs_calculate_checkBox")
        self.gridLayout_3.addWidget(self.apbs_calculate_checkBox, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)
        self.apbs_outputmap_lineEdit = QtWidgets.QLineEdit(self.apbs_frame)
        self.apbs_outputmap_lineEdit.setObjectName("apbs_outputmap_lineEdit")
        self.gridLayout_3.addWidget(self.apbs_outputmap_lineEdit, 3, 1, 1, 2, QtCore.Qt.AlignVCenter)
        self.apbs_focus_lineEdit = QtWidgets.QLineEdit(self.apbs_frame)
        self.apbs_focus_lineEdit.setObjectName("apbs_focus_lineEdit")
        self.gridLayout_3.addWidget(self.apbs_focus_lineEdit, 1, 1, 1, 2, QtCore.Qt.AlignVCenter)
        self.apbs_options_button = QtWidgets.QToolButton(self.apbs_frame)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.apbs_options_button.setFont(font)
        self.apbs_options_button.setObjectName("apbs_options_button")
        self.gridLayout_3.addWidget(self.apbs_options_button, 0, 2, 1, 1, QtCore.Qt.AlignVCenter)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem1, 0, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.apbs_frame)
        self.label_7.setTextFormat(QtCore.Qt.PlainText)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 3, 0, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.apbs_finegrid_spinBox = QtWidgets.QDoubleSpinBox(self.apbs_frame)
        self.apbs_finegrid_spinBox.setObjectName("apbs_finegrid_spinBox")
        self.gridLayout_3.addWidget(self.apbs_finegrid_spinBox, 2, 1, 1, 1, QtCore.Qt.AlignVCenter)
        self.apbs_grid_options_button = QtWidgets.QToolButton(self.apbs_frame)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.apbs_grid_options_button.setFont(font)
        self.apbs_grid_options_button.setObjectName("apbs_grid_options_button")
        self.gridLayout_3.addWidget(self.apbs_grid_options_button, 2, 2, 1, 1, QtCore.Qt.AlignVCenter)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.apbs_frame)
        self.viz_frame = QtWidgets.QFrame(main_widget)
        self.viz_frame.setObjectName("viz_frame")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.viz_frame)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_2 = QtWidgets.QLabel(self.viz_frame)
        self.label_2.setTextFormat(QtCore.Qt.PlainText)
        self.label_2.setObjectName("label_2")
        self.gridLayout_5.addWidget(self.label_2, 2, 0, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem2, 0, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.viz_frame)
        self.label_8.setTextFormat(QtCore.Qt.PlainText)
        self.label_8.setObjectName("label_8")
        self.gridLayout_5.addWidget(self.label_8, 4, 0, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.viz_surface_checkBox = QtWidgets.QCheckBox(self.viz_frame)
        self.viz_surface_checkBox.setChecked(True)
        self.viz_surface_checkBox.setObjectName("viz_surface_checkBox")
        self.gridLayout_5.addWidget(self.viz_surface_checkBox, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)
        self.viz_method_comboBox = QtWidgets.QComboBox(self.viz_frame)
        self.viz_method_comboBox.setObjectName("viz_method_comboBox")
        self.gridLayout_5.addWidget(self.viz_method_comboBox, 5, 0, 1, 3, QtCore.Qt.AlignVCenter)
        self.viz_map_comboBox = QtWidgets.QComboBox(self.viz_frame)
        self.viz_map_comboBox.setEditable(True)
        self.viz_map_comboBox.setObjectName("viz_map_comboBox")
        self.gridLayout_5.addWidget(self.viz_map_comboBox, 2, 1, 1, 2, QtCore.Qt.AlignVCenter)
        self.label_9 = QtWidgets.QLabel(self.viz_frame)
        self.label_9.setTextFormat(QtCore.Qt.PlainText)
        self.label_9.setObjectName("label_9")
        self.gridLayout_5.addWidget(self.label_9, 3, 0, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.label_10 = QtWidgets.QLabel(self.viz_frame)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_10.setFont(font)
        self.label_10.setTextFormat(QtCore.Qt.RichText)
        self.label_10.setObjectName("label_10")
        self.gridLayout_5.addWidget(self.label_10, 1, 0, 1, 3, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.viz_range_spinBox = QtWidgets.QDoubleSpinBox(self.viz_frame)
        self.viz_range_spinBox.setObjectName("viz_range_spinBox")
        self.gridLayout_5.addWidget(self.viz_range_spinBox, 3, 1, 1, 1, QtCore.Qt.AlignVCenter)
        self.viz_ramp_lineEdit = QtWidgets.QLineEdit(self.viz_frame)
        self.viz_ramp_lineEdit.setObjectName("viz_ramp_lineEdit")
        self.gridLayout_5.addWidget(self.viz_ramp_lineEdit, 4, 1, 1, 2, QtCore.Qt.AlignVCenter)
        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.viz_frame)
        self.other_viz_frame = QtWidgets.QFrame(main_widget)
        self.other_viz_frame.setObjectName("other_viz_frame")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.other_viz_frame)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.other_viz_options_button = QtWidgets.QToolButton(self.other_viz_frame)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.other_viz_options_button.setFont(font)
        self.other_viz_options_button.setObjectName("other_viz_options_button")
        self.gridLayout_7.addWidget(self.other_viz_options_button, 0, 2, 1, 1, QtCore.Qt.AlignVCenter)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem3, 0, 1, 1, 1)
        self.other_viz_checkBox = QtWidgets.QCheckBox(self.other_viz_frame)
        self.other_viz_checkBox.setObjectName("other_viz_checkBox")
        self.gridLayout_7.addWidget(self.other_viz_checkBox, 0, 0, 1, 1, QtCore.Qt.AlignVCenter)
        self.gridLayout_8.addLayout(self.gridLayout_7, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.other_viz_frame)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(main_widget)
        QtCore.QMetaObject.connectSlotsByName(main_widget)

    def retranslateUi(self, main_widget):
        _translate = QtCore.QCoreApplication.translate
        main_widget.setWindowTitle(_translate("main_widget", "Form"))
        self.label_3.setText(_translate("main_widget", "Selection:"))
        self.label.setText(_translate("main_widget", "Method:"))
        self.pqr_prepare_mol_checkBox.setText(_translate("main_widget", "Prepare Molecule"))
        self.label_4.setText(_translate("main_widget", "Output Molecule Object:"))
        self.label_5.setText(_translate("main_widget", "Grid Spacing (A):"))
        self.label_6.setText(_translate("main_widget", "Focus Selection (optional):"))
        self.apbs_calculate_checkBox.setText(_translate("main_widget", "Calculate Map with APBS"))
        self.apbs_options_button.setText(_translate("main_widget", "Options..."))
        self.label_7.setText(_translate("main_widget", "Output Map Object:"))
        self.apbs_grid_options_button.setText(_translate("main_widget", "Options..."))
        self.label_2.setText(_translate("main_widget", "Map:"))
        self.label_8.setText(_translate("main_widget", "Output Ramp:"))
        self.viz_surface_checkBox.setText(_translate("main_widget", "Molecular Surface Visualization"))
        self.label_9.setText(_translate("main_widget", "Range: +/-"))
        self.label_10.setText(_translate("main_widget", "Projects the electrostatic potential onto the molecular surface"))
        self.other_viz_options_button.setText(_translate("main_widget", "Options..."))
        self.other_viz_checkBox.setText(_translate("main_widget", "Other Visualizations"))
from pdb2pqrwidget import Pdb2pqrWidget
from pqrpymolwidget import PqrPyMolWidget
