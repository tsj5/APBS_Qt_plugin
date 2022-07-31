"""
Logic for communicating with backend processes, pdb2pqr and apbs.

Citation for APBS:
    Baker NA, Sept D, Joseph S, Holst MJ, McCammon JA. Electrostatics of
    nanosystems: application to microtubules and the ribosome. Proc.
    Natl. Acad. Sci. USA 98, 10037-10041 2001.

Citation for PDB2PQR:
    Dolinsky TJ, Nielsen JE, McCammon JA, Baker NA.
    PDB2PQR: an automated pipeline for the setup, execution,
    and analysis of Poisson-Boltzmann electrostatics calculations.
    Nucleic Acids Research 32 W665-W667 (2004).
"""
import os
import sys
import re
import shlex
import subprocess
import textwrap

import pymol

import util

class PDB2PQRWrapper:

    def fix_columns(self, sel):
        """
        Make sure that everything fits into the correct columns.
        This means doing some rounding. It also means getting rid of
        chain, occupancy and b-factor information.
        """
        pymol.cmd.alter_state(1, 'all', '(x,y,z)=float("%.3f"%x),float("%.3f"%y),float("%.3f"%z)')
        pymol.cmd.alter(sel, 'chain=""')
        pymol.cmd.alter(sel, 'b=0')
        pymol.cmd.alter(sel, 'q=0')

    def cleanup_generated_file(self, filename):
        """
        More cleanup on PQR files.

        pdb2pqr will happily write out a file where the coordinate
        columns overlap if you have -100.something as one of the
        coordinates, like

        90.350  97.230-100.010

        and so will PyMOL. We can't just assume that it's 0-1
        because pdb2pqr will debump things and write them out with
        3 digits post-decimal.
        """
        f = open(filename, 'r')
        txt = f.read()
        f.close()
        print(f"Erasing contents of {filename} in order to clean it up")
        f = open(filename, 'w')
        # APBS accepts whitespace-delimited columns
        coordregex = r'([- 0-9]{4}\.[ 0-9]{3})'
        txt = re.sub(
                r'^(ATOM  |HETATM)(........................)' + 3 * coordregex,
                r'\1\2 \3 \4 \5', txt, flags=re.M)
        f.write(txt)
        f.close()

    def get_unassigned_atoms(self, fname):
        """
        Return string of unassigned atoms, identified via warning text in comments
        in output.
        """
        f = open(fname)
        # Text contains PQR output string
        unassigned = re.compile('REMARK   5 *(\d+) \w* in').findall(f.read())
        f.close()
        return '+'.join(unassigned)

    # PQR generation routines are required to call
    # cleanup_generated_file themselves.
    def _write_pdb2pqr_file(self):
        """Use pdb2pqr to generate a PQR file.
        Call this via the wrapper write_PQR_file()
        """
        def show_error(message):
            print("In show error 2")
            error_dialog = Pmw.MessageDialog(self.parent,
                                             title='Error',
                                             message_text=message,
                                             )
            junk = error_dialog.activate()

        # First, generate a PDB file
        pdb_filename = self.pymol_generated_pdb_filename.getvalue()
        try:
            print(f"Erasing contents of {pdb_filename} in order to generate new PDB file")
            f = open(pdb_filename, 'w')
            f.close()
        except:
            show_error('Please set a temporary PDB file location that you have permission to edit')
            return False
        # copied from WLD code
        sel = "((%s) or (neighbor (%s) and hydro))" % (
            self.selection.getvalue(), self.selection.getvalue())

        apbs_clone = pymol.cmd.get_unused_name()
        pymol.cmd.create(apbs_clone,sel)

        self.fix_columns(apbs_clone)
        pymol.cmd.save(pdb_filename, apbs_clone)
        pymol.cmd.delete(apbs_clone)

        # Now, generate a PQR file
        args = [self.pdb2pqr.getvalue(),
                ] + shlex.split(self.pdb2pqr_options.getvalue()) + [
                            pdb_filename,
                            self.pymol_generated_pqr_filename.getvalue(),
        ]
        try:
            # This allows us to import pdb2pqr
            # sys.path.append(os.path.dirname(os.path.dirname(self.pdb2pqr.getvalue())))
            # print "Appended", os.path.dirname(os.path.dirname(self.pdb2pqr.getvalue()))
            ###!!! Edited for Pymol-script-repo !!!###
            # sys.path.append(os.path.join(os.environ['PYMOL_GIT_MOD'],"pdb2pqr"))
            # print "Appended", os.path.join(os.environ['PYMOL_GIT_MOD'],"pdb2pqr")
            ###!!!------------------------------!!!###
            #import pdb2pqr.pdb2pqr
            # This allows pdb2pqr to correctly find the dat directory with AMBER.DAT.
            # sys.path.append(os.path.dirname(self.pdb2pqr.getvalue()))
            # print "Appended", os.path.dirname(self.pdb2pqr.getvalue())
            # print "Imported pdb2pqr"
            # print "args are: ", args
            #from pdb2pqr import main
            # print "Imported main"
            try:
                ###!!! Edited for Pymol-script-repo !!!###
                args = ' '.join(map(str, args))
                print("args are now converted to string: ", args)
