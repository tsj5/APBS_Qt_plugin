"""
Model, view and controller representing configuration for the APBS code.
"""
import attrs
import enum
import logging
import pathlib
import string
import textwrap

_log = logging.getLogger(__name__)

import util

# ------------------------------------------------------------------------------
# Models

ApbsModeEnum = util.LabeledEnum("ApbsModeEnum",
    {
        'Nonlinear Poisson-Boltzmann Equation':  'npbe',
        'Linearized Poisson-Boltzmann Equation': 'lpbe'
    }
)

BcflEnum = util.LabeledEnum("BcflEnum",
    {
        'Zero': 'zero',
        'Single DH sphere': 'sdh',
        'Multiple DH spheres': 'mdh',
        #'Focusing': 'focus',
    }
)

ChgmEnum = util.LabeledEnum("ChgmEnum",
    {
        'Linear': 'spl0',
        'Cubic B-splines': 'spl2',
        'Quintic B-splines': 'spl4',
    }
)

SrfmEnum = util.LabeledEnum("SrfmEnum",
    {
        'Mol surf for epsilon; inflated VdW for kappa, no smoothing': 'mol',
        'Same, but with harmonic average smoothing': 'smol',
        'Cubic spline': 'spl2',
        'Similar to cubic spline, but with 7th order polynomial': 'spl4'
    }
)

@util.attrs_define
class APBSModel(util.BaseModel):
    """Config state for options to be passed to APBS.
    """
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
    sdens: float =10.0




# ------------------------------------------------------------------------------
# Controller

class APBSController(util.BaseController):
    _model_class = APBSModel # autogenerate on_*_changed Slots

    _file_template = string.Template(textwrap.dedent("""
        # Note that most of the comments here were taken from sample
        # input files that came with APBS.  You can find APBS at
        # https://github.com/Electrostatics/apbs
        # Note that APBS is GPL'd code.
        #
        read
            mol pqr ${pqr_filename}       # read molecule 1
        end
        elec
            mg-auto
            # grid calculated by psize.py:
            dime   ${grid_points_0} ${grid_points_1} ${grid_points_2}  # number of find grid points
            cglen  ${grid_coarse_x} ${grid_coarse_y} ${grid_coarse_z}  # coarse mesh lengths (A)
            fglen  ${grid_fine_x} ${grid_fine_y} ${grid_fine_z}        # fine mesh lengths (A)
            cgcent ${grid_center_x} ${grid_center_y} ${grid_center_z}  # (could also give (x,y,z) form psize.py) #known center
            fgcent ${grid_center_x} ${grid_center_y} ${grid_center_z}  # (could also give (x,y,z) form psize.py) #known center
            ${apbs_mode}     # solve the full nonlinear PBE ("npbe") or linear PBE ("lpbe")
            bcfl ${bcfl}     # Boundary condition flag
                            #  0 => Zero
                            #  1 => Single DH sphere
                            #  2 => Multiple DH spheres
                            #  4 => Focusing

            #ion 1 0.000 2.0 # Counterion declaration:
            ion charge  1 conc ${ion_plus_one_conc} radius ${ion_plus_one_rad}    # Counterion declaration:
            ion charge -1 conc ${ion_minus_one_conc} radius ${ion_minus_one_rad}  # ion <charge> <conc (M)> <radius>
            ion charge  2 conc ${ion_plus_two_conc} radius ${ion_plus_two_rad}    # ion <charge> <conc (M)> <radius>
            ion charge -2 conc ${ion_minus_two_conc} radius ${ion_minus_two_rad}  # ion <charge> <conc (M)> <radius>
            pdie ${interior_dielectric}        # Solute dielectric
            sdie ${solvent_dielectric}         # Solvent dielectric
            chgm ${chgm}     # Charge disc method
                            # 0 is linear splines
                            # 1 is cubic b-splines
            mol 1           # which molecule to use
            srfm smol       # Surface calculation method
                            #  0 => Mol surface for epsilon;
                            #       inflated VdW for kappa; no
                            #       smoothing
                            #  1 => As 0 with harmoinc average
                            #       smoothing
                            #  2 => Cubic spline
            srad ${solvent_radius} # Solvent radius (1.4 for water)
            swin 0.3              # Surface cubic spline window .. default 0.3
            temp ${system_temp}    # System temperature (298.15 default)
            sdens ${sdens}         # Specify the number of grid points per square-angstrom to use in Vacc object. Ignored when srad is 0.0 (see srad) or srfm is spl2 (see srfm). There is a direct correlation between the value used for the Vacc sphere density, the accuracy of the Vacc object, and the APBS calculation time. APBS default value is 10.0.
            #gamma 0.105          # Surface tension parameter for apolar forces (in kJ/mol/A^2)
                                  # only used for force calculations, so we don't care, but
                                  # it *used to be* always required, and 0.105 is the default
            calcenergy no         # Energy I/O to stdout
                                  #  0 => don't write out energy
                                  #  1 => write out total energy
                                  #  2 => write out total energy and all components
            calcforce no          # Atomic forces I/O (to stdout)
                                  #  0 => don't write out forces
                                  #  1 => write out net forces on molecule
                                  #  2 => write out atom-level forces
            write pot dx ${dx_filename}  # write the potential in dx format to a file.
        end
        quit

    """))

    @staticmethod
    def template_apbs_values(self, apbs_model):
        return attrs.asdict(self.model) # BROKEN, need to re-munge field names

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
        if self.model.dx_filename.endswith('.dx'):
            self.model.dx_filename = self.model.dx_filename[:-3]

        template_dict = dict()
        template_dict.update(self.template_grid_values(grid_model))
        template_dict.update(self.template_apbs_values(self.model))

        apbs_input_text = self._file_template.substitute(template_dict)
        _log.debug("GOT THE APBS INPUT FILE")

        # write out the input text
        try:
            _log.info("Erasing contents of", self.pymol_generated_in_filename.getvalue(), "in order to write new input file")
            f = open(self.pymol_generated_in_filename.getvalue(), 'w')
            f.write(apbs_input_text)
            f.close()
        except IOError:
            _log.info("ERROR: Got the input file from APBS, but failed when trying to write to %s" % self.pymol_generated_in_filename.getvalue())


