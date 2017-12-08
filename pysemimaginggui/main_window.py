#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemeelsgui.tools.element_view_script
   :synopsis: GUI to process EELS files in batch mode.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

GUI to process EELS files in batch mode.
"""

###############################################################################
# Copyright 2017 Hendrix Demers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

# Standard library modules.
import os.path
import logging
import time
import six
if six.PY3:
    from tkinter import ttk
    from tkinter import filedialog, N, W, E, S, StringVar, BooleanVar, IntVar, DoubleVar, Tk, DISABLED, NORMAL
elif six.PY2:
    import ttk
    from Tkinter import N, W, E, S, StringVar, BooleanVar, IntVar, DoubleVar, Tk, DISABLED, NORMAL
    import tkFileDialog as filedialog

# Third party modules.
import pyautogui
from PIL import Image, ImageOps
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.fftpack import fft2, fftshift

# Local modules.

# Project modules.
from pysemimaginggui import get_current_module_path

# Globals and constants variables.


def get_log_file_path():
    path = get_current_module_path(__file__, "../log")
    logging.debug("log_file_path: %s", path)
    if not os.path.isdir(path):
        os.makedirs(path)

    return path


def get_images_path():
    path = get_current_module_path(__file__, "../data/images")
    logging.debug("images_path: %s", path)

    return path


def setup_ffmpeg_path(file_path=None):
    if file_path is None:
        path = get_current_module_path(__file__, u"../bin/ffmpeg-3.2.4-win32-static/bin")
        file_path = os.path.join(path, u"ffmpeg.exe")

    plt.rcParams['animation.ffmpeg_path'] = file_path


def get_ffmpeg_path():
    file_path = plt.rcParams['animation.ffmpeg_path']
    return file_path


def setup_logger():
    new_logger = logging.getLogger()
    new_logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    log_format = '%(asctime)s : %(name)-40s : %(levelname)-10s : %(message)s'
    formatter = logging.Formatter(log_format)

    ch.setFormatter(formatter)

    new_logger.addHandler(ch)

    path = get_log_file_path()
    log_file_path = os.path.join(path, "{}.log".format("sem_imaging"))
    fh = logging.FileHandler(log_file_path)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    new_logger.addHandler(fh)

    return new_logger


logger = setup_logger()


class TkMainGui(ttk.Frame):
    def __init__(self, root):
        ttk.Frame.__init__(self, root, padding="3 3 12 12")

        setup_ffmpeg_path()
        self.ffmpeg_path = StringVar()
        self.ffmpeg_path.set(get_ffmpeg_path())

        logger.debug("Create main frame")
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        logger.debug("Create variable")

        self.instrument = StringVar()

        self.is_sem_image = BooleanVar()
        self.is_sem_image.set(False)
        self.sem_image_location = StringVar()
        self.sem_image_width = IntVar()
        self.sem_image_width.set(800)
        self.sem_image_height = IntVar()
        self.sem_image_height.set(560)

        self.frame_interval_ms = IntVar()
        self.frame_interval_ms.set(250)

        self.video_acquisition_time_s = IntVar()
        self.video_acquisition_time_s.set(15)

        self.results_text = StringVar()

        widget_width = 40

        row_id = 0

        logger.debug("Create instrument selection")
        values = self.find_all_instruments()
        row_id += 1
        instrument_label = ttk.Label(self, width=widget_width, text="Instrument: ", state="readonly")
        instrument_label.grid(column=2, row=row_id, sticky=(W, E))
        instrument_entry = ttk.Combobox(self, width=widget_width, textvariable=self.instrument,
                                              values=values)
        instrument_entry.grid(column=3, row=row_id, sticky=(W, E))
        self.instrument.set(values[-1])

        logger.debug("Create Find SEM image")
        row_id += 1
        ttk.Button(self, width=widget_width, text="Find SEM image", command=self.find_sem_image).grid(column=3, row=row_id, sticky=W)
        row_id += 1
        ttk.Checkbutton(self, width=widget_width, text="SEM image", variable=self.is_sem_image, state=DISABLED).grid(column=3, row=row_id, sticky=(W, E))
        row_id += 1
        sem_image_location_label = ttk.Label(self, width=widget_width, textvariable=self.sem_image_location, state="readonly")
        sem_image_location_label.grid(column=3, row=row_id, sticky=(W, E))
        self.micrograph_location = None

        logger.debug("Create sem image width label and edit entry")
        row_id += 1
        sem_image_width_label = ttk.Label(self, width=widget_width, text="Width: ", state="readonly")
        sem_image_width_label.grid(column=2, row=row_id, sticky=(W, E))
        sem_image_width_entry = ttk.Entry(self, width=widget_width, textvariable=self.sem_image_width)
        sem_image_width_entry.grid(column=3, row=row_id, sticky=(W, E))

        logger.debug("Create sem image height label and edit entry")
        row_id += 1
        sem_image_height_label = ttk.Label(self, width=widget_width, text="Height: ", state="readonly")
        sem_image_height_label.grid(column=2, row=row_id, sticky=(W, E))
        sem_image_height_entry = ttk.Entry(self, width=widget_width, textvariable=self.sem_image_height)
        sem_image_height_entry.grid(column=3, row=row_id, sticky=(W, E))

        logger.debug("Create frame interval label and edit entry")
        row_id += 1
        frame_interval_label = ttk.Label(self, width=widget_width, text="Frame interval (ms): ", state="readonly")
        frame_interval_label.grid(column=2, row=row_id, sticky=(W, E))
        frame_interval_entry = ttk.Entry(self, width=widget_width, textvariable=self.frame_interval_ms)
        frame_interval_entry.grid(column=3, row=row_id, sticky=(W, E))

        logger.debug("Setup ffmpeg path")
        row_id += 1
        ffmpeg_path_label = ttk.Label(self, width=widget_width, wraplength=widget_width*5, textvariable=self.ffmpeg_path, state="readonly")
        ffmpeg_path_label.grid(column=2, row=row_id, sticky=(W, E), rowspan=4)
        ffmpeg_path_button = ttk.Button(self, width=widget_width, text="Setup ffmpeg path", command=self.setup_ffmpeg_path, state=NORMAL)
        ffmpeg_path_button.grid(column=3, row=row_id, sticky=W, rowspan=4)
        row_id += 3

        logger.debug("Create video acquisition time label and edit entry")
        row_id += 1
        video_acquisition_time_label = ttk.Label(self, width=widget_width, text="Video acquisition time (s): ", state="readonly")
        video_acquisition_time_label.grid(column=2, row=row_id, sticky=(W, E))
        video_acquisition_time_entry = ttk.Entry(self, width=widget_width, textvariable=self.video_acquisition_time_s)
        video_acquisition_time_entry.grid(column=3, row=row_id, sticky=(W, E))

        logger.debug("Take micrograph screenshot")
        row_id += 1
        self.screenshot_button = ttk.Button(self, width=widget_width, text="Take micrograph screenshot", command=self.take_sem_image_screenshot, state=DISABLED)
        self.screenshot_button.grid(column=3, row=row_id, sticky=W)

        logger.debug("Compute micrograph FT live")
        row_id += 1
        self.sem_fft_button = ttk.Button(self, width=widget_width, text="Compute micrograph FT live", command=self.compute_micrograph_fft, state=DISABLED)
        self.sem_fft_button.grid(column=3, row=row_id, sticky=W)

        logger.debug("Acquire video")
        row_id += 1
        self.sem_video_button = ttk.Button(self, width=widget_width, text="Acquire video", command=self.acquire_sem_video, state=DISABLED)
        self.sem_video_button.grid(column=3, row=row_id, sticky=W)

        logger.debug("Show status")
        row_id += 1
        results_label = ttk.Label(self, textvariable=self.results_text, state="readonly")
        results_label.grid(column=2, row=row_id, sticky=(W, E))

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # basename_entry.focus()
        self.results_text.set("Ready")

    def find_sem_image(self):
        logging.debug("find_sem_image")
        self.results_text.set("Start find sem image")
        micrograph_location = None
        self.is_sem_image = False
        self.screenshot_button.config(state=DISABLED)
        self.sem_fft_button.config(state=DISABLED)
        self.sem_video_button.config(state=DISABLED)

        path = os.path.join(get_images_path(), self.instrument.get())

        file_path = os.path.join(path, "pc_sem_su8230_pause.png")
        logging.debug("pause file_path: %s (is file %s)", file_path, os.path.isfile(file_path))
        pause_location = pyautogui.locateOnScreen(file_path)
        logging.debug("pause_location: %s", pause_location)
        if pause_location is not None:
            micrograph_location = (pause_location[0], pause_location[1]+pause_location[3])

        file_path = os.path.join(path, "pc_sem_su8230_pause.png")
        logging.debug("run file_path: %s (is file %s)", file_path, os.path.isfile(file_path))
        run_location = pyautogui.locateOnScreen(file_path)
        logging.debug("run_location: %s", run_location)
        if run_location is not None:
            micrograph_location = (run_location[0], run_location[1]+run_location[3])

        if micrograph_location is not None:
            self.micrograph_location = (micrograph_location[0]-2, micrograph_location[1]+1)
            self.is_sem_image = True
            self.sem_image_location.set("Location: ({}, {})".format(*self.micrograph_location))
            self.screenshot_button.config(state=NORMAL)
            self.sem_fft_button.config(state=NORMAL)
            self.sem_video_button.config(state=NORMAL)

        logging.info("micrograph_location: %s", self.micrograph_location)
        self.results_text.set("Stop find sem image")

    def take_sem_image_screenshot(self):
        logging.debug("take_sem_image_screenshot")
        self.results_text.set("Take SEM screenshot")

        fig = plt.figure()

        top_pixel = self.micrograph_location[0]
        left_pixel = self.micrograph_location[1]
        width_pixel = self.sem_image_width.get()
        height_pixel = self.sem_image_height.get()
        micrograph_image = pyautogui.screenshot(region=(top_pixel, left_pixel, width_pixel, height_pixel))
        logging.info("Screenshot format: %s; size: %s; mode: %s", micrograph_image.format, micrograph_image.size, micrograph_image.mode)
        micrograph_image.save("screenshot.png")

        # micrograph_image = micrograph_image.convert("L")
        micrograph_image = micrograph_image.convert("F")

        # micrograph_image = np.asarray(micrograph_image, dtype=np.float32)
        micrograph_image = np.asarray(micrograph_image)
        logging.info("micrograph_image shape: %s; dtype: %s", micrograph_image.shape, micrograph_image.dtype)

        fft_image = plt.imshow(1.0 - micrograph_image, cmap=plt.cm.binary)
        # fft_image = plt.imshow(micrograph_image)
        plt.xticks([])
        plt.yticks([])

        plt.tight_layout()

        plt.show()

    def compute_micrograph_fft(self):
        logging.debug("compute_micrograph_fft")
        self.results_text.set("Compute micrograph fft")

        fig = plt.figure()

        top_pixel = self.micrograph_location[0]
        left_pixel = self.micrograph_location[1]
        width_pixel = self.sem_image_width.get()
        height_pixel = self.sem_image_height.get()
        micrograph_image = pyautogui.screenshot(region=(top_pixel, left_pixel, width_pixel, height_pixel))
        logging.info("Screenshot format: %s; size: %s; mode: %s", micrograph_image.format, micrograph_image.size,
                     micrograph_image.mode)
        # micrograph_image.save("screenshot.png")

        micrograph_image = micrograph_image.convert("F")
        micrograph_image = np.asarray(micrograph_image)

        fft_micrograph_image = fft2(micrograph_image)
        fft_micrograph_image = fftshift(fft_micrograph_image)
        fft_micrograph_image = np.abs(fft_micrograph_image) ** 2
        fft_micrograph_image = np.log10(fft_micrograph_image)

        logging.info("micrograph_image shape: %s; dtype: %s", micrograph_image.shape, micrograph_image.dtype)

        fft_image = plt.imshow(fft_micrograph_image, animated=True)

        plt.xticks([])
        plt.yticks([])

        plt.tight_layout()

        def update_figure(*args):
            micrograph_image = pyautogui.screenshot(region=(top_pixel, left_pixel, width_pixel, height_pixel))
            micrograph_image = micrograph_image.convert("F")
            micrograph_image = np.asarray(micrograph_image)

            fft_micrograph_image = fft2(micrograph_image)
            fft_micrograph_image = fftshift(fft_micrograph_image)
            fft_micrograph_image = np.abs(fft_micrograph_image) ** 2
            fft_micrograph_image = np.log10(fft_micrograph_image)

            fft_image.set_array(fft_micrograph_image)

            return fft_image,

        interval_ms = self.frame_interval_ms.get()
        ani = animation.FuncAnimation(fig, update_figure, interval=interval_ms, blit=True)

        plt.show()

    def find_all_instruments(self):
        logging.debug("find_all_instruments")

        image_folder = get_images_path()
        instrument_folders = os.listdir(image_folder)
        logging.debug("instrument_folders: %s", instrument_folders)

        return instrument_folders

    def acquire_sem_video(self):
        logging.debug("acquire_sem_video")
        self.results_text.set("Acquire micrograph video")

        number_frames = int(self.video_acquisition_time_s.get() / (self.frame_interval_ms.get() * 1e-3))
        frame_per_second = 1.0 / (self.frame_interval_ms.get() * 1e-3)

        video_file_path = filedialog.asksaveasfilename(title="Select the video filename", filetypes=[("video file", "*.mp4")])

        fig = plt.figure()

        top_pixel = self.micrograph_location[0]
        left_pixel = self.micrograph_location[1]
        width_pixel = self.sem_image_width.get()
        height_pixel = self.sem_image_height.get()
        micrograph_image = pyautogui.screenshot(region=(top_pixel, left_pixel, width_pixel, height_pixel))
        micrograph_image = micrograph_image.convert("F")
        micrograph_image = np.asarray(micrograph_image)

        sem_image_plot = plt.imshow(1.0-micrograph_image, animated=True, cmap=plt.cm.Greys)
        plt.xticks([])
        plt.yticks([])

        plt.tight_layout()

        def updatefig(*args):
            update_image = pyautogui.screenshot(region=(top_pixel, left_pixel, width_pixel, height_pixel))
            update_image = update_image.convert("F")
            update_image = np.asarray(update_image)

            sem_image_plot.set_array(1.0-update_image)
            return sem_image_plot,

        interval_ms = self.frame_interval_ms.get()
        # ani = animation.FuncAnimation(fig, updatefig, interval=interval_ms, blit=True, frames=number_frames)
        ani = animation.FuncAnimation(fig, updatefig, interval=interval_ms, blit=False, save_count=number_frames)

        # FFwriter = animation.FFMpegWriter(fps=30, extra_args=['-vcodec', 'libx264'])
        FFwriter = animation.FFMpegWriter(fps=frame_per_second, extra_args=['-vcodec', 'libx264'])
        ani.save(video_file_path, writer=FFwriter)
        self.results_text.set("Stop micrograph video")

    def setup_ffmpeg_path(self):
        logging.debug("setup_ffmpeg_path")
        self.results_text.set("Setup ffmpeg path")

        path = os.path.dirname(get_ffmpeg_path())
        file_path = filedialog.askopenfilename(title="Select the ffmpeg file", filetypes=[("executable file", "*.exe")],
                                   initialdir=path, initialfile="ffmpeg.exe")
        logger.debug("Selected ffmpeg file path: %s", file_path)
        self.ffmpeg_path.set(file_path)
        setup_ffmpeg_path(file_path)


def main_gui():
    logger.debug("main_gui")

    logger.debug("Create root")
    root = Tk()
    root.title("Interacting with PC-SEM with Python")
    TkMainGui(root).pack()

    logger.debug("Mainloop")
    root.mainloop()


if __name__ == '__main__':  # pragma: no cover
    main_gui()
