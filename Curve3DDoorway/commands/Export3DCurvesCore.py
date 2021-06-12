# Author-kantoku
# Description-Export 3D Curves
# Fusion360API Python Addins

import adsk.core
import adsk.fusion
import platform

from ..apper import apper
from .. import config
from .Export3DCurvesFactry import Export3DCurvesFactry

class Export3DCurves(apper.Fusion360CommandBase):

    def on_preview(self, command, inputs, args, input_values):
        pass

    def on_destroy(self, command, inputs, reason, input_values):
        pass

    def on_input_changed(self, command, inputs, changed_input, input_values):
        pass

    def on_execute(self, command, inputs, args, input_values):
        Export3DCurvesFactry.execute()

    def on_create(self, command, inputs):
        pass