"""
Model, view and controller for grid generation configuration.
"""
import os
import logging
import math
import pathlib

_log = logging.getLogger(__name__)

import util

# ------------------------------------------------------------------------------
# Models

@util.attrs_define
class GridBaseModel(util.BaseModel):
    """Config state shared by all GridModels.
    """
    coarse_dim: list
    fine_dim: list
    fine_grid_points: list
    center: list

    max_mem_allowed: int = 2500

@util.attrs_define
class GridPSizeModel(GridBaseModel):
    """Config state for generating APBS grid parameters using psize.py (provided
    as part of APBS.)
    """
    pass

@util.attrs_define
class GridPluginModel(GridBaseModel):
    """Config state for generating APBS grid parameters using the plugin's logic.
    """
    pass

# ------------------------------------------------------------------------------
# Controllers

_FLOAT_MB = 1024. * 1024.

class BaseGridController(util.BaseController):
    """Logic used in all GridControllers.
    """
    def __init__(self, model, view, pymol_controller):
        super(BaseGridController, self).__init__(model, view)
        self.pymol_cmd = pymol_controller

    @staticmethod
    def product_of_elts(vec):
        # return functools.reduce(operator.mul, vec)
        return vec[0] * vec[1] * vec[2]

    def grid_to_mem(self, grid_pts):
        return 200. * float(self.product_of_elts(grid_pts)) / _FLOAT_MB

    @staticmethod
    def mem_to_grid(mem):
        return int(mem * _FLOAT_MB / 200.)

    def correct_fine_grid(self):
        """Coarsen fine grid if current value would use too much memory, as set
        by `max_mem_allowed`. `fine_grid_pts` is a 3-vector of `int`s.
        """
        fine_grid_pts = self.model.fine_grid_pts
        max_mem_allowed = self.model.max_mem_allowed

        max_grid_points = self.mem_to_grid(max_mem_allowed)
        _log.info(f"Estimated memory usage: {self.grid_to_mem(fine_grid_pts)} "
            f"MB out of maximum allowed: {max_mem_allowed}")
        if self.grid_to_mem(fine_grid_pts) < max_mem_allowed:
            return fine_grid_pts # no correction needed

        _log.warning(f"Maximum memory usage exceeded. Old grid dimensions: {fine_grid_pts}")
        factor = pow(
            float(max_grid_points / self.product_of_elts(fine_grid_pts)),
            0.333333333
        )
        fine_grid_pts = [(int(factor * x / 2)) * 2 + 1 for x in fine_grid_pts]
        _log.info(f"Fine grid points rounded down to: {fine_grid_pts}")

        # Now we have to make sure that this still fits the equation n = c*2^(l+1) + 1.
        # Here, we'll just assume nlev == 4, which means that we need to be
        # (some constant times 32) + 1.
        # This can be annoying if, e.g., you're trying to set [99, 123, 99] ..
        # it'll get rounded to [99, 127, 99]. First, I'll try to round to the
        # nearest 32*c+1.  If that doesn't work, I'll just round down.
        new_grid_pts = [0, 0, 0]
        for i, n_pts in enumerate(fine_grid_pts):
            quot, rem = divmod(n_pts - 1, 32)
            if rem > 16:
                new_grid_pts[i] = (quot + 1) * 32 + 1
            else:
                new_grid_pts[i] = quot * 32 + 1
        if self.product_of_elts(new_grid_pts) <= max_grid_points:
            # print "able to round to closest"
            fine_grid_pts = new_grid_pts
        else:
            # Have to round down.
            # Note that this can still fail a little bit .. it can only get you back
            # down to the next multiple <= what was in fine_grid_pts.  So, if fine_grid_pts
            # was exactly on a multiple, like (99,129,99), you'll get rounded down to
            # (99,127,99), which is still just a bit over the default max of 1200000.
            # I think that's ok.  It's the rounding error from int(factor*fine_grid_pts ..)
            # above, but it'll never be a huge error.  If we needed to, we could easily fix this.

            # print "rounding down more"
            fine_grid_pts = [((x-1)//32) * 32 + 1 for x in new_grid_pts]
        return fine_grid_pts

    def update_grid_xyz(self, coarse_dim, fine_dim, center, fine_grid_pts):
        _log.info("\tcoarse grid: (%5.3f,%5.3f,%5.3f)" % tuple(coarse_dim))
        _log.info("\tfine grid: (%5.3f,%5.3f,%5.3f)" % tuple(fine_dim))
        _log.info("\tcenter: (%5.3f,%5.3f,%5.3f)" % tuple(center))
        _log.info("\tfine grid points (%d,%d,%d)" % tuple(fine_grid_pts))

class GridPSizeController(BaseGridController):
    """Logic used when grid parameters are set via APBS's psize.py.
    """
    _model_class = GridPSizeModel # autogenerate on_*_changed Slots

    def import_psize(self):
        import imp
        f, fname, description = imp.find_module('psize', [os.path.split(self.psize.getvalue())[0]])
        psize = imp.load_module('psize', f, fname, description)

    def set_grid_params(self):
        if not self.psize.valid():
            raise util.NoPsizeException

        sel = self.pymol_cmd.model.selection # NB not pymol_selection
        if self.pymol_cmd.count_atoms(sel + " and not alt ''") != 0:
            _log.warning("You have alternate locations for some of your atoms!")

        pqr_filename = self.getPqrFilename()
        size = psize.Psize()
        size.setConstant('gmemceil', self.model.max_mem_allowed)
        size.runPsize(pqr_filename)
        coarse_dim = size.getCoarseGridDims()  # cglen
        fine_dim = size.getFineGridDims()  # fglen
        # could use procgrid for multiprocessors
        fine_grid_pts = size.getFineGridPoints()  # dime
        center = size.getCenter()  # cgcent and fgcent
        _log.info("APBS's psize.py was used to calculated grid dimensions")

        fine_grid_pts = self.correct_fine_grid()
        self.update_grid_xyz(coarse_dim, fine_dim, center, fine_grid_pts)


class GridPluginController(BaseGridController):
    _model_class = GridPluginModel # autogenerate on_*_changed Slots

    def set_grid_params(self):
        # First, we need to get the dimensions of the molecule
        sel = self.pymol_cmd.pymol_selection
        model = self.pymol_cmd.get_model(sel)
        mins = [None, None, None]
        maxs = [None, None, None]
        for a in model.atom:
            for i in (0, 1, 2):
                if mins[i] is None or (a.coord[i] - a.elec_radius) < mins[i]:
                    mins[i] = a.coord[i] - a.elec_radius
                if maxs[i] is None or (a.coord[i] + a.elec_radius) > maxs[i]:
                    maxs[i] = a.coord[i] + a.elec_radius
        if None in mins or None in maxs:
            raise util.PluginDialogException("No atoms were in your selection.")

        box_length = [max_ - min_ for min_, max_ in zip(mins, maxs)]
        center = [(max_ + min_) / 2.0 for min_, max_ in zip(mins, maxs)]

        # psize expands the molecular dimensions by CFAC (which defaults
        # to 1.7) for the coarse grid.
        CFAC = 1.7
        coarse_dim = [length * CFAC for length in box_length]

        # psize also does something strange .. it adds a buffer FADD to
        # the box lengths to get the fine lengths. You'd think it'd also
        # have FFAC or CADD, but we'll mimic it here. It also has the
        # requirement that the fine grid lengths must be <= the corase
        # grid lengths. FADD defaults to 20.
        FADD = 20
        fine_dim = [min(cdim, length + FADD) for cdim, length in zip(coarse_dim, box_length)]

        # And now the hard part .. setting up the grid points.
        # From the APBS manual at http://agave.wustl.edu/apbs/doc/html/user-guide/x594.html#dime
        # we have the formula
        # n = c*2^(l+1) + 1
        # where l is the number of levels in the MG hierarchy.  The typical
        # number of levels is 4.
        nlev = 4
        mult_fac = 2 ** (nlev + 1)  # this will typically be 2^5==32
        # and c must be a non-zero integer

        # If we didn't have to be c*mult_fac + 1, this is what our grid points
        # would look like (we use the ceiling to be on the safe side .. it never
        # hurts to do too much.
        SPACE = 0.5  # default desired spacing = 0.5A
        desired_points = [flen / SPACE for flen in fine_dim]

        # Now we set up our cs, taking into account mult_fac
        # (we use the ceiling to be on the safe side .. it never hurts to do
        # too much.)
        cs = [int(math.ceil(pts / mult_fac)) for pts in desired_points]
        fine_grid_pts = [mult_fac * c + 1 for c in cs]

        _log.info("This plugin was used to calculated grid dimensions")
        _log.info("cs: ", cs)
        _log.info("fine_dim: ", fine_dim)
        _log.info("nlev: ", nlev)
        _log.info("mult_fac: ", mult_fac)
        _log.info("fine_grid_pts: ", fine_grid_pts)

        fine_grid_pts = self.correct_fine_grid()
        self.update_grid_xyz(coarse_dim, fine_dim, center, fine_grid_pts)

# ------------------------------------------------------------------------------