# Author-kantoku
# Description-Import 3D Curves
# Fusion360API Python Addins

import adsk.core
import adsk.fusion
import traceback
import subprocess
import pathlib


#-----設定------
this_dir = pathlib.Path(__file__).resolve().parent

#mruby_sirenパス
_siren_path = this_dir / r'siren_0.14d_mingw64\bin\mruby.exe'

#ｲﾝﾎﾟｰﾄ用sirenｽﾌﾟﾘｸﾄパス
_siren_script_path = this_dir / r'siren_import.rb'
#-------------

from .ktkLanguageMessage import LangMsg
msgDict = {
    '"mruby_siren" configuration path is wrong!' : '"mruby_siren" 設定パスが間違っています!',
    '"siren script" configuration path is wrong!' : '"sirenスクリプト" 設定パスが間違っています!',
    'There were no importable curves.' : 'インポート可能な曲線がありませんでした。',
}
lm = LangMsg(msgDict, adsk.core.UserLanguages.JapaneseLanguage)


class Import3DCurvesFactry:

    @staticmethod
    def execute():
        ui = adsk.core.UserInterface.cast(None)
        try:
            # start
            app :adsk.core.Application = adsk.core.Application.get()
            ui = app.userInterface

            # 実行前ﾁｪｯｸ
            if not canExecute(ui):
                return

            # 拡張メソッド
            adsk.core.Line3D.to_skt = include_Lne
            adsk.core.NurbsCurve3D.to_skt = include_NBc
            adsk.core.Arc3D.to_skt = include_Arc
            adsk.core.Circle3D.to_skt = include_Cir
            adsk.core.Point3D.to_skt = include_Pnt

            # ファイルの選択
            im_path = select_File(ui)
            if not im_path:
                return

            # sirenでの読み込み
            infos = execSirenScript(im_path)

            # 情報変換
            crv_infos = conv_Siren_date(infos)
            
            # Geometry
            geos = get_Geos(crv_infos)
            if len(geos) < 1:
                ui.messageBox(lm.sLng('There were no importable curves.' ))
                return
            
            # Include
            des = adsk.fusion.Design.cast(app.activeProduct)
            comp = des.rootComponent
            skt_name = im_path.name + '_3DCurves'
            if IsParametric():
                baseF = comp.features.baseFeatures.add()
                baseF.startEdit()
                include_Geo(geos, comp, skt_name)
                baseF.finishEdit()
            else:
                include_Geo(geos, comp, skt_name)
            
            ui.messageBox('Done')
        except:
            if ui:
                ui.messageBox('ｴﾗｰ\n{}'.format(traceback.format_exc()))


# sirenでの読み込み
def execSirenScript(path):

    def getUniqueName(path) -> str:
        suffix = path.suffix
        files = [f.name for f in path.parent.iterdir()]

        base = 'tmp'
        idx = 0

        while True:
            idx += 1
            name = f'{base}_{idx}{suffix}'

            if not name in files:
                return name

    # rename - pathlibのrename分かりにく過ぎる
    tempName = getUniqueName(path)
    tmpPath = pathlib.Path(path.parent / tempName)

    path.rename(tmpPath)

    # exec script
    try:
        infos = subprocess.check_output([
            str(_siren_path),
            str(_siren_script_path),
            str(tmpPath)])

    finally:
        # re rename
        tmpPath.rename(str(path))
    return infos

# 実行前ﾁｪｯｸ
def canExecute(ui :adsk.core.UserInterface):
    msgs = []
    
    # if not os.path.isfile(_siren_path):
    if not _siren_path.exists():
        msg = lm.sLng('"mruby_siren" configuration path is wrong!')
        msgs.append(f'{msg}\n({str(_siren_path)})')

    # if not os.path.isfile(_siren_script_path):
    if not _siren_script_path.exists():
        msg = lm.sLng('"siren script" configuration path is wrong!')
        msgs.append(f'{msg}\n({str(_siren_path)})')

    if len(msgs) > 0:
        ui.messageBox('\n\n'.join(msgs))
        return False
    return True

# ﾌｧｲﾙ選択
def select_File(ui :adsk.core.UserInterface):
    dlg = ui.createFileDialog()
    dlg.title = 'ｲﾝﾎﾟｰﾄ 選択'
    dlg.filter = '3DCAD (*.ig*s;*.st*p;*.br*p)'
    if dlg.showOpen() != adsk.core.DialogResults.DialogOK :
        return
    return pathlib.Path(dlg.filename)

# パラメトリックチェック
def IsParametric():
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    return design.designType == adsk.fusion.DesignTypes.ParametricDesignType
    
# 挿入
def include_Geo(geos, comp, skt_name):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = skt_name
    sk.isComputeDeferred = True
    sk.areProfilesShown = False
    for geo in geos:
        geo.to_skt(sk)
    return
    
