"""
Model, view and controller for PQR file generation configuration.
"""
import os
import pathlib
import re
import shlex

import logging
_log = logging.getLogger(__name__)

from . import pymol_api, util
from .ui.views import VizGroupBoxView

# ------------------------------------------------------------------------------
# Models

@util.attrs_define
class PQRBaseModel(util.BaseModel):
    """Fields defining config state shared by all PQRModels.
    """
    pymol_cmd: pymol_api.PyMolModel
    prepare_pqr: bool = True
    pqr_out_file: pathlib.Path
    pqr_out_name: str = "prepared"

    def write_selection_to_file(self, sel, path):
        """Write the state of selection `sel` to a text file at `path`. File
        format is set automatically from extension.
        """
        temp_mol_obj = self.pymol_cmd.get_unused_name()
        self.pymol_cmd.create(temp_mol_obj, sel)

        # Make sure that everything fits into the correct columns (rounding)
        self.pymol_cmd.alter_state(
            1, 'all', '(x,y,z)=float("%.3f"%x),float("%.3f"%y),float("%.3f"%z)'
        )
        # Get rid of chain, occupancy and b-factor information
        self.pymol_cmd.alter(temp_mol_obj, 'chain=""')
        self.pymol_cmd.alter(temp_mol_obj, 'b=0')
        self.pymol_cmd.alter(temp_mol_obj, 'q=0')

        self.pymol_cmd.save(path, temp_mol_obj)
        self.pymol_cmd.delete(temp_mol_obj)

    @staticmethod
    def clean_pqr_columns(pqr_txt):
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

@util.attrs_define
class PPQRDB2PQRModel(PQRBaseModel):
    """Config state for generating a PQR file using the pdb2pqr binary.
    """
    pdb2pqr_path: pathlib.Path
    pdb_out_file: pathlib.Path
    pdb2pqr_flags: str
    ignore_warn: bool

    @staticmethod
    def get_unassigned_atoms(pqr_txt):
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
        sel = self.pymol_cmd.pymol_selection
        self.write_selection_to_file(sel, self.pdb_out_file)

        # Now, convert the generated file.
        args = [self.pdb2pqr_path] + shlex.split(self.pdb2pqr_flags) \
            + [self.pdb_out_file, self.pqr_out_file]
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
            raise util.PluginDialogException(f"Could not run pdb2pqr: {self.pdb2pqr_path} "
                f"{args}\n\nIt returned {retval}.\nCheck the PyMOL external GUI window "
                "for more information.\n"
            )

        if self.prepare_pqr:
            with open(self.pqr_out_file, 'a+') as f:
                pqr_text = f.read()
                pqr_text = self.clean_pqr_columns(pqr_text)
                unassigned_atoms = self.get_unassigned_atoms(pqr_text)
                f.seek(0)
                f.write(pqr_text)
                f.truncate()
        else:
            with open(self.pqr_out_file, 'r') as f:
                pqr_text = f.read()
                unassigned_atoms = self.get_unassigned_atoms(pqr_text)

        if unassigned_atoms:
            self.pymol_cmd.select('unassigned', f"ID {unassigned_atoms}")
            _log.warning(f"Unassigned atom IDs: {unassigned_atoms}")
            raise util.PluginDialogException(f"Unable to assign parameters for the "
                f"{len(unassigned_atoms.split('+'))} atoms in selection 'unassigned'.\n"
                "Please either remove these unassigned atoms and re-start the calculation\n"
                "or fix their parameters in the generated PQR file and run the calculation\n"
                "using the modified PQR file (select 'Use another PQR' in 'Main')."
            )
        _log.debug("I WILL RETURN TRUE from pdb2pqr")

