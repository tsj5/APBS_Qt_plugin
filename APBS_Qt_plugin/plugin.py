"""
Top-level plugin state and logic.
"""
import logging
_log = logging.getLogger(__name__)

from pymol.Qt import QtWidgets
from .ui.plugin_dialog_ui import Ui_plugin_dialog
from . import (pymol_api, pqr, apbs, visualization, util)

# ------------------------------------------------------------------------------
# Models

@util.attrs_define
class PluginModel(util.BaseModel):
    pqr_model: util.BaseModel
    apbs_model: util.BaseModel
    viz_model: util.BaseModel

    @util.PYQT_SLOT()
    def run(self):
        """Run the full calculation.
        """
        # TODO: exception handling!!
        try:
            self.pqr_model.write_PQR_file()
            self.apbs_model.write_APBS_input_file(self.pqr_model.pqr_out_file, self.grid_model)
            self.apbs_model.run_apbs()
            self.apbs_model.load_apbs_map()
            self.viz_model.update()
        except Exception as exc:
            raise util.PluginDialogException from exc

# ------------------------------------------------------------------------------
# Views

class PluginView(QtWidgets.QDialog, Ui_plugin_dialog):
    def __init__(self, parent=None):
        super(PluginView, self).__init__(parent)
        self.setupUi(self)

# ------------------------------------------------------------------------------
# Controllers

class PluginController(util.BaseController):
    def __init__(self):
        super(PluginController, self).__init__()
        self.view = PluginView() # initializes groupBoxes

        # init all dependent controllers:
        self.pymol_controller = pymol_api.PyMolController(
            view = self.view.selection_comboBox
        )
        self.pqr_controller = pqr.PQRController(
            pymol_controller = self.pymol_controller,
            view = self.view.pqr_groupBox
        )
        self.abps_controller = apbs.APBSGroupBoxController(
            pymol_controller = self.pymol_controller,
            view = self.view.apbs_groupBox
        )
        self.viz_controller = visualization.VizGroupBoxController(
            pymol_controller = self.pymol_controller,
            view = self.view.viz_groupBox
        )

        self.model = PluginModel(
            pqr_model = self.pqr_controller.model,
            apbs_model = self.abps_controller.model,
            viz_model = self.viz_controller.model
        )
        self.view.run_button.clicked.connect(self.model.run)
        self.model.refresh()

    def show(self):
        self.view.show()