#                retval = main.mainCommand(args)
                if 'PYMOL_GIT_MOD' in os.environ:
                    os.environ['PYTHONPATH'] = os.path.join(os.environ['PYMOL_GIT_MOD']) + ":" + os.path.join(os.environ['PYMOL_GIT_MOD'], "pdb2pqr")
                pymol_env = os.environ
                callfunc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=pymol_env)
                child_stdout, child_stderr = callfunc.communicate()
                print(child_stdout)
                print(child_stderr)
                retval = callfunc.returncode
                print("PDB2PQR's mainCommand returned", retval)
#                if retval == 1:
# retval = 0 # success condition is backwards in pdb2pqr
#                elif retval == 0:
# retval = 1 # success condition is backwards in pdb2pqr
#                elif retval == None:
# retval = 0 # When PDB2PQR does not explicitly
# return anything, it's a success.
###!!!-------------------------------!!!###
            except:
                print("Exception raised by main.mainCommand!")
                print(sys.exc_info())
                retval = 1
        except:
            print("Unexpected error encountered while trying to import pdb2pqr:", sys.exc_info())
            retval = 1  # failure is nonzero here.

        if retval != 0:
            show_error('Could not run pdb2pqr: %s %s\n\nIt returned %s.\nCheck the PyMOL external GUI window for more information\n' % (self.pdb2pqr.getvalue(),
                                                                                                                                      args,
                                                                                                                                      retval)
                       )
            return False
        self.cleanup_generated_file(self.pymol_generated_pqr_filename.getvalue())
        unassigned_atoms = self.get_unassigned_atoms(self.pymol_generated_pqr_filename.getvalue())
        if unassigned_atoms:
            pymol.cmd.select('unassigned', 'ID %s' % unassigned_atoms)
            message_text = "Unable to assign parameters for the %s atoms in selection 'unassigned'.\nPlease either remove these unassigned atoms and re-start the calculation\nor fix their parameters in the generated PQR file and run the calculation\nusing the modified PQR file (select 'Use another PQR' in 'Main')." % len(unassigned_atoms.split('+'))
            print("Unassigned atom IDs", unassigned_atoms)
            show_error(message_text)
            return False
        if DEBUG:
            print("I WILL RETURN TRUE from pdb2pqr")
        return True

    # PQR generation routines are required to call
    # cleanup_generated_file themselves.
    def _write_pymol_pqr_file(self):
        """generate a pqr file from pymol

        This will also call through to champ to set the Hydrogens and charges
        if it needs to.  If it does that, it may change the value self.selection
        to take the new Hydrogens into account.

        To make it worse, APBS seems to freak out when there are chain ids.  So,
        this gets rid of the chain ids.

        call this through the wrapper write_PQR_file
        """
        # CHAMP will break in many cases if retain_order is set. So,
        # we unset it here and reset it later. Note that it's fine to
        # reset it before things are written out.
        ret_order = pymol.cmd.get('retain_order')
        pymol.cmd.set('retain_order', 0)

        # WLD
        sel = "((%s) or (neighbor (%s) and hydro))" % (
            self.selection.getvalue(), self.selection.getvalue())

        pqr_filename = self.getPqrFilename()
        try:
            if DEBUG:
                print("Erasing previous contents of", pqr_filename)
            f = open(pqr_filename, 'w')
            f.close()
        except:
            error_dialog = Pmw.MessageDialog(self.parent,
                                             title='Error',
                                             message_text="Could not write PQR file.\nPlease check that temporary PQR filename is valid.",
                                             )
            junk = error_dialog.activate()
            return False

        # PyMOL + champ == pqr
        from chempy.champ import assign
        if self.radiobuttons.getvalue() == 'Use PyMOL generated PQR and PyMOL generated Hydrogens and termini':
            pymol.cmd.remove('hydro and %s' % sel)
            assign.missing_c_termini(sel)
            assign.formal_charges(sel)
            pymol.cmd.h_add(sel)

        assign.amber99(sel)
        pymol.cmd.set('retain_order', ret_order)

        apbs_clone = pymol.cmd.get_unused_name()
        pymol.cmd.create(apbs_clone, sel)

        self.fix_columns(apbs_clone)
        pymol.cmd.save(pqr_filename, apbs_clone)

        pymol.cmd.delete(apbs_clone)

        self.cleanup_generated_file(pqr_filename)
        missed_count = pymol.cmd.count_atoms(f"({sel}) and flag 23")
        if missed_count > 0:
            pymol.cmd.select("unassigned", f"({sel}) and flag 23")
            error_dialog = Pmw.MessageDialog(self.parent,
                                             title='Error',
                                             message_text="Unable to assign parameters for the %s atoms in selection 'unassigned'.\nPlease either remove these unassigned atoms and re-start the calculation\nor fix their parameters in the generated PQR file and run the calculation\nusing the modified PQR file (select 'Use another PQR' in 'Main')." % missed_count,
                                             )
            junk = error_dialog.activate()
            return False
        return True

    def write_PQR_file(self):
        ''' Wrapper for all of our PQR generation routines.

        - Generate PQR file if necessary
        - Return False if unsuccessful, True if successful.

        - Clean up PQR file if we generated it (the
          generate... functions are required to do this.).
        '''
        if self.radiobuttons.getvalue() == 'Use another PQR':
            pass
        elif self.radiobuttons.getvalue() == 'Use PDB2PQR':
            if DEBUG:
                print("GENERATING PQR FILE via PDB2PQR")
            good = self._write_pdb2pqr_file()
            if not good:
                if DEBUG:
                    print("Could not generate PDB2PQR file.  _write_pdb2pqr_file failed.")
                return False
            if DEBUG:
                print("GENERATED")
        else:  # it's one of the pymol-generated options
            if DEBUG:
                print("GENERATING PQR FILE via PyMOL")
            good = self._write_pymol_pqr_file()
            if not good:
                if DEBUG:
                    print("Could not generate the PyMOL-basd PQR file.  generatePyMOLPqrFile failed.")
                return False
            if DEBUG:
                print("GENERATED")
        return True


