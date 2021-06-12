# Author-kantoku
# Description-Import 3D Curves
# Fusion360API Python Addins

import adsk.core
import adsk.fusion
import platform

from ..apper import apper
from .. import config
from .Import3DCurvesFactry import Import3DCurvesFactry

from .ktkLanguageMessage import LangMsg
msgDict = {
    'Windows Only!' : 'ウィンドウズのみ使用できます!',
}
lm = LangMsg(msgDict, adsk.core.UserLanguages.JapaneseLanguage)


class Import3DCurves(apper.Fusion360CommandBase):

    def on_preview(self, command, inputs, args, input_values):
        pass

    def on_destroy(self, command, inputs, reason, input_values):
        pass

    def on_input_changed(self, command, inputs, changed_input, input_values):
        pass

    def on_execute(self, command, inputs, args, input_values):
        if platform.system() != 'Windows':
            ao = apper.AppObjects()
            ao.ui.messageBox(lm.sLng('Windows Only!'))
            return

        Import3DCurvesFactry.execute()

    def on_create(self, command, inputs):
        pass