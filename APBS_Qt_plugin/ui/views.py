"""
View classes. Need to be in the ui package so that pyuic-generated imports work.
"""

from pymol.Qt import (QtCore, QtGui, QtWidgets)

from .pqr_groupBox_ui import Ui_pqr_GroupBox
from .apbs_groupBox_ui import Ui_apbs_GroupBox
from .viz_groupBox_ui import Ui_viz_GroupBox

# ------------------------------------------------------------------------------
# GroupBoxes

class PQRGroupBoxView(QtWidgets.QGroupBox, Ui_pqr_GroupBox):
    def __init__(self, parent=None):
        super(PQRGroupBoxView, self).__init__(parent)
        self.setupUi(self)

        # checkbox enables/disables dependent widgets
        self.pqr_prepare_mol_checkBox.clicked.connect(self.on_prepare_mol_update)

        # combobox changes pane of stackedwidget
        self.pqr_method_comboBox.activated.connect(
            self.pqr_method_stackedWidget.setCurrentIndex
        )

    @QtCore.pyqtSlot(bool)
    def on_prepare_mol_update(self, b):
        # enable/diable dependent controls
        for w in (
            self.pqr_method_stackedWidget,
            self.pqr_method_comboBox
        ):
            w.setEnabled(b)
            w.setDisabled(not b) # difference?

class APBSGroupBoxView(QtWidgets.QGroupBox, Ui_apbs_GroupBox):
    def __init__(self, parent=None):
        super(APBSGroupBoxView, self).__init__(parent)
        self.setupUi(self)

class VizGroupBoxView(QtWidgets.QGroupBox, Ui_viz_GroupBox):
    def __init__(self, parent=None):
        super(VizGroupBoxView, self).__init__(parent)
        self.setupUi(self)

