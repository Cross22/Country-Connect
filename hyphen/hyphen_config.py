import os, shutil


# Adjust the default path for dictionaries in module hyphen/config.py to the package root.
# Prepare the import of hyphen. It cannot be imported from the
# distribution root as the extension module 'hnj' may be missing there
# and __path__[0] is needed to adjust the default
# directory path for dictionaries. So we rename the hyphen
# directory temporarily.
if os.path.exists('hyphen'): shutil.move('hyphen', 'hyphen_')
print "Adjusting /.../hyphen/config.py... ",
# We catch ImportErrors to handle situations where the hyphen package has been
# installed in a directory that is not listed in sys.path. This occurs, e.g.,
# when creating a Debian package.
try:
    import hyphen
    mod_path = '/'.join((hyphen.__path__[0], 'config.py'))
    f = open(mod_path, "w")
    contents = ''.join(("default_dic_path = '", hyphen.__path__[0], "'\n",
    "default_repository = 'http://ftp.services.openoffice.org/pub/OpenOffice.org/contrib/dictionaries/'\n"))
    f.write(contents)
    f.close()
    print "Done.\n"
except ImportError:
    print '''Warning: Could not import hyphen package. You may wish to adjust config.py
            manually or run setup.py with different options.'''
finally:
    if os.path.exists('hyphen_'): shutil.move('hyphen_', 'hyphen')

