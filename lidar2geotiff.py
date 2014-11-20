#!/usr/bin/env python2
# -*- coding: utf-8 -*-

############################################################################
# NAME:		*.xyz to GeoTIFF
# AUTOR:	Christopher Barron
# ZWECK:	Dieses Skript generiert mit Hilfe von GRASS-GIS aus lidar-Daten 
# 			*.xyz GeoTIFFs. Angepasst werden müssen hierfür die Umgebungs-
#			variablen, der Pfad zu den lidar-Daten und der Pfad zum Ausgabe-
#			verzeichnis. Betriebssystem ist Win7, GRASS-GIS-Version 6.4.3
#############################################################################

import os
import sys
import collections
import subprocess as subp

gisbase = os.environ['GISBASE'] = 'C:\Program Files (x86)\GRASS GIS 6.4.3'  #GISBASE needs to point the root of the GRASS installation directory
gisrc = 'H:\grassdb'
gisdbase = 'H:\grassdb'
location = ''
mapset = ''
LD_LIBRARY_PATH = 'C:\Program Files (x86)\GRASS GIS 6.4.3\lib'
PATH = 'C:\Program Files (x86)\GRASS GIS 6.4.3\etc';'C:\Program Files (x86)\GRASS GIS 6.4.3\etc\python';'C:\Program Files (x86)\GRASS GIS 6.4.3\lib';'C:\Program Files (x86)\GRASS GIS 6.4.3\bin';'C:\Python27';'C:\Program Files (x86)\GRASS GIS 6.4.3\Python27';'C:\Program Files (x86)\GRASS GIS 6.4.3\msys'
PYTHONLIB = 'C:\Python27'
PYTHONPATH = 'C:\Program Files (x86)\GRASS GIS 6.4.3\etc\python'
GRASS_SH = 'C:\Program Files (x86)\GRASS GIS 6.4.3\msys\bin\sh.exe'

sys.path.append(os.path.join(os.environ['GISBASE'], 'etc', 'python'))

import grass.script as grass
import grass.script as grass
import grass.script.setup as gsetup

gsetup.init(gisbase, gisdbase, location, mapset)

# Pfad zum Ordner mit den lidar-Daten
lidar_folder = 'H:\lidar_data\lidar_script\daten'

# Verzeichnis, in dem der Ordner mit den GeoTiffs erstellt werden soll
geotiff_folder = 'H:\lidar_data\lidar_script\daten\geotiff'
if not os.path.exists(geotiff_folder):
    os.makedirs(geotiff_folder)

# Hier beginnt die Schleife für jedes *.xyz-File im lidar_folder
# Liste alle *.xyz Dateien auf, die im Verzeichnis liegen
for lidar_file in os.listdir(lidar_folder):
	if lidar_file.endswith(".xyz"):
		print '###'
		print '###'
		print '###'
		print 'Verarbeite: ' + lidar_file
		print '###'
		print '###'
		print '###'

		#####
		# SCHRITT 1: Ausdehnung des Input-Rasters bestimmen
		#####

		# Pfad zum lidar-file
		lidar_path = str(lidar_folder) + '\\' + str(lidar_file)

		# Grass-Befehl zum Auslesen der grass-region
		ausdehnung = grass.parse_command('r.in.xyz', input=lidar_path, method="median", output='DTM_2012_3458_5486_out.xyz', fs=" ", flags="s")
		#print ausdehnung

		# Ausdehnung sortieren, da dictionaries nicht sortiert sind
		ausdehnung_sortiert = collections.OrderedDict(sorted(ausdehnung.items(), key=lambda t: t[0]))
		#print ausdehnung_sortiert

		# Auswählen der  Koordinatenpaare aus dem sortierten Dictionary
		x_coord = ausdehnung_sortiert.keys()[0]
		y_coord = ausdehnung_sortiert.keys()[1]
		
		# Löschen von 'x: ' und 'y: ' um nur die Zahlen zu habe
		x_coord = x_coord.replace("x: ", "").replace("y: ", "")
		y_coord = y_coord.replace("y: ", "").replace("x: ", "")

		# Splitten der Koordinatenpaare
		x = x_coord.split()
		y = y_coord.split()

		x_min = x[0]
		x_max = x[1]
		y_min = y[0]
		y_max = y[1]

		print x_min, x_max
		print y_min, y_max

		#####
		# SCHRITT 2: Region setzen für weitere Schritte
		#####
		print 'grass region setzen.'
		grass.run_command('g.region', n=y_max, s=y_min, e=x_max, w=x_min, res='0.5')

		#####
		# SCHRITT 3: Datenimport
		#####
		grass.run_command('g.remove', rast=str(lidar_file[:-4]) + '_rast_test')
		
		output_lidar_file = str(lidar_file[:-4]) + '_rast_test'
		grass.run_command('r.in.xyz', input=lidar_path, method='median', output=output_lidar_file, fs=" ")

		mymaps = grass.read_command("g.list", _type="rast") 
		print mymaps

		#####
		# SCHRITT 4: Höhenlinien einfärben
		#####

		#grass.run_command('r.colors', map=output_lidar_file, color='elevation')

		#####
		# SCHRITT 5: Raster in ein GeoTIFF exportieren und dabei ein World-File schreiben ("TFW")
		#####

		geotiff_file = str((output_lidar_file) + '.tif')
		grass.run_command('r.out.gdal', input=output_lidar_file, output=geotiff_folder + '\\' + geotiff_file, type='Float64', createopt='PROFILE\=GeoTIFF,TFW=YES,COMPRESS=DEFLATE')
		

# Literatur
# http://gis.stackexchange.com/questions/74549/grass-6-5-or-7-0-need-help-with-loop-script
