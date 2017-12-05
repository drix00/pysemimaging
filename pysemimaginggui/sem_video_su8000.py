#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemimaginggui.sem_video_su8000

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Video recording script for SU-8000.
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

# Third party modules.

# Local modules.

# Project modules.

# Globals and constants variables.
import logging

import pyautogui
from PIL import Image, ImageOps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.fftpack import fft2, fftshift
#plt.rcParams['animation.ffmpeg_path'] = '../bin/ffmpeg-3.2.4-win32-static/bin'
plt.rcParams['animation.ffmpeg_path'] = u'../bin/ffmpeg-3.2.4-win32-static/bin/ffmpeg.exe'

def find_micrograph():
    micrograph_location = (20, 200)
    pause_location = pyautogui.locateOnScreen("pc_sem_su8000_right_handle.png")
    logging.debug(pause_location)
    if pause_location is not None:
        micrograph_location = (pause_location[0], pause_location[1]+pause_location[3])

    logging.info(micrograph_location)
    return micrograph_location


def save_movie(micrograph_location):
    fig = plt.figure()

    top_pixel = micrograph_location[0]+2
    left_pixel = micrograph_location[1]+2
    width_pixel = 800
    height_pixel = 560
    micrograph_image = pyautogui.screenshot(region=(top_pixel, left_pixel, width_pixel, height_pixel))
    micrograph_image = micrograph_image.convert("L")

    fft_image = plt.imshow(micrograph_image, animated=True, cmap=plt.cm.Greys)
    plt.xticks([])
    plt.yticks([])

    plt.tight_layout()

    def updatefig(*args):
        micrograph_image = pyautogui.screenshot(region=(top_pixel, left_pixel, width_pixel, height_pixel))
        micrograph_image = micrograph_image.convert("L")

        fft_image.set_array(micrograph_image)
        return fft_image,

    interval_ms = 20
    ani = animation.FuncAnimation(fig, updatefig, interval=interval_ms, blit=True)

    FFwriter = animation.FFMpegWriter(fps=30, extra_args=['-vcodec', 'libx264'])
    ani.save('sem_movie.mp4', writer=FFwriter)
    plt.show()


def run_live_fft():
    micrograph_location = find_micrograph()

    save_movie(micrograph_location)


if __name__ == "__main__":
    run_live_fft()


