"""
Model, view and controller for PQR file generation configuration.
"""
import enum
import logging
import pathlib
import shlex

_log = logging.getLogger(__name__)

import pymol.Qt.QtCore as QtCore
import util

# ------------------------------------------------------------------------------
# Models

@util.attrs_define_w_signals
class PQRBaseModel(util.BaseModel):
    """Fields defining config state shared by all PQRModels.
    """
    pqr_out_file: pathlib.Path
    cleanup_pqr: bool

@util.attrs_define_w_signals
class PPQRDB2PQRModel(PQRBaseModel):
    """Config state for generating a PQR file using the pdb2pqr binary.
    """
    pymol_selection: str
    pdb2pqr_path: pathlib.Path
    pdb_file: pathlib.Path

@util.attrs_define_w_signals
class PQRPyMolModel(PQRBaseModel):
    """Fields defining config state for generating a PQR file using PyMol.
    """
    pymol_selection: str
    add_hs: bool

@util.attrs_define_w_signals
class PQRPreExistingModel(PQRBaseModel):
    """Fields defining config state for using a pre-existing PQR file.
    """
    pqr_in_file: pathlib.Path

# ------------------------------------------------------------------------------
# Controllers

class BasePQRController():
    """Base class with common methods for all implementations of PQR file generation.
    """
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
        _log.info(f"Erasing contents of {filename} in order to clean it up")
        f = open(filename, 'w')
        # APBS accepts whitespace-delimited columns
        coordregex = r'([- 0-9]{4}\.[ 0-9]{3})'
        txt = re.sub(
                r'^(ATOM  |HETATM)(........................)' + 3 * coordregex,
                r'\1\2 \3 \4 \5', txt, flags=re.M)
        f.write(txt)
        f.close()

class PreExistingPQRController(BasePQRController):
    """Logic for using a pre-existing PQR file.
    """
    pass

class PDB2PQRController(BasePQRController):
    """Logic for generating a PQR file using the pdb2pqr binary.
    """
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
        # First, generate a PDB file
        pdb_filename = self.pymol_generated_pdb_filename.getvalue()
        try:
            _log.info(f"Erasing contents of {pdb_filename} in order to generate new PDB file")
            f = open(pdb_filename, 'w')
            f.close()
        except:
            raise util.PluginDialogException("Please set a temporary PDB file location "
                "that you have permission to edit")

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
            args = ' '.join(map(str, args))
            _log.info("args are now converted to string: ", args)
#                retval = main.mainCommand(args)
            if 'PYMOL_GIT_MOD' in os.environ:
                os.environ['PYTHONPATH'] = os.path.join(os.environ['PYMOL_GIT_MOD']) + ":" + os.path.join(os.environ['PYMOL_GIT_MOD'], "pdb2pqr")
            pymol_env = os.environ
            callfunc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=pymol_env)
            child_stdout, child_stderr = callfunc.communicate()
            _log.info(child_stdout)
            _log.info(child_stderr)
            retval = callfunc.returncode
            _log.info("PDB2PQR's mainCommand returned", retval)
        except Exception as exc:
            _log.warning("Exception raised by main.mainCommand!")
            _log.warning(sys.exc_info())
            retval = 1

        if retval != 0:
            raise util.PluginDialogException(f"Could not run pdb2pqr: {self.pdb2pqr.getvalue()} "
                f"{args}\n\nIt returned {retval}.\nCheck the PyMOL external GUI window "
                "for more information.\n"
            )
        self.cleanup_generated_file(self.pymol_generated_pqr_filename.getvalue())
        unassigned_atoms = self.get_unassigned_atoms(self.pymol_generated_pqr_filename.getvalue())
        if unassigned_atoms:
            pymol.cmd.select('unassigned', f"ID {unassigned_atoms}")
            _log.warning(f"Unassigned atom IDs: {unassigned_atoms}")
            raise util.PluginDialogException(f"Unable to assign parameters for the "
                f"{len(unassigned_atoms.split('+'))} atoms in selection 'unassigned'.\n"
                "Please either remove these unassigned atoms and re-start the calculation\n"
                "or fix their parameters in the generated PQR file and run the calculation\n"
                "using the modified PQR file (select 'Use another PQR' in 'Main')."
            )
        _log.debug("I WILL RETURN TRUE from pdb2pqr")

    # PQR generation routines are required to call
    # cleanup_generated_file themselves.
    def _write_pymol_pqr_file(self):
        """Generate a pqr file from pymol.

        This will also call through to champ to set the Hydrogens and charges
        if it needs to.  If it does that, it may change the value self.selection
        to take the new Hydrogens into account.

        To make it worse, APBS seems to freak out when there are chain ids.  So,
        this gets rid of the chain ids.

        call this through the wrapper write_PQR_file
        """
        try:
            from chempy.champ import assign
        except ModuleNotFoundError:
            raise util.PluginDialogException("_write_pymol_pqr_file couldn't import chempy.champ.")

        # CHAMP will break in many cases if retain_order is set. So,
        # we unset it here and reset it later. Note that it's fine to
        # reset it before things are written out.
        ret_order = pymol.cmd.get('retain_order')
        pymol.cmd.set('retain_order', 0)

        sel = self.selection.getvalue()
        sel = f"(({sel}) or (neighbor ({sel}) and hydro))"
        pqr_filename = self.getPqrFilename()
        try:
            _log.debug(f"Erasing previous contents of {pqr_filename}")
            f = open(pqr_filename, 'w')
            f.close()
        except Exception as exc:
            raise util.PluginDialogException("Could not write PQR file.\n"
                f"Please check that temporary PQR filename \"{pqr_filename}\" is valid."
            )

        # PyMOL + champ == pqr
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
            raise util.PluginDialogException(f"Unable to assign parameters for the {missed_count} "
                "atoms in selection 'unassigned'.\nPlease either remove these unassigned atoms "
                "and re-start the calculation\nor fix their parameters in the generated PQR file "
                "and run the calculation\nusing the modified PQR file (select 'Use another PQR' in 'Main')."
            )

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
            _log.debug("GENERATING PQR FILE via PDB2PQR")
            self._write_pdb2pqr_file()
        else:
            # it's one of the pymol-generated options
            _log.debug("GENERATING PQR FILE via PyMOL")
            self._write_pymol_pqr_file()
        _log.debug("GENERATED")

# ------------------------------------------------------------------------------
