"""
Model, view and controller for grid generation configuration.
"""
import dataclasses as dc
import logging
import math
import pathlib

_log = logging.getLogger(__name__)

import pymol.Qt.QtCore as QtCore
import util

@dc.dataclass
class BaseGridModelData(util.BaseModelData):
    """Fields defining config state shared by all GridModels.
    """
    coarse_dim: float
    fine_dim: float
    fine_grid_points: float
    center: float

    grid_coarse_x: float
    grid_coarse_y: float
    grid_coarse_z: float
    grid_fine_x: float
    grid_fine_y: float
    grid_fine_z: float
    grid_center_x: float
    grid_center_y: float
    grid_center_z: float
    grid_points_x: float
    grid_points_y: float
    grid_points_z: float

@dc.dataclass
class PSizeGridModelData(BaseGridModelData):
    """Fields defining config state for generating APBS grid parameters using
    psize.py (provided as part of APBS.)
    """
    psize_path: pathlib.Path
class PSizeGridModel(
    QtCore.QObject, PSizeGridModelData, metaclass = util.DataclassDescriptorMetaclass
):
    """Config state for generating APBS grid parameters using psize.py (provided
    as part of APBS.)
    """
    pass

@dc.dataclass
class PluginGridModelData(BaseGridModelData):
    """Fields defining config state for generating APBS grid parameters using
    the plugin's logic.
    """
    pass
class PluginGridModel(
    QtCore.QObject, PluginGridModelData, metaclass = util.DataclassDescriptorMetaclass
):
    """Config state for generating APBS grid parameters using the plugin's logic.
    """
    pass

class MultiGridModel(QtCore.QObject):
    """Wrapper for all PQRModel states, and user selection of PQR file generation
    method.
    """
    _grid_multimodel_index_changed = QtCore.pyqtSignal(int)

    def __init__(self):
        self.grid_multimodel_index = util.SignalWrapper("grid_multimodel_index", default=0)
        self._model_state = (
            PSizeGridModel(),
            PluginGridModel()
        )

    def __getattr__(self, name):
        """Pass through all attribute access to the currently selected PQRModel.
        """
        return getattr(self._model_state[self.grid_multimodel_index], name)

    def __setattr__(self, name, value):
        """Pass through all attribute access to the currently selected PQRModel.
        """
        setattr(self._model_state[self.grid_multimodel_index], name, value)

# ----------------------------------



class BaseGridController():
    """Logic used in all GridControllers.
    """

    def memofgrid(finegridpoints):
        return 200. * float(finegridpoints[0] * finegridpoints[1] * finegridpoints[2]) / 1024. / 1024

    def gridofmem(mem):
        return mem * 1024. * 1024. / 200.

    def correct_finegridpoints(self):
        max_mem_allowed = float(self.max_mem_allowed.getvalue())
        max_grid_points = gridofmem(max_mem_allowed)
        _log.info("Estimated memory usage", memofgrid(finegridpoints) 'MB out of maximum allowed', max_mem_allowed)
        if memofgrid(finegridpoints) < max_mem_allowed:
            return # no correction needed

        _log.warning("Maximum memory usage exceeded.  Old grid dimensions were", finegridpoints)
        product = float(finegridpoints[0] * finegridpoints[1] * finegridpoints[2])
        factor = pow(max_grid_points / product, 0.333333333)
        finegridpoints[0] = (int(factor * finegridpoints[0] / 2)) * 2 + 1
        finegridpoints[1] = (int(factor * finegridpoints[1] / 2)) * 2 + 1
        finegridpoints[2] = (int(factor * finegridpoints[2] / 2)) * 2 + 1
        _log.info("Fine grid points rounded down from", finegridpoints)
        #
        # Now we have to make sure that this still fits the equation n = c*2^(l+1) + 1.  Here, we'll
        # just assume nlev == 4, which means that we need to be (some constant times 32) + 1.
        #
        # This can be annoying if, e.g., you're trying to set [99, 123, 99] .. it'll get rounded to [99, 127, 99].
        # First, I'll try to round to the nearest 32*c+1.  If that doesn't work, I'll just round down.
        #
        new_gp = [0, 0, 0]
        for i in 0, 1, 2:
            dm = divmod(finegridpoints[i] - 1, 32)
            if dm[1] > 16:
                new_gp[i] = (dm[0] + 1) * 32 + 1
            else:
                new_gp[i] = (dm[0]) * 32 + 1
        new_prod = new_gp[0] * new_gp[1] * new_gp[2]
        # print "tried new_prod",new_prod,"max_grid_points",max_grid_points,"small enough?",new_prod <= max_grid_points
        if new_prod <= max_grid_points:
            # print "able to round to closest"
            for i in 0, 1, 2:
                finegridpoints[i] = new_gp[i]
        else:
            # darn .. have to round down.
            # Note that this can still fail a little bit .. it can only get you back down to the next multiple <= what was in
            # finegridpoints.  So, if finegridpoints was exactly on a multiple, like (99,129,99), you'll get rounded down to
            # (99,127,99), which is still just a bit over the default max of 1200000.  I think that's ok.  It's the rounding error
            # from int(factor*finegridpoints ..) above, but it'll never be a huge error.  If we needed to, we could easily fix this.
            #
            # print "rounding down more"
            for i in 0, 1, 2:
                # print finegridpoints[i],divmod(finegridpoints[i] - 1,32),
                finegridpoints[i] = divmod(finegridpoints[i] - 1, 32)[0] * 32 + 1

    def update_grid_xyz(self):
        _log.info("\tcoarse grid: (%5.3f,%5.3f,%5.3f)" % tuple(coarsedim))
        self.grid_coarse_x.setvalue(coarsedim[0])
        self.grid_coarse_y.setvalue(coarsedim[1])
        self.grid_coarse_z.setvalue(coarsedim[2])
        _log.info("\tfine grid: (%5.3f,%5.3f,%5.3f)" % tuple(finedim))
        self.grid_fine_x.setvalue(finedim[0])
        self.grid_fine_y.setvalue(finedim[1])
        self.grid_fine_z.setvalue(finedim[2])
        _log.info("\tcenter: (%5.3f,%5.3f,%5.3f)" % tuple(center))
        self.grid_center_x.setvalue(center[0])
        self.grid_center_y.setvalue(center[1])
        self.grid_center_z.setvalue(center[2])
        _log.info("\tfine grid points (%d,%d,%d)" % tuple(finegridpoints))
        self.grid_points_x.setvalue(finegridpoints[0])
        self.grid_points_y.setvalue(finegridpoints[1])
        self.grid_points_z.setvalue(finegridpoints[2])

