import sys
from panoptes_client import Panoptes


def panoptes_connect():
    # file with username and password on the first line with a space in between
    panoptesuserfile = 'panoptesuserfile.txt'

    with open(panoptesuserfile) as fp:
        uinfo = (fp.readline()).strip().split()


    return Panoptes.connect(username=uinfo[0], password=uinfo[1])



#bye
