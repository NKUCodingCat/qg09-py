import os
DIR = os.path.split(os.path.realpath(__file__))[0]
os.chdir(DIR)

import doctest, glob
for i in glob.glob(DIR+"/*.txt"):
    print "TESTING\t", i
    doctest.testfile(i)