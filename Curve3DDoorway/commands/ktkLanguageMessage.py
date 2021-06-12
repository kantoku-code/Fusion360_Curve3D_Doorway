#Author-kantoku
#Description-Support class for multilingualization
#Fusion360API Python

import adsk.core


class LangMsg:

    def __init__(self, dict, language :adsk.core.UserLanguages = None):
        self.app = adsk.core.Application.get()
        if not language:
            self.language = self.app.preferences.generalPreferences.userLanguage
        else:
            self.language = language

        self.msgDict = {self.language : dict}

    def addDict(self, dict, language :adsk.core.UserLanguages = None):
        self.msgDict[language] = dict

    def sLng(self, s :str) -> str:
        userLanguage = self.app.preferences.generalPreferences.userLanguage
        if not userLanguage in self.msgDict:
            return s

        dict = self.msgDict[userLanguage]

        if not s in dict:
            return s

        return dict[s]