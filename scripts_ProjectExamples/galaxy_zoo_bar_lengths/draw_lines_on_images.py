# um so I never ran this at the command line
# only ever used ipython (4.2.0) for it
# probably means I should make this a notebook
import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


xsize = 424
ysize = 424
top_offset = 200
tilebuf = 5

# widths of lines, with w4 being widest
w1=1
w2=2
w3=3
w4=4

# these will be outputs from extract_line_drawings.py and cluster_line_markings.py
all_markfile   = 'galaxy-zoo-bar-lengths-line-drawings.csv'
cfile_single   = 'gzbl_clusters_all_single.csv'
cfile_complete = 'gzbl_clusters_all_complete.csv'
cfile_average  = 'gzbl_clusters_all_average.csv'
cfile_ward     = 'gzbl_clusters_all_ward.csv'

# this is similar to the manifest I uploaded when I made the project, made from the
# subject data export retrieved through the project builder and the result of
# the aggregations available in the project builder.
# if I find the script that did this I will upload it
# but it's also totally possible I did this in TOPCAT, in which case there's no
# script. Sorry.
subjfile       = 'gzbl_subject_data_withbarclass_nodrawings_withscales_gzh_gzc_sdss.csv'


all_subjects   = pd.read_csv(subjfile)
clust_single   = pd.read_csv(cfile_single)
clust_complete = pd.read_csv(cfile_complete)
clust_average  = pd.read_csv(cfile_average)
clust_ward     = pd.read_csv(cfile_ward)
all_markings   = pd.read_csv(all_markfile)

# there should be no duplicates but let's just make sure
thesubjs = all_subjects.subject_id.unique()

