import os
import sys 
import maya.cmds as mc
import maya.mel as mm

from tool.matte import create_db as db
reload(db)

presetName = '_Vray'

def readDb(project) : 
    """ create default db file. If not exists, generate one """ 
    dbResult = db.readDatabase(project, dbName='vrayMatteID_res')

    return dbResult, db.dbPathCustom(project, dbName='vrayMatteID_res')


def listMtlNode() : 
    """ list material """
    nodeTypes = ['VRayMtl',
                'VRayBlendMtl',
                'VRayBumpMtl',
                'VRayMtl2Sided',
                'VRayCarPaintMtl']

    nodes = []

    for nodeType in nodeTypes: 
        nodes = nodes + mc.ls(type=nodeType)

    mtlNodes = dict()
    matteAttr = 'vrayMaterialId'

    for eachNode in nodes : 
        attr = '%s.%s' % (eachNode, matteAttr)

        if mc.listConnections(eachNode, t='shadingEngine') : 
            if not mc.objExists(attr) : 
                mm.eval('vray addAttributesFromGroup %s vray_material_id 1' % eachNode)

            id = mc.getAttr(attr)

            mtlNodes[eachNode] = id

        return mtlNodes

def setID(material, value) : 
    attr = matteIDAttr(material)

    if not mc.objExists(attr) : 
        mm.eval('vray addAttributesFromGroup %s vray_material_id 1' % attr.split('.')[0])

    try : 
        mc.setAttr(attr, l = False)

    except Exception as e : 
        print e 

    mc.setAttr(attr, value)

def setObjectID(obj, value): 
    attr = '%s.vrayObjectID' % obj

    if not mc.objExists(attr) : 
        mm.eval('vray addAttributesFromGroup %s vray_objectID 1' % obj)

    try : 
        mc.setAttr(attr, l = False)

    except Exception as e : 
        print e 

    mc.setAttr(attr, value)


def matteIDAttr(material): 
    matteAttr = 'vrayMaterialId'
    attr = '%s.%s' % (material, matteAttr)
    return attr

