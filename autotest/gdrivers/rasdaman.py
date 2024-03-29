#!/usr/bin/env pytest
###############################################################################
# $Id$
#
# Project:  GDAL/OGR Test Suite
# Purpose:  rasdaman Testing.
# Author:   Even Rouault, <even dot rouault at spatialys.com>
#
###############################################################################
# Copyright (c) 2010, Even Rouault <even dot rouault at spatialys.com>
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

import gdaltest
import pytest

from osgeo import gdal

#
# The rasdaman DB must be created like this :
# cd $RASDAMAN_INSTALL_DIR/bin
# ./create_db.sh  (Note that the current user should have rights for creating a postgres database)
# ./start_rasdaman.sh
# ./insertdemo.sh localhost 7001 $RASDAMAN_INSTALL_DIR/share/rasdaman/examples/images rasadmin rasadmin

###############################################################################
#


def test_rasdaman_1():
    gdaltest.rasdamanDriver = gdal.GetDriverByName("RASDAMAN")
    if gdaltest.rasdamanDriver is None:
        pytest.skip()

    try:
        ds = gdal.Open(
            "rasdaman:query='select a[$x_lo:$x_hi,$y_lo:$y_hi] from rgb as a'"
        )
    except Exception:
        gdaltest.rasdamanDriver = None

    if ds is None:
        gdaltest.rasdamanDriver = None

    if gdaltest.rasdamanDriver is None:
        pytest.skip()

    cs = ds.GetRasterBand(1).Checksum()
    assert cs == 61774, "did not get expected checksum"


###############################################################################
# Test opening a non existing collection


def test_rasdaman_2():
    if gdaltest.rasdamanDriver is None:
        pytest.skip()

    ds = gdal.Open(
        "rasdaman:query='select a[$x_lo:$x_hi,$y_lo:$y_hi] from notexisting as a'"
    )
    assert ds is None


###############################################################################
# Test syntax error


def test_rasdaman_3():
    if gdaltest.rasdamanDriver is None:
        pytest.skip()

    ds = gdal.Open("rasdaman:query='select'")

    assert ds is None
