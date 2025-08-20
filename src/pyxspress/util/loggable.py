"""
Loggable module

Defines a class interface for module-level logging
"""

import logging

from pyxspress.util.util import module_name


class Loggable:
    def __init__(self):
        """Create the class with a module logger"""
        self.logger = logging.getLogger(f"{module_name}.{self.__class__.__name__}")
