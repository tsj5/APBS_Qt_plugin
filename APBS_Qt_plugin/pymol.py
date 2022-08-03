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
import util

# ------------------------------------------------------------------------------
# Models

@util.attrs_define_w_signals
class PyMolModel(util.BaseModel):
    """Fields defining config state for the PyMol session that are
    plugin-specific (i.e. beyond the pymol API.)
    """
    sel_values: list = attrs.Factory(list)
    sel_idx: int

    @property
    def selection(self):
        """Return text of current selection.
        """
        try:
            return self.sel_values.__getitem__(self.sel_idx)
        except IndexError:
            raise util.PluginDialogException("Selection index out of range "
            f"{self.sel_idx}/{len(self.sel_values)}")

# ------------------------------------------------------------------------------
# Controllers

class PyMolController():
    """Encapsulate state of PyMol application, for completeness.
    """
    def __init__(self, model):
        self._pymol = pymol_cmd
        self._model = model

    def __getattr__(self, name):
        """Pass through all attribute access to pymol.cmd.
        """
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, name)
        except AttributeError:
            return getattr(self._pymol, name)

    def __setattr__(self, name, value):
        """Pass through all attribute access to pymol.cmd.
        """
        try:
            # Throws exception if not in prototype chain
            _ = object.__getattribute__(self, name)
        except AttributeError:
            try:
                setattr(self._pymol, name, value)
            except Exception:
                raise AttributeError(name)
        else:
            object.__setattr__(self, name, value)

    @property
    def pymol_selection(self):
        """Return pymol.cmd string corresponding to the current selection.
        """
        # always include explicitly specified hydrogens -- make this an option?
        sel = self._model.selection
        return f"(({sel}) or (neighbor ({sel}) and hydro))"

    def _get_default_sel_values(self):
        # TODO: is this a reasonable default? List all object:molecules?
        new_values = ['polymer']
        new_values.extend(
            [f"polymer & {s}" for s in self._pymol.get_object_list('polymer')]
        )
        return new_values

    def get_pymol_sel_values(self):
        """Populate selection values based on current pymol state.
        """
        old_sel = self._model.selection
        self._model.sel_values = self._get_default_sel_values()
        if old_sel in self._model.sel_values:
            self._model.sel_idx = self._model.sel_values.index(old_sel)
        else:
            # selected entry doesn't exist anymore; reset to first entry
            self._model.sel_idx = 0

    def insert_custom_sel_value(self, value_str):
        """Add a custom (user-specified) selection value to the list, and select
        it.
        """
        # remove enclosing parentheses, if any; restored by pymol_selection()
        value_str = value_str.strip('()')

        new_values = self._get_default_sel_values()
        new_values.append(value_str)
        self._model.sel_values = new_values
        self._model.sel_idx = len(new_values)






