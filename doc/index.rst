.. crtomo tools documentation master file, created by
   sphinx-quickstart on Tue Feb 21 17:06:04 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to crtomo tools's documentation!
========================================

This document describes the scripts and libraries of the crtomo_tools package.
These tools are written in the Python programming language and provide command
line tools for common tasks such as generating triangular finite-element meshes
for CRMod/CRTomo, or modifying existing grids.

Also included is the Python module *crtomo*, which aims at providing an
interface to all functions of CRMod and CRTomo. Thus, CRMod/CRTomo can be fully
controlled using Python. This also includes retrieving any data output produced
by either of the programs.

.. note::

    The Python abstraction is not yet finished, and is mostly worked on when
    the need arises.


Contents:

.. toctree::
   :maxdepth: 2

   contributing.rst
   theory/basics.rst
   crtomo/crtomo.rst
   grid_creation.rst
   _examples/index.rst
   scripts/grid_tools/modules.rst
   api/modules.rst

As short introduction to electrical modeling and inversion
----------------------------------------------------------

.. mermaid::

   flowchart LR
   mod
   mod("Modeling")
   inv
   inv("Inversion")
   mod --> |'forward modeling'| inv
   inv --> |'inverse step'| mod


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

