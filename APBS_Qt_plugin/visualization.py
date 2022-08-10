"""
Model, view and controller representing configuration for visualizing the
calculated potential back in PyMol.
"""
import logging
_log = logging.getLogger(__name__)

from . import pymol_api, util
from pymol.Qt import QtWidgets
from .ui.other_viz_dialog_ui import Ui_other_viz_dialog
from .ui.views import VizGroupBoxView

# ------------------------------------------------------------------------------

@util.attrs_define
class VisualizationModel(util.BaseModel):
    pymol_cmd: pymol_api.PyMolModel

    do_mol_viz: bool = True
    do_other_viz: bool = False
    vis_group: int = 1 # TODO - needs widget
    molecule: str = "" # TODO - needs widget
    map_name: str = "" # TODO - needs widget
    potential_at_sas: float = 1. # TODO - needs widget
    surface_solvent: bool = False # TODO - needs widget
    show_surface_for_scanning: bool = True # TODO - needs widget
    mol_surf: float = 0.0
    show_pos_iso: bool = False
    pos_surf_val: float = 0.0
    pos_surf_color: str = 'blue'
    show_neg_iso: bool = False
    neg_surf_val: float = 0.0
    neg_surf_color: str = 'red'
    show_fieldlines: bool = False


    @property # allow to set manually?
    def ramp_name(self):
        # return 'e_lvl'
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:molecule']
        names = self.pymol_cmd.get_names_of_type('object:molecule')
        idx = names.index(self.molecule)
        return '_'.join(('e_lvl', str(idx), str(self.vis_group)))

    def updateRamp(self):
        ramp_name = self.ramp_name
        surf_range = [- self.mol_surf, 0.0, self.mol_surf]
        _log.debug(" APBS Tools: range is", surf_range)
        self.pymol_cmd.delete(ramp_name)
        self.pymol_cmd.ramp_new(ramp_name, self.map_name, surf_range)
        self.pymol_cmd.set('surface_color', ramp_name, self.molecule)

    @util.PYQT_SLOT(bool)
    def on_do_mol_viz_update(self, b):
        if b:
            self.updateMolSurface()
        else:
            self.pymol_cmd.hide('surface', self.molecule)

    def updateMolSurface(self):
        molecule_name = self.molecule
        self.updateRamp()
        if self.surface_solvent:
            self.pymol_cmd.set('surface_solvent', 1, molecule_name)
            self.pymol_cmd.set('surface_ramp_above_mode', 0, molecule_name)
        else:
            self.pymol_cmd.set('surface_solvent', 0, molecule_name)
            self.pymol_cmd.set('surface_ramp_above_mode', self.potential_at_sas, molecule_name)
        self.pymol_cmd.show('surface', molecule_name)
        self.pymol_cmd.refresh()
        self.pymol_cmd.recolor(molecule_name)

# ------------------------------------

    @property # allow to set manually?
    def positive_iso_name(self):
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:map']
        names = self.pymol_cmd.get_names_of_type('object:map')
        idx = names.index(self.map_name)
        return '_'.join(('iso_pos', str(idx), str(self.vis_group)))

    @util.PYQT_SLOT(bool)
    def on_show_pos_iso_update(self, b):
        if b:
            self.do_other_viz = True
            self.updatePosSurface()
        else:
            self.pymol_cmd.hide('everything', self.positive_iso_name)
            if not self.show_neg_iso and not self.show_fieldlines:
                self.do_other_viz = False

    def updatePosSurface(self):
        surf_name = self.positive_iso_name()
        self.pymol_cmd.delete(surf_name)
        self.pymol_cmd.isosurface(surf_name, self.map_name, self.pos_surf_val)
        self.pymol_cmd.color(self.pos_surf_color, surf_name)
        self.pymol_cmd.show('everything', surf_name)


# ------------------------------------

    @property # allow to set manually?
    def negative_iso_name(self):
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:map']
        names = self.pymol_cmd.get_names_of_type('object:map')
        idx = names.index(self.map_name)
        return '_'.join(('iso_neg', str(idx), str(self.vis_group)))

    @util.PYQT_SLOT(bool)
    def on_show_neg_iso_update(self, b):
        if b:
            self.do_other_viz = True
            self.updateNegSurface()
        else:
            self.pymol_cmd.hide('everything', self.negative_iso_name)
            if not self.show_pos_iso and not self.show_fieldlines:
                self.do_other_viz = False

    def updateNegSurface(self):
        surf_name = self.neg_iso_name
        self.pymol_cmd.delete(surf_name)
        self.pymol_cmd.isosurface(surf_name, self.map.getvalue(), self.neg_surf_val)
        self.pymol_cmd.color(self.neg_surf_color, surf_name)
        self.pymol_cmd.show('everything', surf_name)


# ------------------------------------

    @property # allow to set manually?
    def grad_name(self):
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:molecule']
        names = self.pymol_cmd.get_names_of_type('object:molecule')
        idx = names.index(self.molecule)
        return '_'.join(('grad', str(idx), str(self.vis_group)))

    @util.PYQT_SLOT(bool)
    def on_show_fieldlines_update(self, b):
        if b:
            self.do_other_viz = True
            self.updateFieldLines()
        else:
            self.pymol_cmd.hide('everything', self.grad_name)
            if not self.show_pos_iso and not self.show_neg_iso:
                self.do_other_viz = False

    def updateFieldLines(self):
        grad_name = self.grad_name
        _log.debug("updateFieldLines: IN update")
        self.pymol_cmd.gradient(grad_name, self.map_name)
        _log.debug("updateFieldLines: Made gradient")
        self.updateRamp()
        _log.debug("updateFieldLines: Updated ramp")
        self.pymol_cmd.color(self.ramp_name, grad_name)
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

        util.biconnect(self.view.pos_iso_checkBox, self.model, "show_pos_iso")
        util.biconnect(self.view.pos_iso_doubleSpinBox, self.model, "pos_surf_val")
        util.biconnect(self.view.pos_iso_color_lineEdit, self.model, "pos_surf_color")

        util.biconnect(self.view.neg_iso_checkBox, self.model, "show_neg_iso")
        util.biconnect(self.view.neg_iso_doubleSpinBox, self.model, "neg_surf_val")
        util.biconnect(self.view.neg_iso_color_lineEdit, self.model, "neg_surf_color")

        util.biconnect(self.view.fieldlines_checkBox, self.model, "show_fieldlines")
        # TODO: fieldlines_ramp_lineEdit

        # init view from model values
        self.model.refresh()

    @util.PYQT_SLOT()
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

        util.biconnect(self.view.viz_surface_checkBox, self.model, "do_mol_viz")
        util.biconnect(self.view.viz_range_doubleSpinBox, self.model, "mol_surf")

        util.biconnect(self.view.other_viz_checkBox, self.model, "do_other_viz")
        self.view.other_viz_options_button.clicked.connect(self.dialog_controller.exec_)

        # init view from model values
        self.model.refresh()