@util.attrs_define
class PQRPyMolModel(PQRBaseModel):
    """Fields defining config state for generating a PQR file using PyMol.
    """
    add_hs: bool = True

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
            # chempy appears to be packaged with pymol
            from chempy.champ import assign
        except ModuleNotFoundError:
            raise util.PluginDialogException("write_PQR_file couldn't import chempy.champ.")

        # CHAMP will break in many cases if retain_order is set. So,
        # we unset it here and reset it later. Note that it's fine to
        # reset it before things are written out.
        ret_order = self.pymol_cmd.get('retain_order')
        self.pymol_cmd.set('retain_order', 0)

        sel = self.pymol_cmd.selection
        sel = f"(({sel}) or (neighbor ({sel}) and hydro))"

        # PyMOL + champ == pqr
        if self.add_hs:
            self.pymol_cmd.remove('hydro and %s' % sel)
            assign.missing_c_termini(sel)
            assign.formal_charges(sel)
            self.pymol_cmd.h_add(sel)
        assign.amber99(sel)
        self.pymol_cmd.set('retain_order', ret_order)

        self.write_selection_to_file(sel, self.pqr_out_file)

        with open(self.pqr_out_file, 'a+') as f:
            pqr_text = f.read()
            pqr_text = self.clean_pqr_columns(pqr_text)
            f.seek(0)
            f.write(pqr_text)
            f.truncate()

        missed_count = self.pymol_cmd.count_atoms(f"({sel}) and flag 23")
        if missed_count > 0:
            self.pymol_cmd.select("unassigned", f"({sel}) and flag 23")
            raise util.PluginDialogException(f"Unable to assign parameters for the {missed_count} "
                "atoms in selection 'unassigned'.\nPlease either remove these unassigned atoms "
                "and re-start the calculation\nor fix their parameters in the generated PQR file "
                "and run the calculation\nusing the modified PQR file (select 'Use another PQR' in 'Main')."
            )

# ------------------------------------------------------------------------------
# Controllers

class PQRController(util.BaseController):
    """Base class with common methods for all implementations of PQR file generation.
    """
    def __init__(self, pymol_controller=None, view=None):
        super(PQRController, self).__init__()
        if pymol_controller is None:
            raise ValueError
        pdb2pqr_model = PPQRDB2PQRModel(
            pymol_cmd = pymol_controller.model.pymol_instance
        )
        pymol_model = PQRPyMolModel(
            pymol_cmd = pymol_controller.model.pymol_instance
        )
        self.model = util.MultiModel(models = [pdb2pqr_model, pymol_model])
        if view is None:
            self.view = VizGroupBoxView()
        else:
            self.view = view

        # populate Method comboBox
        self.view.pqr_method_comboBox.clear()
        self.view.pqr_method_comboBox.addItem("Using pdb2pqr")
        self.view.pqr_method_comboBox.addItem("Using PyMol")
        self.view.pqr_method_comboBox.setIndex(0)

        # view <-> multimodel
        util.biconnect(self.view.pqr_method_comboBox, self.model, "multimodel_index")
        self.view.pqr_prepare_mol_checkBox.stateChanged.connect(self.on_prepare_mol_changed)

        # view <-> pdb2pqr_model
        util.biconnect(self.view.pqr_output_mol_lineEdit, pdb2pqr_model, "pqr_out_name")
        util.biconnect(self.view.pdb2pqr_flags_lineEdit, pdb2pqr_model, "pdb2pqr_flags")
        util.biconnect(self.view.pdb2pqr_warnings_checkBox, pdb2pqr_model, "ignore_warn")

        # view <-> pymol_model
        util.biconnect(self.view.pqr_output_mol_lineEdit, pymol_model, "pqr_out_name")

        # init view from model values
        self.model.refresh()

    @util.PYQT_SLOT(bool)
    def on_prepare_mol_changed(self, b):
        if b:
            # "do prepare" = either use pdb2pqr, or use pymol pqr and add Hs
            idx = self.view.pqr_method_comboBox.currentIndex()
            self.model.multimodel_index = idx
            self.model.models[1].add_hs = True # need better syntax for this stuff
        else:
            # "don't prepare" = use PyMol PQR, don't try to add Hs
            self.model.multimodel_index = 1 # need better syntax for this stuff
            self.model.add_hs = False


