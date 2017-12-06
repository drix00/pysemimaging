#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemimaginggui

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Main package of the project.
"""

###############################################################################
# GUI for pySEM-EELS project.
# Copyright (C) 2017  Hendrix Demers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

# Standard library modules.
import os.path
import logging

# Third party modules.

# Local modules.

# Project modules.

# Globals and constants variables.
#: Maintainer of the project.
author = """Hendrix Demers"""
#: Email of the maintainer of the project.
email = 'hendrix.demers@mail.mcgill.ca'
version = '0.1.0'
"""
Version of the project.

.. note::
    The version of the project should be changed here.

"""


def get_current_module_path(module_filepath, relative_path=""):
    """
    Return the current module path by using :py:obj:`__file__` special module variable.

    An example of usage::

        module_path = get_current_module_path(__file__)

    :param str module_filepath: Pass :py:obj:`__file__` to get the current module path
    :param str relative_path: Optional parameter to return a path relative to the module path
    :return: a path, either the module path or a relative path from the module path
    :rtype: str
    """
    base_path = os.path.dirname(module_filepath)
    logging.debug(base_path)

    file_path = os.path.join(base_path, relative_path)
    logging.debug(file_path)
    file_path = os.path.normpath(file_path)

    return file_path