class PSizeWrapper:

    def run(self):
        class NoPsize(Exception):
            pass

        class NoPDB(Exception):
            pass
        try:
            if not self.psize.valid():
                raise NoPsize
            good = self.write_PQR_file()
            if not good:
                print("Could not generate PQR file!")
                return False
            pqr_filename = self.getPqrFilename()
            try:
                f = open(pqr_filename, 'r')
                f.close()
            except:
                raise NoPDB

            #
            # Do some magic to load the psize module
            #
            import imp
            f, fname, description = imp.find_module('psize', [os.path.split(self.psize.getvalue())[0]])
            psize = imp.load_module('psize', f, fname, description)
            # WLD
            sel = "((%s) or (neighbor (%s) and hydro))" % (
                self.selection.getvalue(), self.selection.getvalue())

            if pymol.cmd.count_atoms(self.selection.getvalue() + " and not alt ''") != 0:
                print("WARNING: You have alternate locations for some of your atoms!")
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
            print("APBS's psize.py was used to calculated grid dimensions")
        except (NoPsize, ImportError, AttributeError) as e:
            print(e)
            print("This plugin was used to calculated grid dimensions")
            #
            # First, we need to get the dimensions of the molecule
            #
            # WLD
            sel = "((%s) or (neighbor (%s) and hydro))" % (
                self.selection.getvalue(), self.selection.getvalue())
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
                error_dialog = Pmw.MessageDialog(self.parent,
                                                 title='Error',
                                                 message_text="No atoms were in your selection",
                                                 )
                junk = error_dialog.activate()
                return False

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

            print("cs", cs)
            print("finedim", finedim)
            print("nlev", nlev)
            print("mult_fac", mult_fac)
            print("finegridpoints", finegridpoints)

        except NoPDB:
            error_dialog = Pmw.MessageDialog(self.parent,
                                             title='Error',
                                             message_text="Please set a temporary PDB file location",
                                             )
            junk = error_dialog.activate()
            return False

        if (finegridpoints[0] > 0) and (finegridpoints[1] > 0) and (finegridpoints[2] > 0):
            max_mem_allowed = float(self.max_mem_allowed.getvalue())

            def memofgrid(finegridpoints):
                return 200. * float(finegridpoints[0] * finegridpoints[1] * finegridpoints[2]) / 1024. / 1024

            def gridofmem(mem):
                return mem * 1024. * 1024. / 200.
            max_grid_points = gridofmem(max_mem_allowed)
            print("Estimated memory usage", memofgrid(finegridpoints), 'MB out of maximum allowed', max_mem_allowed)
            if memofgrid(finegridpoints) > max_mem_allowed:
                print("Maximum memory usage exceeded.  Old grid dimensions were", finegridpoints)
                product = float(finegridpoints[0] * finegridpoints[1] * finegridpoints[2])
                factor = pow(max_grid_points / product, 0.333333333)
                finegridpoints[0] = (int(factor * finegridpoints[0] / 2)) * 2 + 1
                finegridpoints[1] = (int(factor * finegridpoints[1] / 2)) * 2 + 1
                finegridpoints[2] = (int(factor * finegridpoints[2] / 2)) * 2 + 1
                print("Fine grid points rounded down from", finegridpoints)
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
                print("New grid dimensions are", finegridpoints)
        print(" APBS Tools: coarse grid: (%5.3f,%5.3f,%5.3f)" % tuple(coarsedim))
        self.grid_coarse_x.setvalue(coarsedim[0])
        self.grid_coarse_y.setvalue(coarsedim[1])
        self.grid_coarse_z.setvalue(coarsedim[2])
        print(" APBS Tools: fine grid: (%5.3f,%5.3f,%5.3f)" % tuple(finedim))
        self.grid_fine_x.setvalue(finedim[0])
        self.grid_fine_y.setvalue(finedim[1])
        self.grid_fine_z.setvalue(finedim[2])
        print(" APBS Tools: center: (%5.3f,%5.3f,%5.3f)" % tuple(center))
        self.grid_center_x.setvalue(center[0])
        self.grid_center_y.setvalue(center[1])
        self.grid_center_z.setvalue(center[2])
        print(" APBS Tools: fine grid points (%d,%d,%d)" % tuple(finegridpoints))
        self.grid_points_x.setvalue(finegridpoints[0])
        self.grid_points_y.setvalue(finegridpoints[1])
        self.grid_points_z.setvalue(finegridpoints[2])


