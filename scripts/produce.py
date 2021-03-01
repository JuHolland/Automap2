import os
from os import path
import glob

from shutil import copyfile
import create_template
import functions
import pandas as pd 
from qgis.core import *


# Remove PNG overwritting message
from osgeo import gdal
gdal.PushErrorHandler('CPLQuietErrorHandler')
gdal.SetConfigOption("GDAL_PAM_ENABLED", "NO")



def reset():
	'''
	Remove country template and reset the source of neighbours layer to adm0 shapefile
	'''

	# Remove country template 
	files = glob.glob('templates/_qgz/*.qgz')
	for file in files:
		if not(file.endswith('world.qgz')):
			os.remove(file)

	# Reset source
	gadm36 = [os.path.join("templates/_layers",f) for f in os.listdir("templates/_layers") if f.startswith('gadm36_0')]
	for f in gadm36:
		src = f
		dst = f.replace("gadm36_0", "neighbours")
		copyfile(src, dst)


def Map(template_path: str, colorRamp_path: str, products: list, products_names: list, export_path: str, tab: pd.DataFrame):
	'''
	Creating maps in QGis 
	'''

	# Mapping products

	for i in range(len(products)):

		product = products[i]
		product_name = products_names[i]

		print('Producing map ' + product_name + ' (' + str(i + 1) + ' of ' + str(len(products)) + ')')

		# Creating country template and loading it
		country = product_name[0:3]
		project = QgsProject.instance()
		project_name = os.path.join(template_path, country + '.qgz')
		if path.exists(project_name):
			project.read(project_name)
		else: 
			reset()
			create_template.main_fct(template_path, country)
			project.read(project_name)

		# Adding product to map
		project.addMapLayer(product, False)
		root = project.layerTreeRoot()
		node_layer = root.addLayer(product)

		# Setting Color scale
		colorRamp = functions.get_colorRamp(product_name, tab)
		layer_style = os.path.join(colorRamp_path, colorRamp + '.qml')
		product.loadNamedStyle(layer_style)

		# Get layout and items
		manager = project.layoutManager()
		layout = manager.printLayouts()[0]
		items = layout.items()

		# Change subtitles
		sub1 = functions.get_parname(product_name, tab)
		sub2 = functions.get_timestamp(product_name)

		labels = [x for x in items if isinstance(x, QgsLayoutItemLabel)]

		for label in labels:
			if label.text() == 'subtitle1':
				label.setText(sub1)
			elif label.text() == 'subtitle2':
				label.setText(sub2)


		# Updating Legend
		legend = [x for x in items if isinstance(x, QgsLayoutItemLegend)][0]
		par = product_name[3:6]

		if par == 'tda' or par == 'vim':
			leg = QgsLayoutItemPicture(layout)
			leg.setPicturePath(os.path.join(colorRamp_path, par + '_legend.png'))
			leg.attemptMove(legend.positionWithUnits())
			leg.setResizeMode(4)
			layout.addItem(leg)

			group = legend.model().rootGroup()
			group.clear()

		else:	
			group = legend.model().rootGroup()
			group.insertChildNode(0, QgsLayerTreeLayer(product))
			group.children()[0].setName('')

		# Export map as PNG
		exporter = QgsLayoutExporter(layout)
		map_name = os.path.join(export_path, product_name[:-4] + '.png')
		exporter.exportToImage(map_name, QgsLayoutExporter.ImageExportSettings())

	# Removing country template and resetting source shapefiles
	reset()





		
