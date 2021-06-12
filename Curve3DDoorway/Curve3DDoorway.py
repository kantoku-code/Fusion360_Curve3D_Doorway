#Author-kantoku
#Description-Two-turn Mobius strip
#Fusion360API Python

import adsk.core
import traceback

try:
    from . import config
    from .apper import apper

    from .commands.Import3DCurvesCore import Import3DCurves
    from .commands.Export3DCurvesCore import Export3DCurves

    from .commands.ktkLanguageMessage import LangMsg
    msgDict = {
        'Import 3D Curves' : '3D曲線インポート',
        'Import 3D curves.' : '3D曲線のインポートします。',
        'Export 3D Curves' : '3D曲線エクスポート',
        'Export the displayed sketch curve.' : '表示されているスケッチ曲線をエクスポートします。',
    }
    lm = LangMsg(msgDict, adsk.core.UserLanguages.JapaneseLanguage)

    # Create our addin definition object
    my_addin = apper.FusionApp(config.app_name, config.company_name, False)
    my_addin.root_path = config.app_path

    my_addin.add_command(
        lm.sLng('Import 3D Curves'),
        Import3DCurves,
        {
            'cmd_description': lm.sLng('Import 3D curves.'),
            'cmd_id': 'import3DCurves',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'UtilityPanel',
            'cmd_resources': 'import',
            'command_visible': True,
            'command_promoted': False,
            'create_feature': False,
        }
    )

    my_addin.add_command(
        lm.sLng('Export 3D Curves'),
        Export3DCurves,
        {
            'cmd_description': lm.sLng('Export the displayed sketch curve.'),
            'cmd_id': 'export3DCurves',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'UtilityPanel',
            'cmd_resources': 'export',
            'command_visible': True,
            'command_promoted': False,
            'create_feature': False,
        }
    )

except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization: {}'.format(traceback.format_exc()))


def run(context):
    my_addin.run_app()


def stop(context):
    my_addin.stop_app()
