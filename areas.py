#!/usr/bin/env python

#pip install pillow
#pip install pyexiv2

# brew install exiv2 pyexiv2

import shutil

import pyexiv2
import fractions
from PIL import Image
from PIL.ExifTags import TAGS
import sys

import csv
import sys

import glob, os


def to_deg(value, loc):
        if value < 0:
            loc_value = loc[0]
        elif value > 0:
            loc_value = loc[1]
        else:
            loc_value = ""
        abs_value = abs(value)
        deg =  int(abs_value)
        t1 = (abs_value-deg)*60
        min = int(t1)
        sec = round((t1 - min)* 60, 5)
        return (deg, min, sec, loc_value)

def view_gps_location(file_name, lat, lng):
    """Adds GPS position as EXIF metadata

    Keyword arguments:
    file_name -- image file 
    lat -- latitude (as float)
    lng -- longitude (as float)

    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])
    
    print lat_deg
    print lng_deg
    
    # convert decimal coordinates into degrees, munutes and seconds
    exiv_lat = (pyexiv2.Rational(lat_deg[0]*60+lat_deg[1],60),pyexiv2.Rational(lat_deg[2]*100,6000))
    exiv_lng = (pyexiv2.Rational(lng_deg[0]*60+lng_deg[1],60),pyexiv2.Rational(lng_deg[2]*100,6000))

    exiv_image = pyexiv2.Image(file_name)
    exiv_image.readMetadata()
    exif_keys = exiv_image.exifKeys() 
    
    for key in exif_keys:
        print key, [exiv_image[key]]
    

def set_gps_location(file_name, lat, lng, alt):
    """Adds GPS position as EXIF metadata

    Keyword arguments:
    file_name -- image file 
    lat -- latitude (as float)
    lng -- longitude (as float)

    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])
    
    print lat_deg
    print lng_deg
    
    # convert decimal coordinates into degrees, munutes and seconds
    exiv_lat = (pyexiv2.Rational(lat_deg[0]*60+lat_deg[1],60),pyexiv2.Rational(lat_deg[2]*100,6000), pyexiv2.Rational(0, 1))
    exiv_lng = (pyexiv2.Rational(lng_deg[0]*60+lng_deg[1],60),pyexiv2.Rational(lng_deg[2]*100,6000), pyexiv2.Rational(0, 1))

    exiv_image = pyexiv2.ImageMetadata(file_name)
    exiv_image.read()
    exif_keys = exiv_image.exif_keys

    
    exiv_image["Exif.GPSInfo.GPSLatitude"] = exiv_lat
    exiv_image["Exif.GPSInfo.GPSLatitudeRef"] = lat_deg[3]
    exiv_image["Exif.GPSInfo.GPSLongitude"] = exiv_lng
    exiv_image["Exif.GPSInfo.GPSLongitudeRef"] = lng_deg[3]

    exiv_image["Exif.GPSInfo.GPSAltitudeRef"] = '0'
    fraction = fractions.Fraction(alt)
    exiv_image['Exif.GPSInfo.GPSAltitude'] = pyexiv2.Rational(fraction.numerator, fraction.denominator)

    exiv_image["Exif.Image.GPSTag"] = 654
    exiv_image["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
    exiv_image["Exif.GPSInfo.GPSVersionID"] = '2 0 0 0'
    
    exiv_image.write()

def match_areas(row, areas):

    file = row[0]
    lat = row[1]
    lon = row[2]

    #print "[%s] looking for match..." % file
    match = None
    for area in areas:
        #print "!!! %s" % area
        ddir = area[0];
        minLatitude = area[1]
        maxLatitude = area[2]
        minLongitude = area[3]
        maxLongitude = area[4]

        if lat >= minLatitude and lat <= maxLatitude and lon <= maxLongitude and lon >= minLongitude:
            dest = ddir+'/'+file
            print " + [%s] matches [%s]. Copy %s to %s" % (file, ddir, file, dest)
            match = 1

            if not os.path.exists(ddir):
                os.makedirs(ddir)

            shutil.copyfile(file, dest)

    if not match:
        print " - [%s] not matching areas!" %file


print '------ start - discover directory mapping ------'
file = 'areas.csv'
if not os.path.isfile(file):
    "Not areas.csv file"
    exit()

f = open(file, 'rU')
areas = [];

try:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        if row and (row[0] != 'directory'):
            print "Mapping found for area: [%s] %s-%s x %s-%s" % (row[0], row[1], row[2], row[3], row[4])
            areas.append(row)
finally:
    f.close()

print '------ start parse csv files ------'
for file in os.listdir("."):
    if file.endswith(".csv") and file != 'areas.csv':
        f = open(file, 'rU')
        try:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if row and row[0] != 'image':
                    fn = row[0]
                    x = row[1]
                    y= row[2]
                    alt = row[3]                  
                    if fn:
                        if os.path.isfile(fn):
                            match_areas(row, areas);
                        else:
                            print " - [%s] file does not exist " %  fn
        finally:
            f.close()
print '------ done ------'

