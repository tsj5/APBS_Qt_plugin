"""
Classes for storing config state.
"""

import dataclasses as dc
import enum
import logging
import pathlib

_log = logging.getLogger(__name__)

# ----------------------------------

class BasePQRModel():
    """Config state shared by all PQRModels.
    """
    pqr_file: pathlib.Path

@dc.dataclass
class PreExistingPQRModel(BasePQRModel):
    """Config state for using a pre-existing PQR file.
    """
    pass

@dc.dataclass
class PDB2PQRModel(BasePQRModel):
    """Config state for generating a PQR file using the pdb2pqr binary.
    """
    pdb2pqr_path: pathlib.Path
    pdb_file: pathlib.Path

@dc.dataclass
class PyMOLPQRExistingHModel(BasePQRModel):
    """Config state for generating a PQR file using PyMol with existing hydrogens
    and termini.
    """
    pass

@dc.dataclass
class PyMOLPQRAddHModel(BasePQRModel):
    """Config state for generating a PQR file using PyMol with PyMol-added hydrogens
    and termini.
    """
    pass

# ----------------------------------

class BaseGridModel():
    """Config state shared by all GridModels.
    """
    pass

class PsizeGridModel(BaseGridModel):
    """Config state for generating APBS grid parameters using psize.py (provided
    as part of APBS.)
    """
    psize_path: pathlib.Path

class PluginGridModel(BaseGridModel):
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
class APBSModel():
    """Config state for options to be passed to APBS.
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

        #"max_mem_allowed" : 400,
        "max_mem_allowed": 1500,
        "potential_at_sas": 1,
        "surface_solvent": 0,
        "show_surface_for_scanning": 1,
