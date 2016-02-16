from PySide import QtCore
from PySide import QtGui

class customQWidgetItem(QtGui.QWidget) : 
	def __init__(self, parent = None) : 
		super(customQWidgetItem, self).__init__(parent)
		# set label 
		self.allLayout = QtGui.QHBoxLayout()
		self.gridLayout = QtGui.QGridLayout()

		self.text1Label = QtGui.QLabel()
		self.text2Label = QtGui.QLabel()
		self.text3Label = QtGui.QLabel()
		self.text4Label = QtGui.QLabel()

		# set icon
		self.iconQLabel = QtGui.QLabel()

		self.gridLayout.addWidget(self.iconQLabel, 1, 1)
		self.gridLayout.addWidget(self.text1Label, 1, 2)
		self.gridLayout.addWidget(self.text2Label, 1, 3)
		self.gridLayout.addWidget(self.text3Label, 2, 2)
		self.gridLayout.addWidget(self.text4Label, 2, 3)
		self.gridLayout.setColumnStretch(0, 0)
		self.gridLayout.setColumnStretch(1, 0)
		self.gridLayout.setColumnStretch(2, 0)
		self.gridLayout.setColumnStretch(3, 1)
		self.gridLayout.setSpacing(2)

		self.allLayout.addLayout(self.gridLayout, 0)
		self.allLayout.setContentsMargins(2, 2, 2, 2)
		self.setLayout(self.allLayout)

		# set font
		font = QtGui.QFont()
		font.setPointSize(9)
		font.setBold(True)
		self.text1Label.setFont(font)
		self.text2Label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

	def setText1(self, text) : 
		self.text1Label.setText(text)

	def setText2(self, text) : 
		self.text2Label.setText(text)

	def setText3(self, text) : 
		self.text3Label.setText(text)

	def setText4(self, text) : 
		self.text4Label.setText(text)

	def setTextColor1(self, color) : 
		self.text1Label.setStyleSheet('color: rgb(%s, %s, %s);' % (color[0], color[1], color[2]))

	def setTextColor2(self, color) : 
		self.text2Label.setStyleSheet('color: rgb(%s, %s, %s);' % (color[0], color[1], color[2]))

	def setTextColor3(self, color) : 
		self.text3Label.setStyleSheet('color: rgb(%s, %s, %s);' % (color[0], color[1], color[2]))

	def setTextColor4(self, color) : 
		self.text4Label.setStyleSheet('color: rgb(%s, %s, %s);' % (color[0], color[1], color[2]))

	def setIcon(self, iconPath, size = 16) : 
		self.iconQLabel.setPixmap(QtGui.QPixmap(iconPath).scaled(size, size, QtCore.Qt.KeepAspectRatio))

	def text1(self) : 
		return self.text1Label.text()

	def text2(self) : 
		return self.text2Label.text()

	def text3(self) : 
		return self.text3Label.text()

	def text4(self) : 
		return self.text4Label.text()

	def setText1Italic(self, italic = True) : 
		font = QtGui.QFont()
		font.setItalic(italic)
		self.text1Label.setFont(font)

	def setText2Italic(self, italic = True) : 
		font = QtGui.QFont()
		font.setItalic(italic)
		self.text2Label.setFont(font)

	def setText3Italic(self, italic = True) : 
		font = QtGui.QFont()
		font.setItalic(italic)
		self.text3Label.setFont(font)

	def setText4Italic(self, italic = True) : 
		font = QtGui.QFont()
		font.setItalic(italic)
		self.text4Label.setFont(font)