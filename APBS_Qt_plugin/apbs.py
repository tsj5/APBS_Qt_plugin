"""
Model, view and controller representing configuration for the APBS code.
"""
import dataclasses as dc
import enum
import logging
import pathlib
import textwrap

_log = logging.getLogger(__name__)

import pymol.Qt.QtCore as QtCore
import util

# ------------------------------------------------------------------------------
# Models

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

@util.attrs_define_w_signals
class APBSModel(util.BaseModel):
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

        # #"max_mem_allowed" : 400,
        # "max_mem_allowed": 1500,
        # "potential_at_sas": 1,
        # "surface_solvent": 0,
        # "show_surface_for_scanning": 1,

class APBSModel(
    QtCore.QObject, APBSModelData, metaclass = util.DataclassDescriptorMetaclass
):
    """Config state for options to be passed to APBS.
    """
    pass

# ------------------------------------------------------------------------------
# Controller

class APBSController():

    _file_template = textwrap.dedent("""
        # Note that most of the comments here were taken from sample
        # input files that came with APBS.  You can find APBS at
        # https://github.com/Electrostatics/apbs
        # Note that APBS is GPL'd code.
        #
        read
            mol pqr {pqr_filename}       # read molecule 1
        end
        elec
            mg-auto
            # grid calculated by psize.py:
            dime   {grid_points_0} {grid_points_1} {grid_points_2}  # number of find grid points
            cglen  {cglen_0} {cglen_1} {cglen_2}                   # coarse mesh lengths (A)
            fglen  {fglen_0} {fglen_1} {fglen_2}                   # fine mesh lengths (A)
            cgcent {cent_0} {cent_1} {cent_2}  # (could also give (x,y,z) form psize.py) #known center
            fgcent {cent_0} {cent_1} {cent_2}  # (could also give (x,y,z) form psize.py) #known center
            {apbs_mode}     # solve the full nonlinear PBE ("npbe") or linear PBE ("lpbe")
            bcfl {bcfl}     # Boundary condition flag
                            #  0 => Zero
                            #  1 => Single DH sphere
                            #  2 => Multiple DH spheres
                            #  4 => Focusing

            #ion 1 0.000 2.0 # Counterion declaration:
            ion charge  1 conc {ion_plus_one_conc} radius {ion_plus_one_rad}    # Counterion declaration:
            ion charge -1 conc {ion_minus_one_conc} radius {ion_minus_one_rad}  # ion <charge> <conc (M)> <radius>
            ion charge  2 conc {ion_plus_two_conc} radius {ion_plus_two_rad}    # ion <charge> <conc (M)> <radius>
            ion charge -2 conc {ion_minus_two_conc} radius {ion_minus_two_rad}  # ion <charge> <conc (M)> <radius>
            pdie {interior_dielectric}         # Solute dielectric
            sdie {solvent_dielectric}          # Solvent dielectric
            chgm {chgm}     # Charge disc method
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
            srad {solvent_radius} # Solvent radius (1.4 for water)
            swin 0.3              # Surface cubic spline window .. default 0.3
            temp {system_temp}    # System temperature (298.15 default)
            sdens {sdens}         # Specify the number of grid points per square-angstrom to use in Vacc object. Ignored when srad is 0.0 (see srad) or srfm is spl2 (see srfm). There is a direct correlation between the value used for the Vacc sphere density, the accuracy of the Vacc object, and the APBS calculation time. APBS default value is 10.0.
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
            write pot dx {dx_filename}  # write the potential in dx format to a file.
        end
        quit

    """)

    def template_APBS_input_file(pqr_filename,
                        grid_points,
                        cglen,
                        fglen,
                        cent,
                        apbs_mode,
                        bcfl,
                        ion_plus_one_conc, ion_plus_one_rad,
                        ion_minus_one_conc, ion_minus_one_rad,
                        ion_plus_two_conc, ion_plus_two_rad,
                        ion_minus_two_conc, ion_minus_two_rad,
                        interior_dielectric, solvent_dielectric,
                        chgm,
                        srfm,
                        solvent_radius,
                        system_temp,
                        sdens,
                        dx_filename,
                        ):
        print("Getting APBS input")


    def check_input(self):
        """No silent checks. Always show error.
        """
        # First, check to make sure we have valid locations for apbs and psize
        if not self.binary.valid():
            raise util.PluginDialogException('Please set the APBS binary location.')
        # If the path to psize is not correct, that's fine .. we'll
        # do the calculations ourself.

        # if not self.psize.valid():
        #    show_error("Please set APBS's psize location")
        #    return False

        # Now check the temporary filenames
        if self.radiobuttons.getvalue() != 'Use another PQR':
            if not self.pymol_generated_pqr_filename.getvalue():
                raise util.PluginDialogException('Please choose a name for the PyMOL\ngenerated PQR file.')
        elif not self.pqr_to_use.valid():
            raise util.PluginDialogException('Please select a valid pqr file or tell\nPyMOL to generate one.')
        if not self.pymol_generated_pdb_filename.getvalue():
            raise util.PluginDialogException('Please choose a name for the PyMOL\ngenerated PDB file.')
        if not self.pymol_generated_dx_filename.getvalue():
            raise util.PluginDialogException('Please choose a name for the PyMOL\ngenerated DX file.')
        if not self.pymol_generated_in_filename.getvalue():
            raise util.PluginDialogException('Please choose a name for the PyMOL\ngenerated APBS input file.')
        if not self.map.getvalue():
            raise util.PluginDialogException('Please choose a name for the generated map.')

        # Now, the ions
        for sign in ('plus', 'minus'):
            for value in ('one', 'two'):
                for parm in ('conc', 'rad'):
                    if not getattr(self, f"ion_{sign}_{value}_{parm}").valid():
                        raise util.PluginDialogException("Please correct Ion "
                            f"concentrations and radii (ion_{sign}_{value}_{parm})"
                        )
        # Now the grid
        for grid_type in ('coarse', 'fine', 'points', 'center'):
            for coord in ('x', 'y', 'z'):
                if not getattr(self, f"grid_{grid_type}_{coord}").valid():
                    raise util.PluginDialogException("Please correct grid dimensions"
                        f"\nby clicking on the "Set grid" button (grid_{grid_type}_{coord})"
                    )

        # Now other easy things
        for message, thing in (
            ('solvent dielectric', self.solvent_dielectric),
            ('protein dielectric', self.interior_dielectric),
            ('solvent radius', self.solvent_radius),
            ('system temperature', self.system_temp),
            ('sdens', self.sdens),
        ):
            if not thing.valid():
                raise util.PluginDialogException(f"Please correct {message}.")

    def write_APBS_input_file(self):
        self.check_input()

        # set up our variables
        pqr_filename = self.getPqrFilename()

        grid_points = [int(getattr(self, 'grid_points_%s' % i).getvalue()) for i in 'x y z'.split()]
        cglen = [float(getattr(self, 'grid_coarse_%s' % i).getvalue()) for i in 'x y z'.split()]
        fglen = [float(getattr(self, 'grid_fine_%s' % i).getvalue()) for i in 'x y z'.split()]
        cent = [float(getattr(self, 'grid_center_%s' % i).getvalue()) for i in 'x y z'.split()]

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

        dx_filename = self.pymol_generated_dx_filename.getvalue()
        if dx_filename.endswith('.dx'):
            dx_filename = dx_filename[:-3]
        apbs_input_text = template_APBS_input_file(pqr_filename,
                                            grid_points,
                                            cglen,
                                            fglen,
                                            cent,
                                            apbs_mode,
                                            bcfl,
                                            float(self.ion_plus_one_conc.getvalue()), float(self.ion_plus_one_rad.getvalue()),
                                            float(self.ion_minus_one_conc.getvalue()), float(self.ion_minus_one_rad.getvalue()),
                                            float(self.ion_plus_two_conc.getvalue()), float(self.ion_plus_two_rad.getvalue()),
                                            float(self.ion_minus_two_conc.getvalue()), float(self.ion_minus_two_rad.getvalue()),
                                            float(self.interior_dielectric.getvalue()), float(self.solvent_dielectric.getvalue()),
                                            chgm,
                                            srfm,
                                            float(self.solvent_radius.getvalue()),
                                            float(self.system_temp.getvalue()),
                                            float(self.sdens.getvalue()),
                                            dx_filename,
                                            )
        _log.debug("GOT THE APBS INPUT FILE")

        # write out the input text
        try:
            _log.info("Erasing contents of", self.pymol_generated_in_filename.getvalue(), "in order to write new input file")
            f = open(self.pymol_generated_in_filename.getvalue(), 'w')
            f.write(apbs_input_text)
            f.close()
        except IOError:
            _log.info("ERROR: Got the input file from APBS, but failed when trying to write to %s" % self.pymol_generated_in_filename.getvalue())


