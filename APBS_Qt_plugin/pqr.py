"""
Model, view and controller for PQR file generation configuration.
"""
import os
import enum
import logging
import pathlib
import re
import shlex

_log = logging.getLogger(__name__)

import pymol.cmd as pymol_cmd
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
    @staticmethod
    def write_selection_to_file(self, sel, path):
        """Write the state of selection `sel` to a text file at `path`. File
        format is set automatically from extension.
        """
        temp_mol_obj = pymol_cmd.get_unused_name()
        pymol_cmd.create(temp_mol_obj, sel)

        # Make sure that everything fits into the correct columns (rounding)
        pymol_cmd.alter_state(1, 'all', '(x,y,z)=float("%.3f"%x),float("%.3f"%y),float("%.3f"%z)')
        # Get rid of chain, occupancy and b-factor information
        pymol_cmd.alter(temp_mol_obj, 'chain=""')
        pymol_cmd.alter(temp_mol_obj, 'b=0')
        pymol_cmd.alter(temp_mol_obj, 'q=0')

        pymol_cmd.save(path, temp_mol_obj)
        pymol_cmd.delete(temp_mol_obj)

    @staticmethod
    def clean_pqr_columns(self, pqr_txt):
        """Cleanup on contents of generated PQR files.

        pdb2pqr will happily write out a file where the coordinate
        columns overlap if you have -100.something as one of the
        coordinates, like

        90.350  97.230-100.010

        and so will PyMOL. We can't just assume that it's 0-1
        because pdb2pqr will debump things and write them out with
        3 digits post-decimal.
        """
        # APBS accepts whitespace-delimited columns
        coord_regex = r'([- 0-9]{4}\.[ 0-9]{3})'
        source_regex = re.compile(r'^(ATOM  |HETATM)(........................)' + 3*coord_regex)
        target_regex = re.compile(r'\1\2 \3 \4 \5')
        return re.sub(source_regex, target_regex, pqr_txt, flags=re.M)

class PreExistingPQRController(BasePQRController):
    """Logic for using a pre-existing PQR file.
    """
    def write_PQR_file(self):
        if self.getvalue(clean_pqr):
            with open(pqr_filename, 'a+') as f:
                pqr_text = f.read()
                pqr_text = self.clean_pqr_columns(pqr_text)
                f.seek(0)
                f.write(pqr_text)
                f.truncate()


class PDB2PQRController(BasePQRController):
    """Logic for generating a PQR file using the pdb2pqr binary.
    """
    def get_unassigned_atoms(self, pqr_txt):
        """
        Return string of unassigned atoms, identified via warning text in comments
        in output.
        """
        unassigned = re.compile(r'REMARK   5 *(\d+) \w* in').findall(pqr_txt)
        return '+'.join(unassigned)

    def write_PQR_file(self):
        """Use pdb2pqr to generate a PQR file.
        """
        _log.debug("GENERATING PQR FILE via PDB2PQR")
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

        self.write_selection_to_file(sel, pdb_filename)

        # Now, convert the generated file.
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

        if self.getvalue(clean_pqr):
            with open(pqr_filename, 'a+') as f:
                pqr_text = f.read()
                pqr_text = self.clean_pqr_columns(pqr_text)
                f.seek(0)
                f.write(pqr_text)
                f.truncate()
        else:
            with open(pqr_filename, 'r') as f:
                pqr_text = f.read()

        unassigned_atoms = self.get_unassigned_atoms(pqr_txt)
        if unassigned_atoms:
            pymol_cmd.select('unassigned', f"ID {unassigned_atoms}")
            _log.warning(f"Unassigned atom IDs: {unassigned_atoms}")
            raise util.PluginDialogException(f"Unable to assign parameters for the "
                f"{len(unassigned_atoms.split('+'))} atoms in selection 'unassigned'.\n"
                "Please either remove these unassigned atoms and re-start the calculation\n"
                "or fix their parameters in the generated PQR file and run the calculation\n"
                "using the modified PQR file (select 'Use another PQR' in 'Main')."
            )
        _log.debug("I WILL RETURN TRUE from pdb2pqr")


class PQRPyMolController(BasePQRController):
    """Logic for generating a PQR file using the pdb2pqr binary.
    """
    def write_PQR_file(self):
        """Generate a pqr file from pymol.

        This will also call through to champ to set the Hydrogens and charges
        if it needs to.  If it does that, it may change the value self.selection
        to take the new Hydrogens into account.

        To make it worse, APBS seems to freak out when there are chain ids.  So,
        this gets rid of the chain ids.
        """
        _log.debug("GENERATING PQR FILE via PyMOL")
        try:
            from chempy.champ import assign
        except ModuleNotFoundError:
            raise util.PluginDialogException("_write_pymol_pqr_file couldn't import chempy.champ.")

        # CHAMP will break in many cases if retain_order is set. So,
        # we unset it here and reset it later. Note that it's fine to
        # reset it before things are written out.
        ret_order = pymol_cmd.get('retain_order')
        pymol_cmd.set('retain_order', 0)

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
            pymol_cmd.remove('hydro and %s' % sel)
            assign.missing_c_termini(sel)
            assign.formal_charges(sel)
            pymol_cmd.h_add(sel)

        assign.amber99(sel)
        pymol_cmd.set('retain_order', ret_order)

        self.write_selection_to_file(sel, pqr_filename)

        if self.getvalue(clean_pqr):
            with open(pqr_filename, 'a+') as f:
                pqr_text = f.read()
                pqr_text = self.clean_pqr_columns(pqr_text)
                f.seek(0)
                f.write(pqr_text)
                f.truncate()

        missed_count = pymol_cmd.count_atoms(f"({sel}) and flag 23")
        if missed_count > 0:
            pymol_cmd.select("unassigned", f"({sel}) and flag 23")
            raise util.PluginDialogException(f"Unable to assign parameters for the {missed_count} "
                "atoms in selection 'unassigned'.\nPlease either remove these unassigned atoms "
                "and re-start the calculation\nor fix their parameters in the generated PQR file "
                "and run the calculation\nusing the modified PQR file (select 'Use another PQR' in 'Main')."
            )

# ------------------------------------------------------------------------------
