"""
Model, view and controller representing configuration for the APBS code.
"""
import os.path
import attrs
import enum
import logging
import pathlib
import string
import textwrap

_log = logging.getLogger(__name__)

from pymol.Qt import QtWidgets
from .ui.views import APBSGroupBoxView
from .ui.apbs_dialog_ui import Ui_apbs_dialog
from . import pymol_api, grid, util

# ------------------------------------------------------------------------------
# Models

# TODO - implement LabeledEnum
# ApbsModeEnum = util.LabeledEnum("ApbsModeEnum",
#     {
#         'Nonlinear Poisson-Boltzmann Equation':  'npbe',
#         'Linearized Poisson-Boltzmann Equation': 'lpbe'
#     }
# )

# BcflEnum = util.LabeledEnum("BcflEnum",
#     {
#         'Zero': 'zero',
#         'Single DH sphere': 'sdh',
#         'Multiple DH spheres': 'mdh',
#         #'Focusing': 'focus',
#     }
# )

# ChgmEnum = util.LabeledEnum("ChgmEnum",
#     {
#         'Linear': 'spl0',
#         'Cubic B-splines': 'spl2',
#         'Quintic B-splines': 'spl4',
#     }
# )

# SrfmEnum = util.LabeledEnum("SrfmEnum",
#     {
#         'Mol surf for epsilon; inflated VdW for kappa, no smoothing': 'mol',
#         'Same, but with harmonic average smoothing': 'smol',
#         'Cubic spline': 'spl2',
#         'Similar to cubic spline, but with 7th order polynomial': 'spl4'
#     }
# )

@util.attrs_define
class APBSModel(util.BaseModel):
    """Config state for options to be passed to APBS.
    """
    pymol_cmd: pymol_api.PyMolModel

    apbs_path: pathlib.Path
    apbs_config_file: pathlib.Path
    apbs_dx_file: pathlib.Path
    apbs_map_name: str

    apbs_mode: str = ""
    bcfl: str = 'Single DH sphere' # Boundary condition flag
    ion_plus_one_conc: float = 0.15
    ion_plus_one_rad: float = 2.0
    ion_plus_two_conc: float = 0.0
    ion_plus_two_rad: float = 2.0
    ion_minus_one_conc: float = 0.15
    ion_minus_one_rad: float = 1.8
    ion_minus_two_conc: float = 0.0
    ion_minus_two_rad: float = 2.0
    interior_dielectric: float = 2.0
    solvent_dielectric: float = 78.0
    chgm: str = 'Cubic B-splines'  # Charge disc method for APBS
    solvent_radius: float = 1.4
    system_temp: float = 310.0
    # sdens: Specify the number of grid points per square-angstrom to use in Vacc
    # object. Ignored when srad is 0.0 (see srad) or srfm is spl2 (see srfm). There is a direct
    # correlation between the value used for the Vacc sphere density, the accuracy of the Vacc
    # object, and the APBS calculation time. APBS default value is 10.0.
    sdens: float = 10.0
    srfm: str = ""

    @staticmethod
    def template_apbs_values(self):
        return attrs.asdict(self) # BROKEN, need to re-munge field names

    @staticmethod
    def template_grid_values(grid_model):
        return {
            'grid_coarse_x': grid_model.coarse_dim[0],
            'grid_coarse_y': grid_model.coarse_dim[1],
            'grid_coarse_z': grid_model.coarse_dim[2],
            'grid_fine_x': grid_model.fine_dim[0],
            'grid_fine_y': grid_model.fine_dim[1],
            'grid_fine_z': grid_model.fine_dim[2],
            'grid_center_x': grid_model.center[0],
            'grid_center_y': grid_model.center[1],
            'grid_center_z': grid_model.center[2],
            'grid_points_x': grid_model.fine_grid_pts[0],
            'grid_points_y': grid_model.fine_grid_pts[1],
            'grid_points_z': grid_model.fine_grid_pts[2]
        }

    def write_APBS_input_file(self, pqr_filename, grid_model):
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'apbs_input_template.txt'
        )
        if not os.path.isfile(template_path):
            raise util.PluginDialogException(f"APBS template file not found at {template_path}.")

        with open(template_path, 'r') as f:
            apbs_template = string.Template(f.read())
        _log.debug("GOT THE APBS INPUT FILE")

        if self.dx_filename.endswith('.dx'):
            self.dx_filename = self.dx_filename[:-3]

        template_dict = dict()
        template_dict.update(self.template_grid_values(grid_model))
        template_dict.update(self.template_apbs_values())

        apbs_input_text = apbs_template.substitute(template_dict)
        _log.debug("GOT THE APBS INPUT FILE")

        try:
            with open(self.apbs_config_file, 'w') as f:
                f.write(apbs_input_text)
        except Exception:
            raise util.PluginDialogException(f"Couldn't write file to  {self.apbs_config_file}.")

    def run_apbs(self):
        # TODO
        pass

    def load_apbs_map(self):
        # TODO
        pass
# ------------------------------------------------------------------------------
# Views

class APBSDialogView(QtWidgets.QDialog, Ui_apbs_dialog):
    def __init__(self, parent=None):
        super(APBSDialogView, self).__init__(parent)
        self.setupUi(self)

        # connect OK/cancel
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.rejected.connect(self.reject)

# ------------------------------------------------------------------------------
# Controller

class APBSDialogController(util.BaseController):
    def __init__(self, model):
        super(APBSDialogController, self).__init__()
        self.model = model
        self.view = APBSDialogView()

        util.biconnect(self.view.mode_comboBox, self.model, "apbs_mode")
        util.biconnect(self.view.protein_eps_lineEdit, self.model, "interior_dielectric")
        util.biconnect(self.view.solvent_eps_lineEdit, self.model, "solvent_dielectric")
        util.biconnect(self.view.solvent_r_lineEdit, self.model, "solvent_radius")
        util.biconnect(self.view.vacc_lineEdit, self.model, "sdens")
        util.biconnect(self.view.sys_temp_lineEdit, self.model, "system_temp")
        util.biconnect(self.view.bc_comboBox, self.model, "bcfl")
        util.biconnect(self.view.charge_disc_comboBox, self.model, "chgm")
        util.biconnect(self.view.surf_calc_comboBox, self.model, "srfm")

        # init view from model values
        self.model.refresh()

    @util.PYQT_SLOT()
    def exec_(self):
        self.view.exec_()

class APBSGroupBoxController(util.BaseController):
    def __init__(self,
        pymol_controller=None, view=None
    ):
        super(APBSGroupBoxController, self).__init__()
        if pymol_controller is None:
            raise ValueError
        self.model = APBSModel(
            pymol_cmd = pymol_controller.model.pymol_instance
        )
        self.dialog_controller = APBSDialogController(self.model)

        self.pymol_controller = pymol_controller
        self.grid_controller = grid.GridController(
            pymol_controller = self.pymol_controller
        )
        if view is None:
            self.view = APBSGroupBoxView()
        else:
            self.view = view

        util.connect_slot(self.view.apbs_options_button.clicked, self.dialog_controller.exec_)
        util.connect_slot(self.view.apbs_grid_options_button.clicked, self.grid_controller.exec_)

        util.biconnect(self.view.apbs_calculate_checkBox, self.model, XXX)
        util.biconnect(self.view.apbs_focus_lineEdit, self.model, XXX)
        util.biconnect(self.view.apbs_outputmap_lineEdit, self.model, XXX)

        # init view from model values
        self.model.refresh()
