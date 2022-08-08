"""
Top-level plugin state and logic.
"""
import logging
_log = logging.getLogger(__name__)

import pymol
from pymol.Qt.QtWidgets import QDialog
from ui.plugin_dialog_ui import Ui_plugin_dialog
import util

# ------------------------------------------------------------------------------
# Models

class PluginModel(util.BaseModel):
    pass

# ------------------------------------------------------------------------------
# Views

class PluginView(QDialog, Ui_plugin_dialog):
    def __init__(self, parent=None):
        super(PluginView, self).__init__(parent)
        self.setupUi(self)

# ------------------------------------------------------------------------------
# Controllers

class PluginController(util.BaseController):
    def __init__(self, model, view):
        super(PluginController, self).__init__()
        self.model = model
        self.view = view

        # init everything, in reverse hierarchical order
        m_pymol = pymol.PyMolModel()
        util.biconnect(self.view.selection_comboBox, m_pymol, "sel_idx")



