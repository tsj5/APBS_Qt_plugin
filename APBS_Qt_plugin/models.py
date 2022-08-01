"""
Classes for storing config state.
"""

import dataclasses as dc
import enum
import logging
import pathlib

_log = logging.getLogger(__name__)

import pymol.Qt.QtCore as QtCore

class SignalWrapper():
    """Descriptor to automatically emit a pyqtSignal (assumed predefined)
    on change of a model attribute.
    """
    def __init__(self, name, default=None):
        self.__set_name__(None, name)
        self._default = default

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name
        self.signal_name = '_' + name + '_changed'

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self._default
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        old_value = getattr(obj, self.private_name)
        if old_value != value:
            # emit signal if we changed to different value
            getattr(obj, self.signal_name).emit(value)
        setattr(obj, self.private_name, value)

class DataclassDescriptorMetaclass(type(QtCore.QObject)):
    """Metaclass to automatically assign descriptors and pyqtSignals to all
    fields in parent dataclasses.

    Inherits from QObject's metaclass -- appears to preserve the bookkeeping
    done there. Would be more robust to do this by wrapping dataclass
    decorator, but this makes class definitions a bit more explicit.
    """
    def __new__(cls, clsname, bases, attrs):
        for base_cls in bases:
            if dc.is_dataclass(base_cls):
                for field in dc.fields(base_cls):
                    desc = SignalWrapper(field.name)
                    attrs[desc.public_name] = desc
                    attrs[desc.private_name] = (field.type)()
                    attrs[desc.signal_name] = QtCore.pyqtSignal(field.type)

        return super(DataclassDescriptorMetaclass, cls).__new__(
            cls, clsname, bases, attrs)

# ----------------------------------------------------------------------

@dc.dataclass
class BaseModelData():
    """Fields defining config state for using a pre-existing PQR file.
    """
    # signals/slots keep UI/Views in sync with Model, but we need this flag to
    # track if that config has been changed since backend state (output of
    # calculations) was last updated.
    stale: bool = True

# ----------------------------------

@dc.dataclass
class PyMolSelectionModelData(BaseModelData):
    """Fields defining config state for using a pre-existing PQR file.
    """
    selection_mode: str
    selection_hash: int
class PyMolSelectionData(
    QtCore.QObject, PyMolSelectionModelData, metaclass = DataclassDescriptorMetaclass
):
    """Config state for using a pre-existing PQR file.
    """
    pass

# ----------------------------------

@dc.dataclass
class BasePQRModelData(BaseModelData):
    """Fields defining config state shared by all PQRModels.
    """
    pqr_file: pathlib.Path
    cleanup_pqr: True

@dc.dataclass
class PreExistingPQRModelData(BasePQRModelData):
    """Fields defining config state for using a pre-existing PQR file.
    """
    pass
class PreExistingPQRModel(
    QtCore.QObject, PreExistingPQRModelData, metaclass = DataclassDescriptorMetaclass
):
    """Config state for using a pre-existing PQR file.
    """
    pass

@dc.dataclass
class PDB2PQRModelData(BasePQRModelData):
    """Fields defining config state for generating a PQR file using the pdb2pqr
    binary.
    """
    pdb2pqr_path: pathlib.Path
    pdb_file: pathlib.Path
class PDB2PQRModel(
    QtCore.QObject, PDB2PQRModelData, metaclass = DataclassDescriptorMetaclass
):
    """Config state for generating a PQR file using the pdb2pqr binary.
    """
    pass

@dc.dataclass
class PyMOLPQRExistingHModelData(BasePQRModelData):
    """Fields defining config state for generating a PQR file using PyMol with
    existing hydrogens and termini.
    """
    pass
class PyMOLPQRExistingHModel(
    QtCore.QObject, PyMOLPQRExistingHModelData, metaclass = DataclassDescriptorMetaclass
):
    """Config state for generating a PQR file using PyMol with existing hydrogens
    and termini.
    """
    pass

@dc.dataclass
class PyMOLPQRAddHModelData(BasePQRModelData):
    """Fields defining config state for generating a PQR file using PyMol with
    PyMol-added hydrogens and termini.
    """
    pass
class PyMOLPQRAddHModel(
    QtCore.QObject, PyMOLPQRAddHModelData, metaclass = DataclassDescriptorMetaclass
):
    """Config state for generating a PQR file using PyMol with PyMol-added hydrogens
    and termini.
    """
    pass

# ----------------------------------

@dc.dataclass
class BaseGridModelData(BaseModelData):
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
    QtCore.QObject, PSizeGridModelData, metaclass = DataclassDescriptorMetaclass
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
    QtCore.QObject, PluginGridModelData, metaclass = DataclassDescriptorMetaclass
):
    """Config state for generating APBS grid parameters using the plugin's logic.
    """
    pass

# ----------------------------------


if self.apbs_mode.getvalue() == 'Nonlinear Poisson-Boltzmann Equation':
    apbs_mode = 'npbe'
else:
    apbs_mode = 'lpbe'

bcflmap = {'Zero': 'zero',
            'Single DH sphere': 'sdh',
            'Multiple DH spheres': 'mdh',
            #'Focusing': 'focus',
            }
bcfl = bcflmap[self.bcfl.getvalue()]

chgmmap = {'Linear': 'spl0',
            'Cubic B-splines': 'spl2',
            'Quintic B-splines': 'spl4',
            }
chgm = chgmmap[self.chgm.getvalue()]

srfmmap = {'Mol surf for epsilon; inflated VdW for kappa, no smoothing': 'mol',
            'Same, but with harmonic average smoothing': 'smol',
            'Cubic spline': 'spl2',
            'Similar to cubic spline, but with 7th order polynomial': 'spl4', }
srfm = srfmmap[self.srfm.getvalue()]

@dc.dataclass
class APBSModelData(BaseModelData):
    """Fields defining config state for options to be passed to APBS.
    """
    apbs_path: pathlib.Path
    apbs_config_file: pathlib.Path
    apbs_pqr_file: pathlib.Path
    apbs_dx_file: pathlib.Path
    apbs_map_name: str

    grid_points: tuple
    cglen: tuple
    fglen: tuple
    cgcent: tuple
    fgcent: tuple
    apbs_mode: str = 'Linearized Poisson-Boltzmann Equation'
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
    sdens: float =10.0

        # #"max_mem_allowed" : 400,
        # "max_mem_allowed": 1500,
        # "potential_at_sas": 1,
        # "surface_solvent": 0,
        # "show_surface_for_scanning": 1,

class APBSModel(
    QtCore.QObject, APBSModelData, metaclass = DataclassDescriptorMetaclass
):
    """Config state for options to be passed to APBS.
    """
    pass
