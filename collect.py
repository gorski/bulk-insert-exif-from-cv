#!/usr/bin/env python

#pip install pillow
#pip install pyexiv2

# brew install exiv2 pyexiv2

import exifread
#import fractions
#from PIL import Image
#from PIL.ExifTags import TAGS
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

def move_file(fr, to):
    if fr == to:
        #print 'Same file'
        return None

    if not os.path.exists(fr):
        print 'File %s does not exist' % (fr)
        return None

    while os.path.exists(to):
        statinfo_from = os.stat(fr)

        # add _ to the file
        filename, file_extension = os.path.splitext(to)
        new_file_name = filename+"_"+file_extension
        statinfo_to = os.stat(to)



        if (statinfo_from.st_size == statinfo_to.st_size):
            print 'Files %s|%s are the same. Removing original.' % (fr, to)
            os.remove(fr)
            return None
        print 'Move %s to %s, which already exists. Changing name to %s' % (fr, to, new_file_name)
        to = new_file_name

    os.rename(fr, to)


print '------ start collect ------'
for file in os.listdir("."):
    filename, file_extension = os.path.splitext(file)
    if file_extension.lower() == '.jpg' or file_extension.lower() == '.jpeg':
        f = open(file, 'rU')
        tags = exifread.process_file(f)
        #for tag in tags.keys():
    #        if (tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote')):
    #            print "[%s] = %s" % (tag, tags[tag])    
        if ('Image DateTime' in tags):
            dtime = tags['Image DateTime']
            fr = 'I'
        elif ('EXIF DateTimeOriginal' in tags):
            dtime = tags['EXIF DateTimeOriginal']
            fr = 'E'
        else:
            print "- [%s] NO EXIF INFORMATION!" %( file) 
            continue
        dtime = str(dtime).replace('.','').replace(':','-').replace(' ','_')
        new_file_name = dtime+file_extension.lower()
        print "+%s [%s] -> [%s]" %( fr, file,new_file_name)
        f.close()
        move_file(file, new_file_name)
    else:
        print "-- [%s]" %( file)
print '------ done ------'

        




#set_gps_location('DSC05204.JPG', 50.32805929, 20.18687574)