"""
Top-level plugin state and logic.
"""
import logging
_log = logging.getLogger(__name__)

import pymol
from pymol.Qt.QtWidgets import QDialog
from ui.plugin_dialog_ui import Ui_plugin_dialog
import pqr, grid, apbs, visualization, util

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
    def __init__(self):
        super(PluginController, self).__init__()
        self.model = PluginModel()
        self.view = PluginView() # initializes groupBoxes
        util.connect_slot(self.view.run_button.clicked, self.run)

        # now init all dependent controllers:

        self.pymol_controller = pymol.PyMolController(
            view = self.view.selection_comboBox
        )

        self.pqr_controller = pqr.PQRController(
            pymol_controller = self.pymol_controller,
            view = self.view.pqr_groupBox
        )

        self.grid_controller = grid.GridController(
            pymol_controller = self.pymol_controller
        )

        self.abps_controller = apbs.APBSGroupBoxController(
            view = self.view.apbs_groupBox
        )

        self.viz_controller = visualization.VizGroupBoxController(
            pymol_controller = self.pymol_controller,
            view = self.view.viz_groupBox
        )

        # init view from model values
        self.model.refresh()

    @util.PYQT_SLOT
    def run(self):
        """Run the full calculation.
        """
        # TODO
        pass