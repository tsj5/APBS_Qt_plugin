# APBS_Qt_plugin

This is an **experimental** port of the [APBS Tools plugin](https://pymolwiki.org/index.php/Apbsplugin) for [PyMol](https://pymol.org/2/) version 2.x. It's under development and **not** ready for production use; I'm writing it as an exercise to learn PyQt.

Note that this is *only* relevant for the open-source fork of PyMOL; this functionality is [included by default](https://pymolwiki.org/index.php/APBS_Electrostatics_Plugin) in the incentive fork of PyMOL provided by [Schrodinger](https://www.schrodinger.com).

## Background

The APBS (Adaptive Poisson-Boltzmann Solver) Tools plugin is used to compute macromolecular electrostatic charges and visualize this information as a potential surface in PyMOL. It does this by calling the [apbs](https://github.com/Electrostatics/apbs) code; optionally, [pdb2pqr](https://github.com/Electrostatics/pdb2pqr) is called to preprocess input files; see [poissonboltzmann.org](https://www.poissonboltzmann.org).

The current version of the plugin (version 2.1) was written against the `tkinter` GUI library used in PyMOL 1.x; version 2.x of PyMOL migrated to PyQt. There is [legacy support](https://pymolwiki.org/index.php/PluginArchitecture#init_plugin) for `tkinter`-based plugins (not implemented in the APBS Tools plugin), but I wanted to take this as an opportunity to update it to PyQt.

## Installation

Since development is still in progress, currently the only supported installation method is through conda. If conda isn't installed, download [Miniconda3](https://docs.conda.io/en/latest/miniconda.html).

If you're installing on an arm-based mac, you'll need
```
export CONDA_SUBDIR="osx-64"
```
since arm-based builds of `apbs` aren't available on conda (and my attempts to build from source have failed so far.) Note that conda packages for `apbs` have fallen behind tagged releases.

Then do
```
conda env create -f=conda.yml; conda activate APBS_Qt_Plugin
```

To add the plugin in PyMol, select the `APBS_Qt_plugin` directory in the [Plugins manager](https://pymolwiki.org/index.php/Plugin_Manager).

## Design considerations

I've attempted to reorganize the code along the lines of the (hierarchical) Model-View-Controller pattern. This is *absolutely* overkill for an application whose scope is this small, but I wanted to use the project as a way to explore coding practices that scale to large applications.

At least subjectively, this has felt like "going against the grain" of PyQt's intentions. Qt's use of Model/View terminology refers to something subtantively different, as clarified in [this SO post](https://stackoverflow.com/questions/5543198/why-qt-is-misusing-model-view-terminology). UI widgets operate according to an event-driven paradigm using [signals and slots](https://doc.qt.io/qtforpython/overviews/signalsandslots.html), but neither PyQt's `*Model` objects or the base data types wrapped from C++ Qt have predefined signals or slots: these need to be defined manually on the Model class (as in [this example](https://stackoverflow.com/a/26699122)), which results in boilerplate code and redundant definitions.

The solution I've used here (perhaps the most novel part of this project) is to combine a solution proposed [here](https://stackoverflow.com/a/66266877) with the [attrs](https://www.attrs.org/en/stable/) package to automate defintion of Signals and Slots on the Model classes. This is done in [util.py](https://github.com/tsj5/APBS_Qt_plugin/blob/main/APBS_Qt_plugin/util.py).

## Credits

The original APBS Tools plugin was written by Michael G. Lerner in 2009, with contributions from Heather A. Carlson and Warren L. DeLano. The current version is available [here](https://github.com/Pymol-Scripts/Pymol-script-repo/blob/master/plugins/apbsplugin.py).

Users of `apbs` and `pdb2pqr` are strongly encouraged to register their use at [poissonboltzmann.org](https://poissonboltzmann.us11.list-manage.com/subscribe), as this is key to securing funding for continued development of this software.

Citation for `apbs`:
&nbsp;Baker NA, Sept D, Joseph S, Holst MJ, McCammon JA. *Electrostatics of nanosystems: application to microtubules and the ribosome*. Proc. Natl. Acad. Sci. USA **98**, 10037-10041 (2001); [doi/10.1073/pnas.181342398](https://doi.org/10.1073/pnas.181342398); PMID: 11517324; PMCID: [PMC56910](http://www.ncbi.nlm.nih.gov/pmc/articles/pmc56910/).

Citation for `pdb2pqr`:
&nbsp;Dolinsky TJ, Nielsen JE, McCammon JA, Baker NA. *PDB2PQR: an automated pipeline for the setup, execution, and analysis of Poisson-Boltzmann electrostatics calculations.* Nucleic Acids Research **32** W665-W667 (2004). [doi/10.1093/nar/gkh381](10.1093/nar/gkh381); PMID: 15215472; PMCID: [PMC441519](http://www.ncbi.nlm.nih.gov/pmc/articles/pmc441519/).