class APBSWrapper:

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
        def show_error(message):
            print("In show error 1")
            error_dialog = Pmw.MessageDialog(self.parent,
                                             title='Error',
                                             message_text=message,
                                             )
            junk = error_dialog.activate()

        # First, check to make sure we have valid locations for apbs and psize
        if not self.binary.valid():
            show_error('Please set the APBS binary location')
            return False
        # If the path to psize is not correct, that's fine .. we'll
        # do the calculations ourself.

        # if not self.psize.valid():
        #    show_error("Please set APBS's psize location")
        #    return False

        # Now check the temporary filenames
        if self.radiobuttons.getvalue() != 'Use another PQR':
            if not self.pymol_generated_pqr_filename.getvalue():
                show_error('Please choose a name for the PyMOL\ngenerated PQR file')
                return False
        elif not self.pqr_to_use.valid():
            show_error('Please select a valid pqr file or tell\nPyMOL to generate one')
            return False
        if not self.pymol_generated_pdb_filename.getvalue():
            show_error('Please choose a name for the PyMOL\ngenerated PDB file')
            return False
        if not self.pymol_generated_dx_filename.getvalue():
            show_error('Please choose a name for the PyMOL\ngenerated DX file')
            return False
        if not self.pymol_generated_in_filename.getvalue():
            show_error('Please choose a name for the PyMOL\ngenerated APBS input file')
            return False
        if not self.map.getvalue():
            show_error('Please choose a name for the generated map.')
            return False

        # Now, the ions
        for sign in ('plus', 'minus'):
            for value in ('one', 'two'):
                for parm in ('conc', 'rad'):
                    if not getattr(self, f"ion_{sign}_{value}_{parm}").valid():
                        show_error('Please correct Ion concentrations and radii')
                        return False
        # Now the grid
        for grid_type in ('coarse', 'fine', 'points', 'center'):
            for coord in ('x', 'y', 'z'):
                if not getattr(self, f"grid_{grid_type}_{coord}").valid():
                    show_error('Please correct grid dimensions\nby clicking on the "Set grid" button')
                    return False

        # Now other easy things
        for message, thing in (
            ('solvent dielectric', self.solvent_dielectric),
            ('protein dielectric', self.interior_dielectric),
            ('solvent radius', self.solvent_radius),
            ('system temperature', self.system_temp),
            ('sdens', self.sdens),
        ):
            if not thing.valid():
                show_error('Please correct %s' % message)
                return False

        return True

    def write_APBS_input_file(self):
        if self.check_input():
            #
            # set up our variables
            #
            pqr_filename = self.getPqrFilename()

            grid_points = [int(getattr(self, 'grid_points_%s' % i).getvalue()) for i in 'x y z'.split()]
            cglen = [float(getattr(self, 'grid_coarse_%s' % i).getvalue()) for i in 'x y z'.split()]
            fglen = [float(getattr(self, 'grid_fine_%s' % i).getvalue()) for i in 'x y z'.split()]
            cent = [float(getattr(self, 'grid_center_%s' % i).getvalue()) for i in 'x y z'.split()]

            apbs_mode = self.apbs_mode.getvalue()
            if apbs_mode == 'Nonlinear Poisson-Boltzmann Equation':
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
            if DEBUG:
                print("GOT THE APBS INPUT FILE")

            # write out the input text
            try:
                print("Erasing contents of", self.pymol_generated_in_filename.getvalue(), "in order to write new input file")
                f = open(self.pymol_generated_in_filename.getvalue(), 'w')
                f.write(apbs_input_text)
                f.close()
            except IOError:
                print("ERROR: Got the input file from APBS, but failed when trying to write to %s" % self.pymol_generated_in_filename.getvalue())
            return True
        else:
            # self.check_input()
            return False
