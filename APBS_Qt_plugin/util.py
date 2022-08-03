"""
Utility classes and functions.
"""
import attrs
import functools
import logging
import pathlib

_log = logging.getLogger(__name__)

import pymol.Qt.QtCore as QtCore


# ------------------------------------------------------------------------------
# Qt convenience classes

PYQT_SIGNAL = QtCore.pyqtSignal # name differs between PyQT and PySide

class SignalWrapper():
    """Descriptor to automatically emit a pyqtSignal (assumed predefined)
    on change of a model attribute.
    """
    def __init__(self, name, signal_type=None):
        self.__set_name__(None, name)
        self.signal_type = signal_type

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name
        self.signal_name = '_' + name + '_changed'

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        """Emit `signal_name` when value is changed to a new value (only.)
        """
        old_value = getattr(obj, self.private_name)
        try:
            setattr(obj, self.private_name, value)
            if old_value != value:
                getattr(obj, self.signal_name).emit(self.signal_type(value))
        except ValueError:
            # if attrs validation fails, don't emit signal
            raise

def _attr_field_transformer(cls, fields):
    """Modify field definition process on attrs/dataclass in order to set up
    signal and signal descriptor. The original field is mapped to `private_name`,
    while the descriptor is assigned to the original `public_name`.

    See https://www.attrs.org/en/stable/extending.html#automatic-field-transformation-and-modification.
    """
    new_fields = []
    for f in fields:
        desc = SignalWrapper(f.name)
        renamed_f = f.evolve(name=desc.private_name)
        new_fields.append(renamed_f)
        setattr(cls, desc.public_name, desc)
        setattr(cls, desc.signal_name, PYQT_SIGNAL(f.type))
    return new_fields

def attrs_define_w_signals(cls=None, **deco_kwargs):
    """Wrap the attrs.define() class decorator to automatically invoke
    `_attr_field_transformer`, to automatically define and emit signals when the
    values of the fields of `cls` are changed.
    """
    deco_kwargs.update({"slots":False, "field_transformer":_attr_field_transformer})
    if cls is None:
        # decorator called without arguments
        return functools.partial(attrs_define_w_signals, **deco_kwargs)

    # check that the class we're decorating is capable of emitting Signals
    assert any(issubclass(cls_, QtCore.QObject) for cls_ in cls.__mro__)

    # attrs auto-generates an __init__ method; need to manually ensure that
    # super() is called.
    # https://www.attrs.org/en/stable/init.html#hooking-yourself-into-initialization
    def _pre_init(self):
        super(cls, self).__init__()
    setattr(cls, "__attrs_pre_init__", _pre_init)

    return attrs.define(cls, **deco_kwargs)

@attrs_define_w_signals
class BaseModel(QtCore.QObject):
    """Base class for our Model classes.
    """
    pass

class MultiModel(QtCore.QObject):
    """Wrapper for a collection of Models: maintains state of all models, but
    attributes are only looked up on the currently active Model.
    """
    _multimodel_index_changed = PYQT_SIGNAL(int)

    def __init__(self, models):
        self.multimodel_index = SignalWrapper("multimodel_index", default=0)
        self._model_state = models

    def __getattr__(self, name):
        """Pass through all attribute access to the currently selected Model.
        """
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, name)
        except AttributeError:
            return getattr(self._model_state[self.multimodel_index], name)

    def __setattr__(self, name, value):
        """Pass through all attribute access to the currently selected Model.
        """
        try:
            # Throws exception if not in prototype chain
            _ = object.__getattribute__(self, name)
        except AttributeError:
            try:
                setattr(self._model_state[self.multimodel_index], name, value)
            except Exception:
                raise AttributeError(name)
        else:
            object.__setattr__(self, name, value)

# ----------------------------------------------------------------------

class PluginException(Exception):
    """Base class for all exceptions raised by plugin's code.
    """
    pass

class NoPsizeException(PluginException):
    pass

class NoPDBException(PluginException):
    pass

class PluginDialogException(PluginException):
    """Base class for any exception which will be handled at the top level of
    the plugin by creating a dialog box.
    """
    pass
