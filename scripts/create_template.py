import os
import pandas as pd 
from qgis.core import *
from PyQt5.QtGui import * 

def main_fct(template_path:str, country: str):
	'''
	Creating QGis template and layout for specified country from world template
	'''

	# Loading world template
	project = QgsProject.instance()
	project.read(os.path.join(template_path,'world.qgz'))

	# Getting information about country
	country = country.upper()
	mapDim = pd.read_csv('csv/dimensions.csv', index_col = 0)
	dim = mapDim.loc[country]

	# Removing the country from template   
	layer = project.mapLayersByName('neighbours')[0]
	select_str = "\"GID_0\" = '" + country + "'"
	layer.selectByExpression(select_str, QgsVectorLayer.SetSelection)
	layer.startEditing()
	layer.deleteSelectedFeatures()
	layer.commitChanges()

	# Create map       
	manager = project.layoutManager()              
	layoutName = "PrintLayout"

	layouts_list = manager.printLayouts()
	for layout in layouts_list:
	    if layout.name() == layoutName:
	        manager.removeLayout(layout)
	        
	        
	layout = QgsPrintLayout(project) 
	layout.initializeDefaults()
	layout.setName(layoutName)
	manager.addLayout(layout)

	# create map item in the layout
	map = QgsLayoutItemMap(layout)
	map.setRect(20, 20, 20, 20)

	# set the map extent
	ms = QgsMapSettings()
	ms.setLayers(project.mapLayers().values())
	rect = QgsRectangle(dim['rectXMin'], dim['rectYMin'], dim['rectXMax'], dim['rectYMax'])
	rect.scale(1.0)
	ms.setExtent(rect)
	map.setExtent(rect)
	map.setBackgroundColor(QColor(255, 255, 255, 0))
	layout.addLayoutItem(map)

	map.attemptMove(QgsLayoutPoint(0, 0, QgsUnitTypes.LayoutMillimeters))
	map.attemptResize(QgsLayoutSize(dim['width'], dim['height'], QgsUnitTypes.LayoutMillimeters))

	pc = layout.pageCollection()
	pc.resizeToContents(QgsMargins(), QgsUnitTypes.LayoutMillimeters)

	# Adding logo
	logo = QgsLayoutItemPicture(layout)
	logo.setPicturePath('templates/_logos/vam_blue.jpg')
	logo.attemptMove(QgsLayoutPoint(dim['logoX'], dim['logoY'], QgsUnitTypes.LayoutMillimeters))
	logo.setResizeMode(4)
	layout.addItem(logo)

	# Adding legend
	legend = QgsLayoutItemLegend(layout)
	legend.setAutoUpdateModel(False)
	legend.model().rootGroup().clear()
	layerTree = QgsLayerTree()
	lakeLayer = project.mapLayersByName('Lakes')[0]
	layerTree.addLayer(lakeLayer)
	group = legend.model().rootGroup()
	group.insertChildNode(0, layerTree)
	group.children()[0].setName('')
	legend.setBackgroundColor(QColor(255, 255, 255, 0))
	layout.addLayoutItem(legend)
	legend.attemptMove(QgsLayoutPoint(dim['legX'], dim['legY'], QgsUnitTypes.LayoutMillimeters))

	# Adding title and subtitles
	title = QgsLayoutItemLabel(layout)
	title.setText(dim['country'].upper())
	title.setFont(QFont('Calibri', 24))
	title.setFontColor(QColor(31, 120, 180, 255))
	title.adjustSizeToText()
	layout.addLayoutItem(title)

	subtitle1 = QgsLayoutItemLabel(layout)
	subtitle1.setText('subtitle1')
	subtitle1.setFont(QFont('Calibri', 18))
	subtitle1.adjustSizeToText()
	layout.addLayoutItem(subtitle1)

	subtitle2 = QgsLayoutItemLabel(layout)
	subtitle2.setText('subtitle2')
	subtitle2.setFont(QFont('Calibri', 20))
	subtitle2.adjustSizeToText()
	layout.addLayoutItem(subtitle2)

	title.attemptResize(QgsLayoutSize(110, 15, QgsUnitTypes.LayoutMillimeters))
	subtitle1.attemptResize(QgsLayoutSize(110, 15, QgsUnitTypes.LayoutMillimeters))
	subtitle2.attemptResize(QgsLayoutSize(110, 20, QgsUnitTypes.LayoutMillimeters))
	title.setHAlign(4)
	subtitle1.setHAlign(4)
	subtitle2.setHAlign(4)
	title.attemptMove(QgsLayoutPoint(dim['titleX'], dim['titleY'], QgsUnitTypes.LayoutMillimeters))
	subtitle1.attemptMove(QgsLayoutPoint(dim['titleX'], dim['titleY'] + 12, QgsUnitTypes.LayoutMillimeters))
	subtitle2.attemptMove(QgsLayoutPoint(dim['titleX'], dim['titleY'] + 22, QgsUnitTypes.LayoutMillimeters))


	# Save country template
	project_name = country + '.qgz'
	project.write(os.path.join(template_path, project_name))