# 曲線情報取得
def conv_Siren_date(data):
    prms = []
    crvs = str(data).split('|')
    for crv in crvs:
        infos = crv.split('!')
        
        if infos[0].find('Siren::') < 1: continue
        cv_type = infos[0].split('Siren::')[-1]
        
        prm = [cv_type]
        if cv_type == 'Line':
            poss = [info[1:-1].split(',') for info in infos[1:]]
            [prm.append([float(x), float(y), float(z)]) for x, y, z in poss]

        elif cv_type == 'Circle':
            poss = [info[1:-1].split(",") for info in infos[1:4]]
            [prm.append([float(x), float(y), float(z)]) for x, y, z in poss]
            [prm.append(float(info)) for info in infos[4:]]
            if abs(prm[-1] - prm[-2]) > 0.001:
                prm[0] = 'Arc'

        elif cv_type == 'BSCurve':
            poss = [info[1:-1].split(',') for info in infos[1].split('@')]
            prm.append([[float(x), float(y), float(z)] for x, y, z in poss])
            prm.append(int(infos[2]))
            lst = [info[1:-1].split(',') for info in infos[3:]]
            for l in lst:
                prm.append([float(p) for p in l])

        elif cv_type == 'Vertex':
            poss = [infos[1][1:-1].split(',')]
            [prm.append([float(x), float(y), float(z)]) for x, y, z in poss]
        else:
            pass

        prms.append(prm)
    return prms

def get_Geos(lst):
    geos = []
    for cv_info in lst:
        cv_type = cv_info[0]
        if cv_type == 'Line':
            geos.append(create_Line(cv_info))
        elif cv_type == 'Circle':
            geos.append(create_Circle(cv_info))
        elif cv_type == 'Arc':
            geos.append(create_Arc(cv_info))
        elif cv_type == 'BSCurve':
            geos.append(create_BSCurve(cv_info))
        elif cv_type == 'Vertex':
            geos.append(create_Point(cv_info[1]))
        else:
            pass
    return geos
    
# Extension Methods
def include_Lne(self, sk):
    sk_geo = sk.sketchCurves.sketchLines.addByTwoPoints(
                self.startPoint, 
                self.endPoint)
    sk.include(sk_geo)
    sk_geo.deleteMe()
    return

def include_NBc(self, sk):
    sk_geo = sk.sketchCurves.sketchFittedSplines.addByNurbsCurve(self)
    sk_geo.isFixed = True
    sk.include(sk_geo)
    sk_geo.deleteMe()
    return

def include_Arc(self, sk):
    eva = self.evaluator
    (reValue, sParam, eParam) = eva.getParameterExtents()
    (reValue, midpnt) = eva.getPointAtParameter((sParam + eParam) * 0.5)
    sk_geo = sk.sketchCurves.sketchArcs.addByThreePoints(
        self.startPoint, midpnt, self.endPoint)
    sk.include(sk_geo)
    sk_geo.deleteMe()
    return

def include_Cir(self, skt):
    eva = self.evaluator
    re, sParam, eParam = eva.getParameterExtents()
    w = (eParam - sParam) * 0.25
    prms = {sParam + w * p for p in range(0,4)}
    
    pnts=[]
    for p in prms:
        re, pnt = eva.getPointAtParameter(p)
        pnts.append(pnt)
        
    ac1 = skt.sketchCurves.sketchArcs.addByThreePoints(
        pnts[0], pnts[1], pnts[2])
    ac2 = skt.sketchCurves.sketchArcs.addByThreePoints(
        pnts[2], pnts[3], pnts[0])
    arcs = [ac1, ac2]
    [skt.include(ac) for ac in arcs]
    [ac.deleteMe() for ac in arcs]
    return

def include_Pnt(self, sk):
    sk.sketchPoints.add(self)
    return

# Geometry
def create_Vector(pos):
    v = adsk.core.Vector3D.create(
        pos[0], pos[1], pos[2])
    return v

def create_Point(pos):
    return adsk.core.Point3D.create(
        pos[0] * 0.1, pos[1] * 0.1, pos[2] * 0.1)

def create_Line(lst):
    lin = adsk.core.Line3D.create(
            create_Point(lst[1]), 
            create_Point(lst[2]))
    nc = lin.asNurbsCurve
    return nc

def create_BSCurve(lst):
    poles = [create_Point(pos) for pos in lst[1]]
    degree = lst[2]
    knots = []
    for i, m in enumerate(lst[4]):
        for k in range(0, int(m)):
            knots.append(lst[3][i])
    weights = lst[5]

    nc = adsk.core.NurbsCurve3D.createRational(
        poles, degree, knots, weights, False)
    return nc

def create_Circle(lst):
    circle = adsk.core.Circle3D.createByCenter(
            create_Point(lst[1]), 
            create_Vector(lst[2]), 
            lst[4] * 0.1)
    return circle

def create_Arc(lst):
    arc = adsk.core.Arc3D.createByCenter(
            create_Point(lst[1]), 
            create_Vector(lst[2]), 
            create_Vector(lst[3]),
            lst[4] * 0.1, lst[5], lst[6])
    return arc