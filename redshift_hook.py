import os
import sys 
import maya.cmds as mc
import maya.mel as mm

from tool.matte import create_db as db
reload(db)

presetName = '_RS'

def readDb(project) : 
    """ create default db file. If not exists, generate one """ 
    dbResult = db.readDatabase(project, dbName='rsMatteID')

    return dbResult, db.dbPathCustom(project, dbName='rsMatteID')


def listMtlNode() : 
    """ list material """
    nodeTypes = ['RedshiftArchitectural',
                'RedshiftCarPaint',
                'RedshiftHair',
                'RedshiftIncandescent',
                'RedshiftMaterial',
                'RedshiftMaterialBlender',
                'RedshiftMatteShadowCatcher',
                'RedshiftSkin',
                'RedshiftSprite',
                'RedshiftSubSurfaceScatter']

    nodes = []

    for nodeType in nodeTypes: 
        nodes = nodes + mc.ls(type=nodeType)

    mtlNodes = dict()
    matteAttr = 'rsMaterialId'

    for eachNode in nodes : 
        shadingEngine = mc.listConnections(eachNode, t = 'shadingEngine')

        if shadingEngine : 
            attr = '%s.%s' % (shadingEngine[0], matteAttr)
            if mc.objExists(attr) : 
                id = mc.getAttr(attr)

                mtlNodes[eachNode] = id

    return mtlNodes

def setID(material, value) : 
    attr = matteIDAttr(material)

    if attr: 
         mc.setAttr('%s' % attr, value)

def matteIDAttr(material): 
    shadingEngine = mc.listConnections(material, t='shadingEngine')

    if shadingEngine: 
        return '%s.rsMaterialId' % shadingEngine[0]

def setObjectID(obj, value): 
    pass 
