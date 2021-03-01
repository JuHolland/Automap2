import os
import sys

import click 
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from qgis.core import QgsRasterLayer, QgsApplication, QgsMessageLogNotifyBlocker
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

sys.path.append('scripts/')
import functions
import produce
sys.path.append('../')

#Initialize QGIS Application
qgs = QgsApplication([], False)
qgs.setStyle("Fusion")
QgsApplication.setPrefixPath("C:\OSGEO4~1\apps\qgis", True)
QgsApplication.initQgis()
for alg in QgsApplication.processingRegistry().algorithms():
    print(alg.id(), "->", alg.displayName())

@click.command()
@click.option('--select', is_flag=True, help='Select the products to map')
@click.option('--new', is_flag=True, help='Only map products which are not already in the map folder')
@click.option('--input', is_flag=True, help='Select input path')
@click.option('--output', is_flag=True, help='Select output path')
def cli(select: bool,
        new: bool,
        input: bool,
        output: bool):

    """Produces PNG maps from tiff files with QGis

    Args:
        select (bool): Select the countries to map
        new (bool): Only map products which are not already in the map folder
        input (bool):  Select input path
        output (bool):  Select output path
    """


    # Setting paths
    template_path = "templates/_qgz"
    tab_path = "csv/product_type.csv"
    tab_path2 = "csv/dimensions.csv"
    colorRamp_path = "templates/_layer_styles"

    # Selecting path of input directory
    if input:
        products_path = str(QFileDialog.getExistingDirectory(None, "Select Input directory"))
    else:
        products_path = "products"

    # Selecting path of ouput directory
    if output:
        export_path = str(QFileDialog.getExistingDirectory(None, "Select Output directory"))
    else:
        export_path = "maps"


    # Getting products to map
    products_names = [p for p in os.listdir(products_path) if p.endswith('.tif')]


    # reading csv files
    tab = pd.read_csv(tab_path, index_col = 0, header = 0)
    tab2 = pd.read_csv(tab_path2, index_col = 0, header = 0)

    # check if name correct
    for filename in products_names:

        check = functions.check_name(filename, tab)
        
        if not check:
            w = QWidget()
            w.resize(400, 100)
            w.setWindowTitle('ERROR')
            vbox = QVBoxLayout(w)
            label = QLabel("Incorrect filename: " + filename)
            label.setAlignment(QtCore.Qt.AlignCenter)
            vbox.addWidget(label)
            w.show()
            sys.exit(qgs.exec_())


    # Only select new products
    if new:
        input_names = [p for p in os.listdir(products_path) if p.endswith('.tif')]
        output_names = [p[:-4]+'.tif' for p in os.listdir(export_path) if p.endswith('.png')]
        products_names = list(set(input_names).difference(output_names))

        if len(products_names)==0 :
            print('No new products to map !')

    products = [QgsRasterLayer(os.path.join(products_path,p), p) for p in products_names]
    all_countries = [functions.get_country(filename, tab2) for filename in products_names]
    countries = list(dict.fromkeys(all_countries))
    nb_countries = [all_countries.count(c) for c in countries]
    

    # Select countries to map
    if select:

        w = QWidget()
        w.resize(400, int(w.height()/10))
        w.setWindowTitle('Automap - Select countries to map')

        vbox = QVBoxLayout(w)

        # Products checkbox
        bxs = []
        bxs_name = []
        for i,c in enumerate(countries):
            bxs.append(QCheckBox(c + '\t \t \t(' + str(nb_countries[i]) + ')'))
            bxs_name.append(c)
            bxs[i].setChecked(True)
            vbox.addWidget(bxs[i])

        # Produce maps button
        hbox = QHBoxLayout()
        btn = QPushButton("Produce maps")
        btn.setFixedSize(QtCore.QSize(200, 30))
        hbox.addWidget(btn)
        vbox.addLayout(hbox)
        btn.clicked.connect(lambda: mapping(w, bxs, bxs_name, 
                                            template_path, colorRamp_path, products_names, 
                                            products_path, export_path, tab, tab2))

        w.show()
        sys.exit(qgs.exec_())

    else:
        produce.Map(template_path, colorRamp_path, products, products_names, export_path, tab)



def mapping(w, bxs, bxs_name, template_path, colorRamp_path, products_names, products_path, export_path, tab, tab2):

    w.close()

    bxs_txt = [bxs_name[i] for i,bx in enumerate(bxs) if bx.isChecked()]
    sel_products_names = [filename for filename in products_names if functions.get_country(filename, tab2) in bxs_txt]
    sel_products = [QgsRasterLayer(os.path.join(products_path,p), p) for p in sel_products_names]

    produce.Map(template_path, colorRamp_path, sel_products, sel_products_names, export_path, tab)


if __name__ == '__main__':
    cli()