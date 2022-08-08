"""
Utility classes and functions.
"""
import attrs
import collections
import enum
import functools
import logging
import pathlib

_log = logging.getLogger(__name__)

import pymol.Qt.QtCore as QtCore
from pymol.Qt.QtWidgets import (
    QWidget, QCheckBox, QComboBox, QLineEdit
)

# ------------------------------------------------------------------------------
# Qt convenience classes

# name differs between PyQT and PySide; believe pymol.Qt wraps differences for
# us, but this is just to be safe
PYQT_PROPERTY = QtCore.pyqtProperty
PYQT_SIGNAL = QtCore.pyqtSignal
PYQT_SLOT = QtCore.pyqtSlot
PYQT_QOBJECT = QtCore.QObject

# ------------------------------------------------------------------------------
# Auto-generate Properties and Signals for fields on model classes
# PyQt docs state that Signals can't be defined dynamically; this isn't true
# Adaption of solution from https://stackoverflow.com/a/66266877

def _attr_field_transformer(cls, fields):
    """Modify field definition process on attrs/dataclass in order to set up
    signal and signal descriptor. The original field is mapped to `private_name`,
    while the descriptor is assigned to the original `public_name`.

    See https://www.attrs.org/en/stable/extending.html#automatic-field-transformation-and-modification.
    """
    new_fields = []
    for f in fields:
        if attrs.has(f.type) or issubclass(f.type, PYQT_QOBJECT):
            # don't create a descriptor/signal for attributes that are other
            # Models (ie building up Model object through composition.)
            # currently can't handle this case.
            continue
        p = PropertyNames.from_name(f.name)
        new_fields.append(f.evolve(name=p.private_name))
    return new_fields

def attrs_define(cls=None, **deco_kwargs):
    deco_kwargs.update({ # enforce default values for attrs class creation
        "slots": True,
        "kw_only": True,
        "field_transformer":_attr_field_transformer
    })
    if cls is None:
        # decorator called without arguments
        return functools.partial(attrs_define, **deco_kwargs)

    # attrs auto-generates an __init__ method; need to manually ensure that
    # super() is called.
    # https://www.attrs.org/en/stable/init.html#hooking-yourself-into-initialization
    def _pre_init(self):
        PYQT_QOBJECT.__init__(self)
    setattr(cls, "__attrs_pre_init__", _pre_init)

    # apply the attrs dataclass decorator, with descriptors and signals assigned
    # according to _attr_field_transformer()
    return attrs.define(cls, **deco_kwargs)

class MakeNotified:
    """From https://stackoverflow.com/a/66266877.
    Defines logic for triggering Signals on mutating operations on `list`- and
    `dict`-valued fields.
    """
    change_methods = {
        list: ['__delitem__', '__iadd__', '__imul__', '__setitem__', 'append',
               'extend', 'insert', 'pop', 'remove', 'reverse', 'sort'],
        dict: ['__delitem__', '__ior__', '__setitem__', 'clear', 'pop',
               'popitem', 'setdefault', 'update']
    }

    def __init__(self):
        if not hasattr(dict, '__ior__'):
            # Dictionaries don't have | operator in Python < 3.9.
            self.change_methods[dict].remove('__ior__')
        self.notified_class = {type_: self.make_notified_class(type_)
                               for type_ in [list, dict]}

    def __call__(self, seq, signal):
        """Returns a notifying version of the supplied list or dict."""
        notified_class = self.notified_class[type(seq)]
        notified_seq = notified_class(seq)
        notified_seq.signal = signal
        return notified_seq

    @classmethod
    def make_notified_class(cls, parent):
        notified_class = type(f'notified_{parent.__name__}', (parent,), {})
        for method_name in cls.change_methods[parent]:
            original = getattr(notified_class, method_name)
            notified_method = cls.make_notified_method(original, parent)
            setattr(notified_class, method_name, notified_method)
        return notified_class

    @staticmethod
    def make_notified_method(method, parent):
        @functools.wraps(method)
        def notified_method(self, *args, **kwargs):
            result = getattr(parent, method.__name__)(self, *args, **kwargs)
            self.signal.emit(self)
            return result
        return notified_method

_MAKE_NOTIFIED = MakeNotified()

class PropertyNames(collections.namedtuple(
    'PropertyNames',
    ('name', 'private_name', 'signal_name', 'slot_name')
)):
    """Use rigid naming conventions, defined in one place, for the naming of
    auto-generated Signals, Slots and other attributes.
    """
    __slots__ = ()

    @classmethod
    def from_name(cls, name):
        # the lstrip() is a hack to deal with attribute redefinition on class
        # inheritance; don't want to auto-generate x, _x, __x, ___x etc.
        name = name.lstrip('_')
        return cls(
            name = name,
            private_name = '_' + name,
            signal_name = name + '_update',
            slot_name = 'on_' + name + '_update'
        )

    @classmethod
    def from_private_name(cls, private_name):
        assert private_name.startswith('_')
        return cls.from_name(private_name)

def connect_signal(obj_w_signal, prop_name, slot):
    p = PropertyNames.from_name(prop_name)
    getattr(obj_w_signal, p.signal_name).connect(slot)

def connect_slot(signal, obj_w_slot, prop_name):
    p = PropertyNames.from_name(prop_name)
    signal.connect(getattr(obj_w_slot, p.slot_name))

