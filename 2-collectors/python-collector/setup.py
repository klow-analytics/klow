#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

version_file_path = os.path.join(
    os.path.dirname(__file__),
    'snowplow_tracker',
    '_version.py'
    )
exec(open(version_file_path).read(), {}, locals())
