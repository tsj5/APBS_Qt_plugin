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
