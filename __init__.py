"""
Entry point: PyMOL plug-in registration

See https://pymolwiki.org/index.php/Plugins_Tutorial
"""

def __init_plugin__(app=None):
    """
    Add an entry to the PyMOL "Plugin" menu.
    """
    try:
        from pymol.plugins import addmenuitemqt
    except ModuleNotFoundError:
        print("APBS_Qt_Plugin: couldn't import pymol. Aborting.")
    addmenuitemqt('APBS Tools...', run_plugin_gui)

# global reference to avoid garbage collection of our dialog
PLUGIN_DIALOG = None

def run_plugin_gui():
    '''Open our custom dialog.
    '''
    import APBS_Qt_plugin.util as util
    global PLUGIN_DIALOG

    # set up logging: print any messages to PyMol terminal
    import logging
    _log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    try:
        if PLUGIN_DIALOG is None:
            import APBS_Qt_plugin.plugin as plugin
            PLUGIN_DIALOG = plugin.PluginController()
        PLUGIN_DIALOG.show()

    # handle uncaught exceptions
    except util.PluginDialogException as exc:
        import sys, traceback
        from pymol.Qt import QtWidgets

        QMB = QtWidgets.QMessageBox
        parent = QtWidgets.QApplication.focusWidget()
        msg = str(exc) or 'unknown error'
        msgbox = QMB(QMB.Critical, 'Error', msg, QMB.Close, parent)
        _, _, tb = sys.exc_info()
        msgbox.setDetailedText(''.join(traceback.format_tb(tb)))
        msgbox.exec_()
