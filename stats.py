"""For help see http://docs.python.org/library/profile.html"""

import pstats
p = pstats.Stats('cprofile')
#p.strip_dirs().sort_stats('cumulative').print_stats()
#p.strip_dirs().sort_stats('time').print_stats()

p.strip_dirs().sort_stats('time', 'cum').print_stats()
