"""
Model, view and controller representing configuration for visualizing the
calculated potential back in PyMol.
"""
import logging
_log = logging.getLogger(__name__)

import util

# ------------------------------------------------------------------------------


class VisualizationModel(util.BaseModel):
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


# ------------------------------------------------------------------------------

class VisualizationController(util.BaseController):
    def __init__(self, model, view, pymol_controller):
        super(VisualizationController, self).__init__(model, view)
        self.pymol_cmd = pymol_controller

    def ramp_name(self):
        # return 'e_lvl'
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:molecule']
        names = self.pymol_cmd.get_names_of_type('object:molecule')
        idx = names.index(self.model.molecule)
        return '_'.join(('e_lvl', str(idx), str(self.model.vis_group)))

    def grad_name(self):
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:molecule']
        names = self.pymol_cmd.get_names_of_type('object:molecule')
        idx = names.index(self.model.molecule)
        return '_'.join(('grad', str(idx), str(self.model.vis_group)))

    def positive_iso_name(self):
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:map']
        names = self.pymol_cmd.get_names_of_type('object:map')
        idx = names.index(self.model.map_name)
        return '_'.join(('iso_pos', str(idx), str(self.model.vis_group)))

    def negative_iso_name(self):
        # [i for i in self.pymol_cmd.get_names() if self.pymol_cmd.get_type(i) == 'object:map']
        names = self.pymol_cmd.get_names_of_type('object:map')
        idx = names.index(self.model.map_name)
        return '_'.join(('iso_neg', str(idx), str(self.model.vis_group)))

    def updateRamp(self):
        ramp_name = self.ramp_name()
        surf_range = [self.model.mol_surf_low, self.model.mol_surf_mid, self.model.mol_surf_hi]
        _log.debug(" APBS Tools: range is", surf_range)
        self.pymol_cmd.delete(ramp_name)
        self.pymol_cmd.ramp_new(ramp_name, self.model.map_name, surf_range)
        self.pymol_cmd.set('surface_color', ramp_name, self.model.molecule)

    def showMolSurface(self):
        self.updateMolSurface()

    def hideMolSurface(self):
        self.pymol_cmd.hide('surface', self.model.molecule)

    def updateMolSurface(self):
        molecule_name = self.model.molecule
        self.updateRamp()
        if self.model.surface_solvent == 1:
            self.pymol_cmd.set('surface_solvent', 1, molecule_name)
            self.pymol_cmd.set('surface_ramp_above_mode', 0, molecule_name)
        else:
            self.pymol_cmd.set('surface_solvent', 0, molecule_name)
            self.pymol_cmd.set('surface_ramp_above_mode', self.model.potential_at_sas, molecule_name)
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
        self.pymol_cmd.isosurface(surf_name, self.model.map_name, self.model.pos_surf_val)
        self.pymol_cmd.color('blue', surf_name)
        self.pymol_cmd.show('everything', surf_name)

    def showNegSurface(self):
        self.updateNegSurface()

    def hideNegSurface(self):
        self.pymol_cmd.hide('everything', self.negative_iso_name())

    def updateNegSurface(self):
        surf_name = self.negative_iso_name()
        self.pymol_cmd.delete(surf_name)
        self.pymol_cmd.isosurface(surf_name, self.map.getvalue(), self.model.neg_surf_val)
        self.pymol_cmd.color('red', surf_name)
        self.pymol_cmd.show('everything', surf_name)

    def showFieldLines(self):
        self.updateFieldLines()

    def hideFieldLines(self):
        self.pymol_cmd.hide('everything', self.grad_name())

    def updateFieldLines(self):
        grad_name = self.grad_name()
        _log.debug("updateFieldLines: IN update")
        self.pymol_cmd.gradient(grad_name, self.model.map_name)
        _log.debug("updateFieldLines: Made gradient")
        self.updateRamp()
        _log.debug("updateFieldLines: Updated ramp")
        self.pymol_cmd.color(self.ramp_name(), grad_name)
        _log.debug("updateFieldLines: set colors")
        self.pymol_cmd.show('mesh', grad_name)
