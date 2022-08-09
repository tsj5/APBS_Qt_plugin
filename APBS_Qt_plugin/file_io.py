"""
Custom widgets for path open/save with additional validation logic.
"""
import os.path
# import pathlib # TODO
import tempfile

import logging
_log = logging.getLogger(__name__)

import util

from pymol.Qt import (QtGui, QtWidgets)
from ui.custom_path_widget_ui import Ui_CustomPathWidget

@util.attrs_define
class PathModelBase(util.PYQT_QOBJECT):
    """Base class for our Model classes.
    """
    path: str = None
    is_valid: bool = False

    def __attrs_post_init__(self):
        if self.path is None:
            # set path to temp path
            pass

    def validate(self, new_path):
        self.is_valid = True
        if self.is_valid:
            self.path = new_path

class CustomPathBaseView(QtWidgets.QGroupBox, Ui_CustomPathWidget):
    def __init__(
        self,
        widget_label = "Path to file:",
        dialog_caption = "Select path to file:",
        dialog_filter = "All files (*.*)",
        parent=None
    ):
        super(CustomPathBaseView, self).__init__(parent)
        self.setupUi(self)
        self.browse_label.setText(widget_label)
        self.dialog_caption = dialog_caption
        self.dialog_filter = dialog_filter

class CustomPathBaseController(util.PYQT_QOBJECT):
    def __init__(self, model, view, parent=None):
        super(CustomPathBaseController, self).__init__(parent)
        self.model = model
        self.view = view

        # view -> model
        self.view.browse_toolButton.clicked.connect(self.on_browse_toolButton_clicked)
        self.view.browse_lineEdit.textEdited.connect(self.on_browse_lineEdit_textEdited)

        # model -> view
        self.model.path_changed.connect(self.view.browse_lineEdit.setText)
        self.model.is_valid_changed.connect(self.on_isvalid_changed)

    @util.PYQT_SLOT(str)
    def on_browse_lineEdit_textEdited(self, new_path):
        # TODO
        pass

    @util.PYQT_SLOT(bool)
    def on_isvalid_changed(self, b):
        if b:
            self._ui.validated_label.setText(' ')
            self._ui.validated_label.setToolTip("")
        else:
            self._ui.validated_label.setText('\u26A0') # unicode caution
            self._ui.validated_label.setToolTip("The currently specified path is invalid.")

    @util.PYQT_SLOT()
    def on_browse_toolButton_clicked(self):
        raise NotImplementedError

    def get_dialog_start_dir(self):
        if self.model.is_valid:
            return os.path.dirname(self.model.path)
        else:
            # start in home directory
            return os.path.expanduser("~")

# ------------------------------------------------------------------------------

class CustomPathOpenController(CustomPathBaseController):
    @util.PYQT_SLOT()
    def on_browse_toolButton_clicked(self):
        new_path, _ = QtGui.QFileDialog.getOpenFileName(
            parent=self,
            caption=self.dialog_caption,
            dir=self.get_dialog_start_dir(),
            filter=self.dialog_filter
        )
        if new_path:
            self.model.path = new_path


# ------------------------------------------------------------------------------

@util.attrs_define
class SavePathModel(PathModelBase):
    is_tempfile: bool = True

    def __attrs_post_init__(self):
        if self.path is None:
            # set path to temp path, TODO
            pass

class CustomPathSaveController(CustomPathBaseController):
    @util.PYQT_SLOT()
    def on_browse_toolButton_clicked(self):
        new_path, _ = QtGui.QFileDialog.getSaveFileName(
            parent=self,
            caption=self.dialog_caption,
            dir=self.get_dialog_start_dir(),
            filter=self.dialog_filter
        )
        if new_path:
            self.model.path = new_path

    def open():
        # TODO
        pass
