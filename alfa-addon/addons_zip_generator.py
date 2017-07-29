""" zip generator """

import os
import zipfile


class Generator:
    """
		Original code from addons_xml_generator.py
    """
    def __init__( self ):
        # generate files
        self._generate_addons_file()
        # notify user
        print "Finished creating zip file"

    def _generate_addons_file( self ):
        # addon list
        addons = os.listdir( "." )
        # final addons text
        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                # skip any file or .svn folder
                if ( not os.path.isdir( addon ) or addon == ".svn" ): continue
                # create path
                _path = os.path.join( addon, "addon.xml" )
                # split lines for stripping
                xml_lines = open( _path, "r" ).read().splitlines()
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if line.find("<addon") >= 0:
                        version = line[line.find('version="') + 9:]
                        version = version[:version.find('"')]
                        break
                    # add line
                filenamezip = '.\\' + addon + '.\\' + addon + '-' + version
                print addon
                zf = zipfile.ZipFile(filenamezip + ".zip", "w")
                for dirname, subdirs, files in os.walk(addon):
                    zf.write(dirname)
                    for filename in files:
                        if '.zip' not in filename:
                            zf.write(os.path.join(dirname, filename))
                zf.close()
            except Exception, e:
                # missing or poorly formatted addon.xml
                print "Excluding %s for %s" % ( _path, e, )


if ( __name__ == "__main__" ):
    # start
    Generator()