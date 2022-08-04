# APBS_Qt_plugin

This is an **experimental** port of the [APBS Tools plugin](https://pymolwiki.org/index.php/Apbsplugin) for [PyMol](https://pymol.org/2/) version 2.x. It is **not** ready for production use; I'm writing it as an exercise to learn PyQt.

Note that this is *only* relevant for the open-source fork of PyMOL; this functionality is [included by default](https://pymolwiki.org/index.php/APBS_Electrostatics_Plugin) in the incentive fork of PyMOL provided by [Schrodinger](https://www.schrodinger.com).

## Background

The APBS (Adaptive Poisson-Boltzmann Solver) Tools plugin is used to compute macromolecular electrostatic charges and visualize this information as a potential surface in PyMOL. It does this by calling the [apbs](https://github.com/Electrostatics/apbs) code; optionally, [pdb2pqr](https://github.com/Electrostatics/pdb2pqr) is called to preprocess input files; see [poissonboltzmann.org](https://www.poissonboltzmann.org).

The current version of the plugin (version 2.1) was written against the `tkinter` GUI library used in PyMOL 1.x; version 2.x of PyMOL migrated to PyQt. There is [legacy support](https://pymolwiki.org/index.php/PluginArchitecture#init_plugin) for `tkinter`-based plugins (not implemented in the APBS Tools plugin), but I wanted to take this as an opportunity to update it to PyQt.

## Credits

The original APBS Tools plugin was written by Michael G. Lerner in 2009, with contributions from Heather A. Carlson and Warren L. DeLano. The current version is available [here](https://github.com/Pymol-Scripts/Pymol-script-repo/blob/master/plugins/apbsplugin.py).

Users of `apbs` and `pdb2pqr` are strongly encouraged to register their use at [poissonboltzmann.org](https://poissonboltzmann.us11.list-manage.com/subscribe), as this is key to securing funding for continued development of this software.

Citation for `apbs`:
&nbsp;Baker NA, Sept D, Joseph S, Holst MJ, McCammon JA. *Electrostatics of nanosystems: application to microtubules and the ribosome*. Proc. Natl. Acad. Sci. USA **98**, 10037-10041 (2001); [doi/10.1073/pnas.181342398](https://doi.org/10.1073/pnas.181342398); PMID: 11517324; PMCID: [PMC56910](http://www.ncbi.nlm.nih.gov/pmc/articles/pmc56910/).

Citation for `pdb2pqr`:
&nbsp;Dolinsky TJ, Nielsen JE, McCammon JA, Baker NA. *PDB2PQR: an automated pipeline for the setup, execution, and analysis of Poisson-Boltzmann electrostatics calculations.* Nucleic Acids Research *32* W665-W667 (2004). [doi/10.1093/nar/gkh381](10.1093/nar/gkh381); PMID: 15215472; PMCID: [PMC441519](http://www.ncbi.nlm.nih.gov/pmc/articles/pmc441519/).


