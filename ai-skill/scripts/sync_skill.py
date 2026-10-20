#!/usr/bin/env python3
"""Compatibility entry point: regenerate the full native bundle and source state."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('build_bundle.py')), run_name='__main__')