# I don't think this would work as a groupby.apply() because we need to draw both raw markings and clustered markings for different kinds of linkage distances
# so a for loop it is
n_subj = len(thesubjs)
for i_s, the_sid in enumerate(thesubjs):

    if i_s % 250 == 0:
        print("Subject %d of %d (Subject id %d)..." % (i_s, n_subj, the_sid))

    # pull out the subject info and markings that we care about
    thesubj    = all_subjects[all_subjects.subject_id == the_sid]
    themarks   = all_markings[all_markings.subject_id == the_sid]
    # the sorts don't guarantee the highest-p marks will be on the top layer (because the loops below don't have to go in order) but it's pretty good.
    thecl_sing = clust_single[clust_single.subject_id == the_sid].sort(['p_true_positive'])
    thecl_comp = clust_complete[clust_complete.subject_id == the_sid].sort(['p_true_positive'])
    thecl_aver = clust_average[clust_average.subject_id == the_sid].sort(['p_true_positive'])
    thecl_ward = clust_ward[clust_ward.subject_id == the_sid].sort(['p_true_positive'])

    # we are going to do a grid that's 2 images wide x 3 long
    imsize_x = xsize + tilebuf + xsize
    imsize_y = ysize + tilebuf + ysize + tilebuf + ysize + top_offset

    # create the grid with a white background color
    imgrid = Image.new('RGB', (imsize_x, imsize_y), (255, 255, 255))
    draw   = ImageDraw.Draw(imgrid)
    galimg = Image.open('../../gzbl_project/gzbl_data_bundle/subject_images/%s' % thesubj.image_inverted_local.values[0])

    yloc0 = top_offset
    yloc0_end = yloc0 + ysize

    xloc1 = xsize + tilebuf
    yloc1 = top_offset + ysize + tilebuf
    xloc1_end = xloc1 + xsize
    yloc1_end = yloc1 + ysize

    yloc2 = top_offset + ysize + tilebuf + ysize + tilebuf
    yloc2_end = yloc2 + ysize

    # (0,0 is the top left)
    # top row
    imgrid.paste(galimg, (xloc1,yloc0, xloc1_end,yloc0_end))
    imgrid.paste(galimg, (0,yloc0, xsize,yloc0_end))
    # middle row
    imgrid.paste(galimg, (0,yloc1, xsize,yloc1_end))
    imgrid.paste(galimg, (xloc1,yloc1, xloc1_end,yloc1_end))
    # bottom row
    imgrid.paste(galimg, (0,yloc2, xsize,yloc2_end))
    imgrid.paste(galimg, (xloc1,yloc2, xloc1_end,yloc2_end))

    # Add some basic info in text to the top of the image
    # ugh, the system couldn't find arial.ttf but it found Arial.ttf just fine
    xoffset = xstart = 25
    xtxt = xoffset
    xtxt2 = xloc1 + xoffset
    ystart = 25
    ytxt = ystart
    font = ImageFont.truetype("Arial.ttf", 20)
    txtsize = font.getsize("ABCDEF")
    yoffset = txtsize[1] + txtsize[1]/2  #1.5 line spacing

    draw.text((xtxt, ytxt),"Subject %d (%s)" % (the_sid, thesubj.OBJID.values[0]),(0,0,0),font=font)
    ytxt += yoffset

    draw.text((xtxt, ytxt), "z = %.2f, p_bar = %.2f, n_class = %d" % (thesubj.z_use.values[0], thesubj.t0_p_bar.values[0], thesubj.t0_num_users.values[0]), (0,0,0), font=font)
    ytxt += yoffset

    draw.text((xtxt, ytxt), "%d marks drawn in %d classifications" % (len(themarks), len(themarks.classification_id.unique())), (0,0,0), font=font)
    ytxt += yoffset

    draw.text((xtxt, ytxt), "    by %d users" % (len(themarks.user_name.unique())), (0,0,0), font=font)
    ytxt += yoffset

    ytxt = ystart

    draw.text((xtxt2, ytxt), "Clusters with significance > 0.3 in:", (0,0,0), font=font)
    ytxt += yoffset

    draw.text((xtxt2, ytxt), "   Single: %d (of %d clusters)" % (sum(thecl_sing.p_true_positive >= 0.3), len(thecl_sing)), (0,0,0), font=font)
    ytxt += yoffset

    draw.text((xtxt2, ytxt), "   Complete: %d (of %d clusters)" % (sum(thecl_comp.p_true_positive >= 0.3), len(thecl_comp)), (0,0,0), font=font)
    ytxt += yoffset

    draw.text((xtxt2, ytxt), "   Average: %d (of %d clusters)" % (sum(thecl_aver.p_true_positive >= 0.3), len(thecl_aver)), (0,0,0), font=font)
    ytxt += yoffset

    draw.text((xtxt2, ytxt), "   Ward: %d (of %d clusters)" % (sum(thecl_ward.p_true_positive >= 0.3), len(thecl_ward)), (0,0,0), font=font)
    ytxt += yoffset

    # add marks - note the top left stays clean so we can see the bar underneath, if there is one.

    # all marks - top right
    draw.text((xloc1+xstart, yloc0+ystart), "Raw marks", (0,0,0), font=font)
    dx = xloc1
    dy = top_offset
    for themark in themarks.iterrows():
        theline = themark[1]
        draw.line((theline.x1+dx,theline.y1+dy, theline.x2+dx,theline.y2+dy), fill="#CC0000", width=1)


    # single - middle left
    draw.text((xstart, yloc1+ystart), "Single", (0,0,0), font=font)
    dx = 0
    dy = yloc1
    for themark in thecl_sing.iterrows():
        theline = themark[1]
        if theline.p_true_positive >= 0.5:
            thewidth = w4
            thefill = "#00DD00"
        elif theline.p_true_positive >= 0.3:
            thewidth = w3
            thefill = "#55AA55"
        elif theline.p_true_positive >= 0.15:
            thewidth = w2
            thefill = "#77CCFF"
        else:
            thewidth = w1
            thefill = "#55AADD"
        draw.line((theline.x1_med+dx,theline.y1_med+dy, theline.x2_med+dx,theline.y2_med+dy), fill=thefill, width=thewidth)

    # complete - middle right
    draw.text((xloc1+xstart, yloc1+ystart), "Complete", (0,0,0), font=font)
    dx = xloc1
    dy = yloc1
    for themark in thecl_comp.iterrows():
        theline = themark[1]
        if theline.p_true_positive >= 0.5:
            thewidth = w4
            thefill = "#00DD00"
        elif theline.p_true_positive >= 0.3:
            thewidth = w3
            thefill = "#55AA55"
        elif theline.p_true_positive >= 0.15:
            thewidth = w2
            thefill = "#77CCFF"
        else:
            thewidth = w1
            thefill = "#55AADD"
        draw.line((theline.x1_med+dx,theline.y1_med+dy, theline.x2_med+dx,theline.y2_med+dy), fill=thefill, width=thewidth)


    # average - lower left
    draw.text((xstart, yloc2+ystart), "Average", (0,0,0), font=font)
    dx = 0
    dy = yloc2
    for themark in thecl_aver.iterrows():
        theline = themark[1]
        if theline.p_true_positive >= 0.5:
            thewidth = w4
            thefill = "#00DD00"
        elif theline.p_true_positive >= 0.3:
            thewidth = w3
            thefill = "#55AA55"
        elif theline.p_true_positive >= 0.15:
            thewidth = w2
            thefill = "#77CCFF"
        else:
            thewidth = w1
            thefill = "#55AADD"
        draw.line((theline.x1_med+dx,theline.y1_med+dy, theline.x2_med+dx,theline.y2_med+dy), fill=thefill, width=thewidth)


    # ward - lower right
    draw.text((xloc1+xstart, yloc2+ystart), "Ward", (0,0,0), font=font)
    dx = xloc1
    dy = yloc2
    for themark in thecl_ward.iterrows():
        theline = themark[1]
        if theline.p_true_positive >= 0.5:
            thewidth = w4
            thefill = "#00DD00"
        elif theline.p_true_positive >= 0.3:
            thewidth = w3
            thefill = "#55AA55"
        elif theline.p_true_positive >= 0.15:
            thewidth = w2
            thefill = "#77CCFF"
        else:
            thewidth = w1
            thefill = "#55AADD"
        draw.line((theline.x1_med+dx,theline.y1_med+dy, theline.x2_med+dx,theline.y2_med+dy), fill=thefill, width=thewidth)

    imgrid.save("marked_images/s%d_allmarks_clusters.png" % the_sid)
