#!/usr/bin/env python

import os.path
import sys

import pymol.Qt.QtWidgets as QtWidgets

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dir_name(this_dir))
import APBS_Qt_plugin.plugin as plugin
import APBS_Qt_plugin.util as util

PLUGIN_DIALOG = None

class App(QtWidgets.QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        if PLUGIN_DIALOG is None:
            import APBS_Qt_plugin.plugin as plugin
            PLUGIN_DIALOG = plugin.PluginController()
        PLUGIN_DIALOG.show()


if __name__ == '__main__':
    # set up logging: print any messages to PyMol terminal
    import logging
    _log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    try:
        if PLUGIN_DIALOG is None:
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


