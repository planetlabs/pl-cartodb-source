#!/usr/bin/env pytest
# -*- coding: utf-8 -*-
###############################################################################
# $Id$
#
# Project:  GDAL/OGR Test Suite
# Purpose:  gdal_pansharpen testing
# Author:   Even Rouault <even.rouault at spatialys.com>
#
###############################################################################
# Copyright (c) 2015, Even Rouault <even.rouault at spatialys.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################


import pytest
import test_py_scripts

from osgeo import gdal

###############################################################################
# Simple test


def test_gdal_pansharpen_1():

    script_path = test_py_scripts.get_py_script("gdal_pansharpen")
    if script_path is None:
        pytest.skip()

    src_ds = gdal.Open(test_py_scripts.get_data_path("gdrivers") + "small_world.tif")
    src_data = src_ds.GetRasterBand(1).ReadRaster()
    gt = src_ds.GetGeoTransform()
    wkt = src_ds.GetProjectionRef()
    src_ds = None
    pan_ds = gdal.GetDriverByName("GTiff").Create("tmp/small_world_pan.tif", 800, 400)
    gt = [gt[i] for i in range(len(gt))]
    gt[1] *= 0.5
    gt[5] *= 0.5
    pan_ds.SetGeoTransform(gt)
    pan_ds.SetProjection(wkt)
    pan_ds.GetRasterBand(1).WriteRaster(0, 0, 800, 400, src_data, 400, 200)
    pan_ds = None

    test_py_scripts.run_py_script(
        script_path,
        "gdal_pansharpen",
        " tmp/small_world_pan.tif "
        + test_py_scripts.get_data_path("gdrivers")
        + "small_world.tif tmp/out.tif",
    )

    ds = gdal.Open("tmp/out.tif")
    cs = [ds.GetRasterBand(i + 1).Checksum() for i in range(ds.RasterCount)]
    ds = None
    gdal.GetDriverByName("GTiff").Delete("tmp/out.tif")

    assert cs in ([4735, 10000, 9742], [4731, 9991, 9734])  # s390x or graviton2


###############################################################################
# Full options


def test_gdal_pansharpen_2():

    script_path = test_py_scripts.get_py_script("gdal_pansharpen")
    if script_path is None:
        pytest.skip()

    test_py_scripts.run_py_script(
        script_path,
        "gdal_pansharpen",
        " -q -b 3 -b 1 -bitdepth 8 -threads ALL_CPUS -spat_adjust union -w 0.33333333333333333 -w 0.33333333333333333 -w 0.33333333333333333 -of VRT -r cubic tmp/small_world_pan.tif "
        + test_py_scripts.get_data_path("gdrivers")
        + "small_world.tif,band=1 "
        + test_py_scripts.get_data_path("gdrivers")
        + "small_world.tif,band=2 "
        + test_py_scripts.get_data_path("gdrivers")
        + "small_world.tif,band=3 tmp/out.vrt",
    )

    ds = gdal.Open("tmp/out.vrt")
    cs = [ds.GetRasterBand(i + 1).Checksum() for i in range(ds.RasterCount)]
    ds = None
    gdal.GetDriverByName("VRT").Delete("tmp/out.vrt")

    assert cs in ([9742, 4735], [9734, 4731])  # s390x or graviton2


###############################################################################
# Cleanup


def test_gdal_pansharpen_cleanup():

    script_path = test_py_scripts.get_py_script("gdal_pansharpen")
    if script_path is None:
        pytest.skip()

    gdal.GetDriverByName("GTiff").Delete("tmp/small_world_pan.tif")