class PSizeGridController(BaseGridController):
    """Logic used when grid parameters are set via APBS's psize.py.
    """
    def import_psize(self):
        import imp
        f, fname, description = imp.find_module('psize', [os.path.split(self.psize.getvalue())[0]])
        psize = imp.load_module('psize', f, fname, description)


    def set_grid_params(self):
        if not self.psize.valid():
            raise util.NoPsizeException
        good = self.write_PQR_file()
        if not good:
            print("Could not generate PQR file!")
            return False
        pqr_filename = self.getPqrFilename()

        sel = "((%s) or (neighbor (%s) and hydro))" % (
            self.selection.getvalue(), self.selection.getvalue())

        if pymol.cmd.count_atoms(self.selection.getvalue() + " and not alt ''") != 0:
            _log.warning("You have alternate locations for some of your atoms!")
        # pymol.cmd.save(pqr_filename,sel) # Pretty sure this was a bug. No need to write it when it's externally generated.
        f.close()

        size = psize.Psize()
        size.setConstant('gmemceil', int(self.max_mem_allowed.getvalue()))
        size.runPsize(pqr_filename)
        coarsedim = size.getCoarseGridDims()  # cglen
        finedim = size.getFineGridDims()  # fglen
        # could use procgrid for multiprocessors
        finegridpoints = size.getFineGridPoints()  # dime
        center = size.getCenter()  # cgcent and fgcent
        _log.info("APBS's psize.py was used to calculated grid dimensions")


        except util.NoPDBException:
            raise util.PluginDialogException("Please set a temporary PDB file location.")

class PluginGridController(BaseGridController):

    def set_grid_params(self):
        # First, we need to get the dimensions of the molecule
        sel = self.selection.getvalue()
        sel = f"(({sel}) or (neighbor ({sel}) and hydro))"
        model = pymol.cmd.get_model(sel)
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

        box_length = [maxs[i] - mins[i] for i in range(3)]
        center = [(maxs[i] + mins[i]) / 2.0 for i in range(3)]
        #
        # psize expands the molecular dimensions by CFAC (which defaults
        # to 1.7) for the coarse grid
        #
        CFAC = 1.7
        coarsedim = [length * CFAC for length in box_length]

        #
        # psize also does something strange .. it adds a buffer FADD to
        # the box lengths to get the fine lengths.  you'd think it'd also
        # have FFAC or CADD, but we'll mimic it here.  it also has the
        # requirement that the fine grid lengths must be <= the corase
        # grid lengths.  FADD defaults to 20.
        #
        FADD = 20
        finedim = [min(coarsedim[i], box_length[i] + FADD) for i in range(3)]

        #
        # And now the hard part .. setting up the grid points.
        # From the APBS manual at http://agave.wustl.edu/apbs/doc/html/user-guide/x594.html#dime
        # we have the formula
        # n = c*2^(l+1) + 1
        # where l is the number of levels in the MG hierarchy.  The typical
        # number of levels is 4.
        #
        nlev = 4
        mult_fac = 2 ** (nlev + 1)  # this will typically be 2^5==32
        # and c must be a non-zero integer

        # If we didn't have to be c*mult_fac + 1, this is what our grid points
        # would look like (we use the ceiling to be on the safe side .. it never
        # hurts to do too much.
        SPACE = 0.5  # default desired spacing = 0.5A
        # desired_points = [int(math.ceil(flen / SPACE)) for flen in finedim] # as integers
        desired_points = [flen / SPACE for flen in finedim]  # as floats .. use int(math.ceil(..)) later

        # Now we set up our cs, taking into account mult_fac
        # (we use the ceiling to be on the safe side .. it never hurts to do
        # too much.)
        cs = [int(math.ceil(dp / mult_fac)) for dp in desired_points]

        finegridpoints = [mult_fac * c + 1 for c in cs]


        _log.info("This plugin was used to calculated grid dimensions")
        _log.info("cs: ", cs)
        _log.info("finedim: ", finedim)
        _log.info("nlev: ", nlev)
        _log.info("mult_fac: ", mult_fac)
        _log.info("finegridpoints: ", finegridpoints)

# ------------------------------------------------------------------------------