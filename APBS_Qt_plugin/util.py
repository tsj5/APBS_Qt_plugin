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

from pymol.Qt import (QtCore, QtWidgets)

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

class PropertyNames(collections.namedtuple(
    'PropertyNames',
    ('name', 'signal_name', 'slot_name')
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
            signal_name = name + '_update',
            slot_name = 'on_' + name + '_update'
        )

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

def attr_setter_emit(obj, attr_obj, value):
    """Emit corresponding Signal when field (attrs Attribute) is set to a new
    value.
    """
    p = PropertyNames.from_name(attr_obj.name)
    signal = getattr(obj, p.signal_name)
    if type(value) in (list, dict):
        value = _MAKE_NOTIFIED(value, signal)
        signal.emit(value)
    else:
        # coerce from field's type
        # TODO: case when Signal is a tupe of values?
        old_val = getattr(obj, attr_obj.name)
        if old_val != value:
            obj.wrapped_emit(p.name, value)
    return value

def _attr_field_transformer(cls, fields):
    """Insert `attr_setter_emit` into list of methods called when field (attrs
    Attribute) is set to a new value.
    """
    new_fields = []
    for f in fields:
        if attrs.has(f.type) or issubclass(f.type, PYQT_QOBJECT):
            new_fields.append(f) # no-op for fields that are a composition of other Models
            continue

        if f.on_setattr:
            new_setattr = attrs.setters.pipe(
                attrs.setters.convert,
                attrs.setters.validate,
                f.on_setattr,
                attr_setter_emit
            )
        else:
            new_setattr = attrs.setters.pipe(
                attrs.setters.convert,
                attrs.setters.validate,
                attr_setter_emit
            )
        new_fields.append(f.evolve(on_setattr=new_setattr))
    return new_fields

def attrs_define(cls=None, **deco_kwargs):
    """Wraps the attrs `define` class decorator to enforce required settings for
    attrs class creation.
    """
    if not deco_kwargs.get('slots', True):
        # slots = True necessary, otherwise for some reason metaclass isn't picked up
        raise ValueError("Model classes aren't slots-based, but require slots=True")
    deco_kwargs['slots'] = True

    if not deco_kwargs.get('kw_only', True):
        # kw_only = True needed for sane __init__ signature under class inheritance
        raise ValueError("Model class init must be kwarg-only")
    deco_kwargs['kw_only'] = True

    if not deco_kwargs.get('init', True):
        raise ValueError("Define init by inheriting from util.BaseModel")
    deco_kwargs['init'] = True

    deco_kwargs['field_transformer'] = _attr_field_transformer

    if cls is None:
        # decorator called without arguments
        return functools.partial(attrs_define, **deco_kwargs)

    # apply the original attrs dataclass decorator
    return attrs.define(cls, **deco_kwargs)

_AUTOSIGNAL_TYPE_COERCE = {
    list: 'QVariantList', dict: 'QVariantMap',
    pathlib.Path: str, # need to understand typing of signals better
    enum.Enum: int
}

class AutoSignalSlotMetaclass(type(PYQT_QOBJECT)):
    """Metaclass for dynamically associating PyQt Properties and Signals with
    attrs fields. Based on https://stackoverflow.com/a/66266877.
    """
    def __new__(cls, name, bases, attrs_):
        if '__attrs_attrs__' in attrs_:
            # with slots=True, we get called twice. First call is before attrs
            # decorator so we need to pass through; make definitions on second call.

            for f in attrs_['__attrs_attrs__']:
                signal_type = _AUTOSIGNAL_TYPE_COERCE.get(f.type, f.type)
                if attrs.has(f.type) or issubclass(f.type, PYQT_QOBJECT):
                    # don't define new signals/slots for nested Model objects
                    continue

                p = PropertyNames.from_name(f.name)
                if p.signal_name not in attrs_:
                    # auto-generate signal
                    attrs_[p.signal_name] = PYQT_SIGNAL(signal_type, name=p.signal_name)

                if p.slot_name not in attrs_:
                    # auto-generate slot. Each slot has to be a unique callable with specific
                    # signature, so we can't use stuff on PropertyWrapper and instead
                    # need to define new, separate setter methods as synonyms.
                    @PYQT_SLOT(signal_type)
                    def _dummy_slot(self, value):
                        setattr(self, p.name, value)
                    attrs_[p.slot_name] = _dummy_slot

        return super(AutoSignalSlotMetaclass, cls).__new__(cls, name, bases, attrs_)

class BaseModel(PYQT_QOBJECT, metaclass = AutoSignalSlotMetaclass):
    """Base class for our Model classes.
    """
    def __attrs_pre_init__(self, *args, **kwargs):
        super().__init__() # required to call init on QObject

    def wrapped_emit(self, name, value):
        p = PropertyNames.from_name(name)
        signal = getattr(self, p.signal_name, None)
        if signal:
            signal_type = signal.type
            if hasattr(value, "coerce_to_signal"):
                val = value.coerce_to_signal(signal_type)
            else:
                val = signal_type(value)
            signal.emit(val)

    def refresh(self):
        """Hacky but necessary way to sync up associated Views with the Model. Model
        needs to be instantiated before it's connect()ed to views, but this means
        views don't know about inital values of model fields. To fix this, provide
        a method to manually fire all *_update signals for all model fields.
        """
        for f in attrs.fields(type(self)):
            self.wrapped_emit(f.name, getattr(self, f.name))


def connect_signal(obj_w_signal, prop_name, slot):
    p = PropertyNames.from_name(prop_name)
    getattr(obj_w_signal, p.signal_name).connect(slot)

def connect_slot(signal, obj_w_slot, prop_name):
    p = PropertyNames.from_name(prop_name)
    signal.connect(getattr(obj_w_slot, p.slot_name))

_AUTOCONNECT_SIGNAL_NAMES = {
    QtWidgets.QCheckBox: ("clicked", "setChecked"), # bool
    QtWidgets.QComboBox: ("activated", "setCurrentIndex"), # int
    QtWidgets.QLineEdit: ("textEdited", "setText") # str
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
