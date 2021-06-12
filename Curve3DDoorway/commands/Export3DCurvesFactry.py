# Author-kantoku
# Description-Export 3D Curves
# Fusion360API Python Addins

import adsk.core
import adsk.fusion
import traceback
from itertools import chain
import os.path

from .ktkLanguageMessage import LangMsg
msgDict = {
    'There are no elements to export.' : 'エクスポートする要素がありません',
}
lm = LangMsg(msgDict, adsk.core.UserLanguages.JapaneseLanguage)


class Export3DCurvesFactry:

    @staticmethod
    def execute():
        ui = adsk.core.UserInterface.cast(None)
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            doc = app.activeDocument
            des = adsk.fusion.Design.cast(app.activeProduct)
            
            # 表示されているスケッチ
            skts = [skt
                    for comp in des.allComponents if comp.isSketchFolderLightBulbOn
                    for skt in comp.sketches if skt.isVisible]
            ui.activeSelections.clear()
            
            # 正しい位置でジオメトリ取得
            geos = list(chain.from_iterable(getSketchCurvesGeos(skt) for skt in skts))
            if len(geos) < 1:
                ui.messageBox(lm.sLng('There are no elements to export.'))
                return
            
            # エクスポートファイルパス
            path = get_Filepath(ui)
            if path is None:
                return
            
            # 新規デザイン
            expDoc = newDoc(app)
            expDes = adsk.fusion.Design.cast(app.activeProduct)
            doc.activate()
            
            # ダイレクト
            expDes.designType = adsk.fusion.DesignTypes.DirectDesignType

            # tempBRep
            tmpMgr = adsk.fusion.TemporaryBRepManager.get()
            crvs,_ = tmpMgr.createWireFromCurves(geos, True)
            
            # 実体化
            expRoot = expDes.rootComponent
            bodies = expRoot.bRepBodies
            bodies.add(crvs)
            
            # 保存
            res = exportFile(path,expDes.exportManager)
            
            # 一時Docを閉じる
            expDoc.close(False)
            
            # おしまい
            if res:
                msg = 'Done'
            else:
                msg = 'Failed'
            
            ui.messageBox(msg)
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# ファイルエクスポート
def exportFile(path, expMgr):
    _, ext = os.path.splitext(path)
    
    if 'igs' in ext:
        expOpt = expMgr.createIGESExportOptions(path)
    elif 'stp' in ext:
        expOpt = expMgr.createSTEPExportOptions(path)
    elif 'sat' in ext:
        expOpt = expMgr.createSATExportOptions(path)
    else:
        return False
        
    expMgr.execute(expOpt)
    return True
    
# ファイルパス
def get_Filepath(ui):
    dlg = ui.createFileDialog()
    dlg.title = 'Export3DCurves'
    dlg.isMultiSelectEnabled = False
    dlg.filter = 'IGES(*.igs);;STEP(*.stp);;SAT(*.sat)'
    if dlg.showSave() != adsk.core.DialogResults.DialogOK :
        return
    return dlg.filename

# 新しいDocs
def newDoc(app):
    desDoc = adsk.core.DocumentTypes.FusionDesignDocumentType
    return app.documents.add(desDoc)

# World座標でのジオメトリ取得
def getSketchCurvesGeos(skt):
    if len(skt.sketchCurves) < 1:
        return None
    
    #extension
    adsk.fusion.SketchCurve.toGeoTF = sketchCurveToGeoTransform
    adsk.fusion.Component.toOcc = componentToOccurrenc
    
    mat = skt.transform.copy()
    occ = skt.parentComponent.toOcc()
    
    if not occ is None:
        mat.transformBy(occ.transform)

    geos = [crv.toGeoTF(mat) for crv in skt.sketchCurves if not crv.isConstruction]
    
    return geos

# adsk.fusion.SketchCurve
def sketchCurveToGeoTransform(self,mat3d):
    geo = self.geometry.copy()
    if self.objectType == 'adsk::fusion::SketchEllipse':
        geo = geo.asNurbsCurve
    geo.transformBy(mat3d)
    
    return geo

# adsk.fusion.Component 拡張メソッド
# コンポーネントからオカレンスの取得　ルートはNone
def componentToOccurrenc(self):
    root = self.parentDesign.rootComponent
    if self == root:
        return None
        
    occs = [occ
            for occ in root.allOccurrencesByComponent(self)
            if occ.component == self]
    return occs[0]