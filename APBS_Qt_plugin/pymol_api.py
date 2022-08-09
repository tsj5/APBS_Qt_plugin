"""
Model, view and controller representing the part of PyMol app state that we use.

Overkill for current application, where we simply wrap the pymol.cmd module, but
in principle these classes could be extended to handle multiple pymol instances
(as with pymol.cmd2.)
"""
import logging
_log = logging.getLogger(__name__)

import attrs
import pymol.cmd as pymol_cmd
from . import util

# ------------------------------------------------------------------------------
# Models

@util.attrs_define
class PyMolModel(util.BaseModel):
    """Fields defining config state for the PyMol session that are
    plugin-specific (i.e. beyond the pymol API.)
    """
    sel_values: list = attrs.Factory(list)
    sel_idx: int = 0
    pymol_instance = pymol_cmd

    def __getattr__(self, name):
        """Pass through all method lookups to pymol.cmd.
        """
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, name)
        except AttributeError:
            return getattr(self.pymol_instance, name)

    @property
    def selection(self):
        """Return text of current selection.
        """
        try:
            return self.sel_values.__getitem__(self.sel_idx)
        except IndexError:
            raise util.PluginDialogException("Selection index out of range "
            f"{self.sel_idx}/{len(self.sel_values)}")

    @property
    def pymol_selection(self):
        """Return pymol.cmd string corresponding to the current selection.
        """
        # always include explicitly specified hydrogens -- make this an option?
        return f"(({self.selection}) or (neighbor ({self.selection}) and hydro))"

    def get_default_sel_values(self):
        # TODO: is this a reasonable default? List all object:molecules?
        new_values = ['polymer']
        new_values.extend(
            [f"polymer & {s}" for s in self.pymol_instance.get_object_list('polymer')]
        )
        return new_values

# ------------------------------------------------------------------------------
# Controllers

class PyMolController(util.PYQT_OBJECT):
    """Encapsulate state of PyMol application, for completeness.
    """
    def __init__(self, view):
        super(PyMolController, self).__init__()
        self.model = PyMolModel()
        # view for selection comboBox only; rest updated implicitly through
        # changes to state to pymol_instance "model"
        self.view = view

        # init combobox
        self.view.clear()
        for s in self.model.sel_values:
            self.view.addItem(s)

        # view -> model
        self.view.currentIndexChanged.connect()
        self.view.editTextChanged.connect(self.insert_custom_sel_value)

        # model -> view
        self.model.sel_idx_changed.connect(self.view.setCurrentIndex)

        # init view from model values
        self.model.refresh()


    @util.PYQT_SLOT(int)
    def change_selection(self, new_sel_idx):
        try:
            _ = self.model.sel_values.__getitem__(new_sel_idx)
        except IndexError:
            raise util.PluginDialogException("Selection index out of range "
            f"{self.model.sel_idx}/{len(self.model.sel_values)}")
        self.model.sel_idx = new_sel_idx

    @util.PYQT_SLOT
    def get_pymol_sel_values(self):
        """Populate selection values based on current pymol state.
        """
        old_sel = self.model.selection
        self.model.sel_values = self._get_default_sel_values()
        if old_sel in self.model.sel_values:
            self.model.sel_idx = self.model.sel_values.index(old_sel)
        else:
            # selected entry doesn't exist anymore; reset to first entry
            self.model.sel_idx = 0

    @util.PYQT_SLOT(str)
    def insert_custom_sel_value(self, value_str):
        """Add a custom (user-specified) selection value to the list, and select
        it.
        """
        # TODO: don't check that value_str is a valid pymol command; no logic
        # to catch exception & recover if that isn't the case

        # remove enclosing parentheses, if any; restored by pymol_selection()
        value_str = value_str.strip('()')

        new_values = self._get_default_sel_values()
        new_values.append(value_str)
        self.model.sel_values = new_values
        self.model.sel_idx = len(new_values)






