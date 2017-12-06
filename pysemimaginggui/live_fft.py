#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemimaginggui.live_fft

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

FFT viewer script for SU-8230.
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
import logging
import os.path

# Third party modules.
import pyautogui
from PIL import Image, ImageOps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.fftpack import fft2, fftshift

# Local modules.

# Project modules.

# Globals and constants variables.


def find_micrograph():
    micrograph_location = (20, 200)
    path = os.path.join("data/images", "SU8230")
    file_path = os.path.join(path, "pc_sem_su8230_pause.png")
    logging.debug("pause file_path: %s (is file %s)", file_path, os.path.isfile(file_path))
    pause_location = pyautogui.locateOnScreen(file_path)
    logging.debug(pause_location)
    if pause_location is not None:
        micrograph_location = (pause_location[0], pause_location[1]+pause_location[3])

    file_path = os.path.join(path, "pc_sem_su8230_run.png")
    logging.debug("pause file_path: %s (is file %s)", file_path, os.path.isfile(file_path))
    run_location = pyautogui.locateOnScreen(file_path)
    logging.debug(run_location)
    if run_location is not None:
        micrograph_location = (run_location[0], run_location[1]+run_location[3])

    logging.info(micrograph_location)
    return micrograph_location


def display_fft(micrograph_location):
    fig = plt.figure()

    top_pixel = micrograph_location[0]+2
    left_pixel = micrograph_location[1]+2
    width_pixel = 800-10
    height_pixel = 560-10
    micrograph_image = pyautogui.screenshot(region=(top_pixel, left_pixel, width_pixel, height_pixel))
    micrograph_image = micrograph_image.convert("L")
    micrograph_image = fft2(micrograph_image)
    micrograph_image = fftshift(micrograph_image)
    micrograph_image = np.abs(micrograph_image) ** 2
    micrograph_image = np.log10(micrograph_image)

    fft_image = plt.imshow(micrograph_image, animated=True, cmap=plt.cm.Greys)
    plt.xticks([])
    plt.yticks([])

    plt.tight_layout()

    def updatefig(*args):
        micrograph_image = pyautogui.screenshot(region=(top_pixel, left_pixel, width_pixel, height_pixel))
        micrograph_image = micrograph_image.convert("L")

        micrograph_image = fft2(micrograph_image)
        micrograph_image = fftshift(micrograph_image)
        micrograph_image = np.abs(micrograph_image) ** 2
        micrograph_image = np.log10(micrograph_image)

        fft_image.set_array(micrograph_image)
        return fft_image,

    interval_ms = 20
    ani = animation.FuncAnimation(fig, updatefig, interval=interval_ms, blit=True)

    plt.show()


def run_live_fft():
    micrograph_location = find_micrograph()

    display_fft(micrograph_location)


if __name__ == "__main__":
    run_live_fft()