_AUTOCONNECT_SIGNAL_NAMES = {
    QCheckBox: ("stateChanged", "setChecked"),
    QComboBox: ("activated", "setCurrentIndex"),
    QLineEdit: ("textEdited", "setText")
} # others?

def biconnect(view, model, model_prop_name):
    connected = False
    for k,v in _AUTOCONNECT_SIGNAL_NAMES.items():
        if issubclass(view, k):
            v_signal_name, v_slot_name = v
            connect_signal(model, model_prop_name, getattr(view, v_slot_name))
            connect_slot(getattr(view, v_signal_name), model, model_prop_name)
            connected = True
    if not connected:
        raise AttributeError

class PropertyWrapper(PYQT_PROPERTY):
    """Wrapper for pyqtProperty which automatically emits signal on field value
    change.
    """
    def __init__(self, type_, name, notify):
        # NB: pyqtProperty doesn't do anything with .notify; still need to
        # .emit() the signal manually
        super(PropertyWrapper, self).__init__(type_, self.getter, self.setter, notify=notify)
        self.name = name
        self.signal_type = type_

    @property
    def private_name(self):
        p = PropertyNames.from_name(self.name)
        return p.private_name

    @property
    def signal_name(self):
        p = PropertyNames.from_name(self.name)
        return p.signal_name

    def getter(self, instance):
        return getattr(instance, self.private_name)

    def setter(self, instance, value):
        signal = getattr(instance, self.signal_name)
        if type(value) in (list, dict):
            value = _MAKE_NOTIFIED(value, signal)
            signal.emit(value)
        else:
            # coerce from field's type
            coerce_old_val = self.signal_type(getattr(instance, self.private_name))
            coerce_val = self.signal_type(value)
            if coerce_old_val != coerce_val:
                signal.emit(coerce_val) # may be redundant
        setattr(instance, self.private_name, value)

_AUTOSIGNAL_TYPE_COERCE = {
    list: 'QVariantList', dict: 'QVariantMap',
    pathlib.Path: str, # need to understand typing of signals better
    enum.Enum: int
}

class AutoSignalSlotMetaclass(type(PYQT_QOBJECT)):
    """Metaclass for dynamically associating PyQt Properties and Signals with
    attrs fields.
    """
    def __new__(cls, name, bases, attrs_):
        if '__attrs_attrs__' not in attrs_:
            # first call, before attrs decorator; ordinary Object behavior
            return type.__new__(cls, name, bases, attrs_)

        # If we get here, attrs decorator has done its work -- need attrs slots=True!
        for f in attrs_['__attrs_attrs__']:
            signal_type = _AUTOSIGNAL_TYPE_COERCE.get(f.type, f.type)
            if attrs.has(f.type) or issubclass(f.type, PYQT_QOBJECT):
                # don't define new signals/slots for nested Model objects
                continue
            p = PropertyNames.from_private_name(f.name) # _attr_field_transformer remapped names
            if p.signal_name not in attrs_:
                # auto-generate signal
                signal = PYQT_SIGNAL(signal_type, name=p.signal_name)
                attrs_[p.signal_name] = signal
                attrs_[p.name] = PropertyWrapper(type_=signal_type, name=p.name, notify=signal)

            if p.slot_name not in attrs_:
                # auto-generate. Each slot has to be a unique callable, so we
                # have to define them because we're using a descriptor for attribute
                # access
                @PYQT_SLOT(signal_type)
                def _dummy_slot(self, value):
                    setattr(self, p.name, value)
                attrs_[p.slot_name] = _dummy_slot

        # hacky but necessary way to sync up associated Views with the Model. Model
        # needs to be instantiated before it's connect()ed to views, but this means
        # views don't know about inital values of model fields. To fix this, provide
        # a method to manually fire all _*_changed signals for all model fields.
        def _refresh(self):
            cls_ = type(self)
            for f in attrs.fields(cls_):
                p = PropertyNames.from_private_name(f.name) # _attr_field_transformer remapped names
                if hasattr(cls_, p.signal_name):
                    # signals are class attributes BUT need to call emit() on the instance
                    value = getattr(self, p.name)
                    getattr(self, p.signal_name).emit(value)
        attrs_["refresh"] = _refresh

        return super().__new__(cls, name, bases, attrs_)


class BaseModel(PYQT_QOBJECT, metaclass = AutoSignalSlotMetaclass):
    """Base class for our Model classes.
    """
    pass

class BaseController(PYQT_QOBJECT):
    """Base class for our Controller classes.
    """
    pass

@attrs_define
class MultiModel(PYQT_QOBJECT):
    """Wrapper for a collection of Models: maintains state of all models, but
    attributes are only looked up on the currently active Model.
    """
    multimodel_index: int = 0
    models: list = attrs.Factory(list)

    def __getattr__(self, name):
        """Pass through all attribute access to the currently selected Model.
        """
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, name)
        except AttributeError:
            return getattr(self.models[self.multimodel_index], name)

    def __setattr__(self, name, value):
        """Pass through all attribute access to the currently selected Model.
        """
        try:
            # Throws exception if not in prototype chain
            _ = object.__getattribute__(self, name)
        except AttributeError:
            try:
                setattr(self.models[self.multimodel_index], name, value)
            except Exception:
                raise AttributeError(name)
        else:
            object.__setattr__(self, name, value)

# ------------------------------------------------------------------------------

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
