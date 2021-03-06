# PyHyphen - hyphenation for Python
# module: dictools
'''
This module contains convenience functions to handle hyphenation dictionaries.
'''

import os, urllib2, config
from StringIO import StringIO
from  zipfile import ZipFile

__all__ = ['install', 'is_installed', 'uninstall', 'list_installed']


def list_installed(directory = config.default_dic_path):
    '''Return a list of strings containing language and country codes of the
    dictionaries installed in 'directory' (default as declared in config.py).
    Example: file name = 'hyph_en_US.dic'. Return value: ['en_US']'''
    return [d[5:-4] for d in os.listdir(directory)
            if (d.startswith('hyph_') and d.endswith('.dic'))]

def is_installed(language, directory = config.default_dic_path):
    '''return True if 'directory' (default as declared in config.py)
    contains a dictionary file for 'language',
    False otherwise.
    By convention, 'language' should have the form 'll_CC'.
    Example: 'en_US' for US English.
    '''
    return (language in list_installed(directory))


def install(language, directory = config.default_dic_path,
            repos = config.default_repository):
    '''
    Download  and install a dictionary file.
    language: a string of the form 'll_CC'. Example: 'en_US' for English, USA
    directory: the installation directory. Defaults to the
    value given in config.py. After installation this is the package root of 'hyphen'
    repos: the url of the dictionary repository. (Default: as declared in config.py;
    after installation this is the OpenOffice repository for dictionaries.).'''
    url = ''.join((repos, 'hyph_', language, '.zip'))
    s = urllib2.urlopen(url).read()
    z = ZipFile(StringIO(s))
    if z.testzip():
        raise IOError('The ZIP archive containing the dictionary is corrupt.')
    dic_filename = ''.join(('hyph_', language, '.dic'))
    dic_str = z.read(dic_filename)
    dest = open('/'.join((directory, dic_filename)), 'w')
    dest.write(dic_str)
    dest.close()

def uninstall(language, directory = config.default_dic_path):
    '''
    Uninstall the dictionary of the specified language.
    'language': is by convention a string of the form 'll_CC' whereby ll is the
        language code and CC the country code.
    'directory' (default: config.default_dic_path'. After installation of PyHyphen
    this is the package root of 'hyphen'.'''
    file_path = ''.join((directory, '/hyph_', language, '.dic'))
    os.remove(file_path)

