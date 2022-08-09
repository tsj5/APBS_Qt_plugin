"""
Model, view and controller representing configuration for visualizing the
calculated potential back in PyMol.
"""
import logging
_log = logging.getLogger(__name__)

import pymol_api
from pymol.Qt import QtWidgets
from ui.other_viz_dialog_ui import Ui_other_viz_dialog
from ui.views import VizGroupBoxView
import util

# ------------------------------------------------------------------------------

@util.attrs_define
class VisualizationModel(util.BaseModel):
    pymol_cmd: pymol_api.PyMolModel

    vis_group: int = 1
    molecule: str = ""
    map_name: str = ""
    potential_at_sas: float = 1.
    surface_solvent: int = 0
    show_surface_for_scanning: bool = True
    mol_surf_low: float = 0.0
    mol_surf_mid: float = 0.0
    mol_surf_hi: float = 0.0
    pos_surf_val: float = 0.0
    neg_surf_val: float = 0.0

    def ramp_name(self):
        # return 'e_lvl'
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:molecule']
        names = self.pymol_cmd.get_names_of_type('object:molecule')
        idx = names.index(self.molecule)
        return '_'.join(('e_lvl', str(idx), str(self.vis_group)))

    def grad_name(self):
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:molecule']
        names = self.pymol_cmd.get_names_of_type('object:molecule')
        idx = names.index(self.molecule)
        return '_'.join(('grad', str(idx), str(self.vis_group)))

    def positive_iso_name(self):
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:map']
        names = self.pymol_cmd.get_names_of_type('object:map')
        idx = names.index(self.map_name)
        return '_'.join(('iso_pos', str(idx), str(self.vis_group)))

    def negative_iso_name(self):
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:map']
        names = self.pymol_cmd.get_names_of_type('object:map')
        idx = names.index(self.map_name)
        return '_'.join(('iso_neg', str(idx), str(self.vis_group)))

    def updateRamp(self):
        ramp_name = self.ramp_name()
        surf_range = [self.mol_surf_low, self.mol_surf_mid, self.mol_surf_hi]
        _log.debug(" APBS Tools: range is", surf_range)
        self.pymol_cmd.delete(ramp_name)
        self.pymol_cmd.ramp_new(ramp_name, self.map_name, surf_range)
        self.pymol_cmd.set('surface_color', ramp_name, self.molecule)

    def showMolSurface(self):
        self.updateMolSurface()

    def hideMolSurface(self):
        self.pymol_cmd.hide('surface', self.molecule)

    def updateMolSurface(self):
        molecule_name = self.molecule
        self.updateRamp()
        if self.surface_solvent == 1:
            self.pymol_cmd.set('surface_solvent', 1, molecule_name)
            self.pymol_cmd.set('surface_ramp_above_mode', 0, molecule_name)
        else:
            self.pymol_cmd.set('surface_solvent', 0, molecule_name)
            self.pymol_cmd.set('surface_ramp_above_mode', self.potential_at_sas, molecule_name)
        self.pymol_cmd.show('surface', molecule_name)
        self.pymol_cmd.refresh()
        self.pymol_cmd.recolor(molecule_name)

    def showPosSurface(self):
        self.updatePosSurface()

    def hidePosSurface(self):
        self.pymol_cmd.hide('everything', self.positive_iso_name())

    def updatePosSurface(self):
        surf_name = self.positive_iso_name()
        self.pymol_cmd.delete(surf_name)
        self.pymol_cmd.isosurface(surf_name, self.map_name, self.pos_surf_val)
        self.pymol_cmd.color('blue', surf_name)
        self.pymol_cmd.show('everything', surf_name)

    def showNegSurface(self):
        self.updateNegSurface()

    def hideNegSurface(self):
        self.pymol_cmd.hide('everything', self.negative_iso_name())

    def updateNegSurface(self):
        surf_name = self.negative_iso_name()
        self.pymol_cmd.delete(surf_name)
        self.pymol_cmd.isosurface(surf_name, self.map.getvalue(), self.neg_surf_val)
        self.pymol_cmd.color('red', surf_name)
        self.pymol_cmd.show('everything', surf_name)

    def showFieldLines(self):
        self.updateFieldLines()

    def hideFieldLines(self):
        self.pymol_cmd.hide('everything', self.grad_name())

    def updateFieldLines(self):
        grad_name = self.grad_name()
        _log.debug("updateFieldLines: IN update")
        self.pymol_cmd.gradient(grad_name, self.map_name)
        _log.debug("updateFieldLines: Made gradient")
        self.updateRamp()
        _log.debug("updateFieldLines: Updated ramp")
        self.pymol_cmd.color(self.ramp_name(), grad_name)
        _log.debug("updateFieldLines: set colors")
        self.pymol_cmd.show('mesh', grad_name)

# ------------------------------------------------------------------------------
# Views

class VizDialogView(QtWidgets.QDialog, Ui_other_viz_dialog):
    def __init__(self, parent=None):
        super(VizDialogView, self).__init__(parent)
        self.setupUi(self)

        # connect OK/cancel
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.rejected.connect(self.reject)

# ------------------------------------------------------------------------------
# Controller

class VizDialogController(util.BaseController):
    def __init__(self, model):
        super(VizDialogController, self).__init__()
        self.model = model
        self.view = VizDialogView()

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

    @util.PYQT_SLOT
    def exec_(self):
        self.view.exec_()

class VizGroupBoxController(util.BaseController):
    def __init__(self, pymol_controller=None, view=None):
        super(VizGroupBoxController, self).__init__()
        if pymol_controller is None:
            raise ValueError
        self.model = VisualizationModel(
            pymol_cmd = pymol_controller.model.pymol_instance
        )
        self.dialog_controller = VizDialogController(self.model)
        if view is None:
            self.view = VizGroupBoxView()
        else:
            self.view = view

        util.connect_slot(self.view.other_viz_options_button.clicked, self.dialog_controller.exec_)

        util.biconnect(self.view.apbs_calculate_checkBox, self.model, XXX)
        util.biconnect(self.view.apbs_focus_lineEdit, self.model, XXX)
        util.biconnect(self.view.apbs_outputmap_lineEdit, self.model, XXX)

        # init view from model values
        self.model.refresh()
