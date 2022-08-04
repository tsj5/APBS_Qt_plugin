"""
Custom widgets for path open/save with additional validation logic.

"""

import logging
import pathlib

_log = logging.getLogger(__name__)

import util
import pymol.Qt.QtCore as QtCore
import pymol.Qt.QtGui as QtGui
import pymol.Qt.QtWidgets as QtWidgets

from ui.custom_path_widget_ui import Ui_CustomPathWidget

@util.attrs_define
class PathModel(QtCore.QObject):
    """Base class for our Model classes.
    """
    pass

class CustomPathBase(QtWidgets.QGroupBox):
    path_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(CustomPathBase, self).__init__(parent)
        self._ui = Ui_CustomPathWidget()
        self._ui.setupUi(self)

    def setupUi(self,
            widget_label="",

        ):
        self._ui.browse_label.setText(str(label_text))

    # to be auto-connected

    @QtCore.pyqtSlot()
    def on_browse_lineEdit_textEdited(self, str_):
        pass

    # to be connected by controller

    @QtCore.pyqtSlot(bool)
    def on_validated_changed(self, b):
        if b:
            self._ui.validated_label.setText(' ')
        else:
            self._ui.validated_label.setText('\u26A0') # unicode caution

    @QtCore.pyqtSlot(str)
    def on_path_changed(self, path):
        self._ui.browse_lineEdit.setText(path)

class CustomPathOpen(CustomPathBase):

    def setupUi(self,
            widget_label="",

        ):
        self._ui.browse_label.setText(str(label_text))

    # to be auto-connected

    @QtCore.pyqtSlot()
    def on_browse_toolButton_clicked(self):
        new_path, _ = QtGui.QFileDialog.getOpenFileName(
            parent=self,
            caption='Open file',
            dir='.',
            filter='Kicad PCB Files (*.kicad_pcb)'
        )
        if new_path:
            self._model.

class CustomPathSave(CustomPathBase):
    def setupUi(self,

        ):
        self._ui.validated_label.setText(' ') # assume valid
        self._ui.browse_label.setText(str(label_text))


    @QtCore.pyqtSlot()
    def on_browse_toolButton_clicked(self):
        new_path, _ = QtGui.getSaveFileName(
            parent=self,
            caption='Select output file',
            dir='.',
            filter='Kicad PCB Files (*.kicad_pcb)'
        )
        if new_path:
            self._model.


