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
from pymol.Qt.QtWidgets import QWidget, QDialog, QGroupBox

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
        assert not attrs.has(f.type)
        # don't create a descriptor/signal for attributes that are other
        # Models (ie building up Model object through composition.)
        # currently can't handle this case.
        private_name = PropertyWrapper._private_from_public_name(f.name)
        new_fields.append(f.evolve(name=private_name))
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
        return cls.from_name(cls, private_name)

class PropertyWrapper(PYQT_PROPERTY):
    """Wrapper for pyqtProperty which automatically emits signal on field value
    change.
    """
    def __init__(self, type_, name, notify):
        super().__init__(type_, self.getter, self.setter, notify=notify)
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

class AutoSignalMetaclass(type(PYQT_QOBJECT)):
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
            p = PropertyNames.from_private_name(f.name) # _attr_field_transformer remapped names
            signal = PYQT_SIGNAL(signal_type, name=p.signal_name)
            attrs_[p.signal_name] = signal
            attrs_[p.name] = PropertyWrapper(type_=signal_type, name=p.name, notify=signal)

        # hacky but necessary way to sync up associated Views with the Model. Model
        # needs to be instantiated before it's connect()ed to views, but this means
        # views don't know about inital values of model fields. To fix this, provide
        # a method to manually fire all _*_changed signals for all model fields.
        def _on_connect(self):
            cls_ = type(self)
            for f in attrs.fields(cls_):
                p = PropertyNames.from_private_name(f.name) # _attr_field_transformer remapped names
                if hasattr(cls_, p.signal_name):
                    # signals are class attributes BUT need to call emit() on the instance
                    value = getattr(self, p.name)
                    getattr(self, p.signal_name).emit(value)
        attrs_["on_connect"] = _on_connect

        return super().__new__(cls, name, bases, attrs_)


class BaseModel(PYQT_QOBJECT, metaclass = AutoSignalMetaclass):
    """Base class for our Model classes.
    """
    pass

class MultiModel(PYQT_QOBJECT):
    """Wrapper for a collection of Models: maintains state of all models, but
    attributes are only looked up on the currently active Model.
    """
    _multimodel_index_changed = PYQT_SIGNAL(int)

    def __init__(self, models):
        super(MultiModel, self).__init__()
        self._multimodel_index = 0
        self.multimodel_index = PropertyWrapper(
            type_=int, name="multimodel_index", notify=self._multimodel_index_changed
        )
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

class AutoSlotMetaclass(type(PYQT_QOBJECT)):
    """Metaclass for dynamically associating PyQt Slots based on an associated Model.
    Model class taken from a class attribute named `_model_class`.
    """
    def __new__(cls, name, bases, attrs_):
        if '_model_class' not in attrs_:
            return super().__new__(cls, name, bases, attrs_)
        model_cls = attrs_['_model_class']
        if not hasattr(model_cls, '__attrs_attrs__'):
            return super().__new__(cls, name, bases, attrs_)

        for f in model_cls.__attrs_attrs__:
            p = PropertyNames.from_private_name(f.name) # _attr_field_transformer remapped names
            signal_type = getattr(model_cls, p.name).signal_type

            @PYQT_SLOT(signal_type)
            def _slot_with_dummy_name(self, value):
                setattr(self.model, p.name, value)

            attrs_[p.slot_name] = _slot_with_dummy_name
        return super().__new__(cls, name, bases, attrs_)

class BaseController(PYQT_QOBJECT, metaclass = AutoSlotMetaclass):
    """Base class for our Controller classes.
    """
    def __init__(self, model, view):
        super(BaseController, self).__init__()
        self.model = model
        self.view = view

class BaseWidgetView(QWidget):
    def __init__(self, ui_cls):
        super(BaseWidgetView, self).__init__()
        self._ui = ui_cls()
        self._ui.setupUi(self)

class BaseDialogView(QDialog):
    def __init__(self, ui_cls):
        super(BaseDialogView, self).__init__()
        self._ui = ui_cls()
        self._ui.setupUi(self)

class BaseGroupBoxView(QGroupBox):
    def __init__(self, ui_cls):
        super(BaseGroupBoxView, self).__init__()
        self._ui = ui_cls()
        self._ui.setupUi(self)

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
