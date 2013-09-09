a = dict()

if not 33 in a:
    a[33] = 5

if not 33 in a:
    a[33] = 6

for key in a.keys():
    print key, a[key]


#
#my_text = ["how do you do there?", str(1), str(56), 'smiles']
#
#joined = ' : '.join(my_text)
#print joined
#
#
#
#
#print float(4)
#
#print 65.7
#print int(65.7)
#
#a = (1, 1)
#b = (2, 1)
#
#if b > a:
#    print 'boo'
#
#from hyphen import hyphenator
#from textwrap2 import TextWrapper
#import pygame
#pygame.font.init()
## Download and install some dictionaries in the default directory using the default
## repository, usually the OpenOffice website
##for lang in ['en_US']:
##    if is_installed(lang): uninstall(lang)
## Create some hyphenators
#
##print list_installed()
#h_en = hyphenator('en_US', lmin = 3, rmin = 3) # the en_US dictionary is used by default!
## Now hyphenate some words. Note that under Python 3.0, words are of type string.
##print h_en.wrap(u'Mozambiquenorad')
##[[u'beau', u'tiful'], [u'beauti', u'ful']]
##print h_en.wrap(u'beautiful', 6)
##[u'beau-', u'tiful']
##print h_en.wrap(u'beautiful', 7)
##[u'beauti-', u'ful']
#
#h_en = hyphenator('en_US', lmin = 3, rmin = 3)
#tw = TextWrapper(width=10, use_hyphenator=h_en)
#max_text_width = 3
#from textrect import *
#
#text = unicode("Bosnia and Herzegovina")
#
#print tw.wrap(text)
#
#
#
#
##font = pygame.font.Font("assets/fonts/verdana.TTF", 10)
##cur_width = 60
##repeat = True
##while repeat == True:
##    print 'cur_width: ' + str(cur_width)
##    cur_width -= 1
##    tw = TextWrapper(width=cur_width, use_hyphenator=h_en)
##    wrapped_text = tw.wrap(unicode(text))
##    for line in wrapped_text:
##        if font.size(line)[0] > max_text_width:
##            repeat = True
##            break
##    else:
##        repeat = False
#        
#
##rendered_width = 0
##rendered_height = 0
##text = ""
##for line in wrapped_text:
##    text += line
##    if line != wrapped_text[-1]:
##        text += " "
##    rendered_height += font.size(line)[1] + font.get_linesize()
##    if font.size(line)[0] > rendered_width:
##        rendered_width = font.size(line)[0]
##        
##print text
##print rendered_height
##print font.get_linesize()
##print rendered_width
##        
##text_rect = pygame.Rect(0, 0, rendered_width, rendered_height)
##render_textrect(text, font, text_rect, (0,0,0), (255,255,255), 1)        

