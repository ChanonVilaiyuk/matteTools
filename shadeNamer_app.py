import maya.cmds as mc
import maya.mel as mm
from functools import partial

import sys, os, time
from tool.matte import presets
reload(presets)


class MyApp() : 
	def __init__(self) : 
		self.win = 'shadeNamer'
		self.ui = '%sUI' % self.win
		self.wh = [400, 640]


	def show(self) : 
		if mc.window(self.ui, exists = True) : 
			mc.deleteUI(self.ui)

		mc.window(self.ui, t = 'Shade Namer Tool v.1.0', wh = self.wh)

		form = mc.formLayout()

		layout1r = [a for a in xrange(0, 9, 1)]
		layout2r = [a for a in xrange(9, 20, 1)]
		data = presets.charPresets
		keyData = [a for a in data.keys()]
		endCount = len(keyData) - 1
		c1 = mc.columnLayout(adj = 1, rs = 4)
		pmm = str()
		i = 0 

		for i in range(len(keyData)) : 

			if i in layout1r : 
				key = '$replace_'
				mm = data[keyData[i]]['mm'].replace(key, '')
				name = data[keyData[i]]['presetName']

				if not pmm == mm : 
					# mc.text(l = mm)
					mc.frameLayout(l = mm)
					mc.columnLayout(adj = 1)
					count = 0

				mc.button('button%s' % i, l = name, h = 30, c = partial(self.rename, name, i))

				if pmm == mm : 
					if count == 1 : 
						mc.setParent('..')
						mc.setParent('..')
						pass

					count += 1 

				pmm = mm

		mc.frameLayout(l = 'Extra Tool')
		mc.columnLayout(adj = 1)
		mc.button(l = 'Select object from material', h = 30, c = partial(self.selectObj))
		mc.setParent('..')
		mc.setParent('..')


		mc.setParent('..')

		c2 = mc.columnLayout(adj = 1, rs = 4)

		pmm = str()

		for i in range(len(keyData)) : 

			if i in layout2r : 
				key = '$replace_'
				mm = data[keyData[i]]['mm'].replace(key, '')
				name = data[keyData[i]]['presetName']

				if not pmm == mm : 
					# mc.text(l = mm)
					mc.frameLayout(l = mm)
					mc.columnLayout(adj = 1)
					count = 0

				mc.button('button%s' % i, l = name, h = 30, c = partial(self.rename, name, i))

				if pmm == mm : 
					if count == 1 : 
						mc.setParent('..')
						mc.setParent('..')
						pass

					count += 1 

				if i == endCount : 
					mc.setParent('..')
					mc.setParent('..')

				pmm = mm

				i += 1


		mc.setParent('..')

		mc.formLayout(form, e = True, 
						attachForm = [(c1, 'top', 4), (c2, 'top', 4), (c1, 'left', 4), (c2, 'right', 4), (c1, 'bottom', 4), (c2, 'bottom', 4)], 
						attachControl = [(c1, 'right', 5, c2)], 
						attachPosition=[(c1, 'right', 5, 50), (c2, 'left', 0, 50)]
						)

		mc.showWindow()
		mc.window(self.ui, e = True, wh = self.wh)


	def rename(self, name, i, arg = None) : 
		sel = mc.ls(sl = True)

		if sel : 
			mc.rename(sel[0], '%s_VRayMtl' % name)
			mc.button('button%s' % i, e = True, bgc = [0, 0.4, 0])


	def selectObj(self, arg = None) : 
		selMtr = mc.ls(sl = True)

		if selMtr : 
			mc.hyperShade(objects = selMtr[0])