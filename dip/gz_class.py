# Adapted from galaxyzoo2.gz2string

def gal_string(datarow,survey='decals'):

    """ Determine a string for the consensus GZ2 classification of a
        galaxy's morphology.
    
    Parameters
    ----------
    datarow : astropy.io.fits.fitsrec.FITS_record
        Iterated element (row) of a final
        GZ2 table, containing all debiased probabilities
        and vote counts
    
    survey : string indicating the survey group that defines
        the workflow/decision tree. Default is 'decals'. 
        Possible options should be:
            
            'candels'
            'candels_2epoch'
            'decals'
            'ferengi'
            'goods_full'
            'illustris'
            'sloan',
            'sloan_singleband'
            'ukidss'
    
    Returns
    -------
    char: str
        String giving the plurality classification from GZ2
        eg, '
    
    Notes
    -------
    
    """
    
    weights = datarow
    
    if survey in ('decals',):
    
        max_t1 = weights[:3].argmax()
        
        char = ''
        task_eval = [0]*12
        
        task_eval[0] = 1
        
        # Smooth galaxies
        if max_t1 == 0:
            char += 'E'
            # Roundness
            char += ('r','i','c')[weights[23:26].argmax()]
            task_eval[8] = 1
        
        # Features/disk galaxies
        if max_t1 == 1:
            char += 'S'
            
            task_eval[1] = 1
            edgeon = weights[3:5]
            # Edge-on disks
            if edgeon[0] >= edgeon[1]:
                char += 'e'
                # Bulge shape
                char += ('r','b','n')[weights[20:23].argmax()]
                task_eval[7] = 1
            # Not edge-on disks
            else:
                task_eval[2] = 1
                task_eval[3] = 1
                task_eval[4] = 1
                if weights[5] > weights[6]:
                    # Barred galaxies
                    char += 'B'
                # Bulge prominence
                char += ('c','b','a')[weights[9:12].argmax()]
                if weights[7] > weights[8]:
                    # Arms number
                    char += ('1','2','3','4','+')[weights[15:20].argmax()]
                    task_eval[6] = 1
                    # Arms winding
                    char += ('t','m','l')[weights[12:15].argmax()]
                    task_eval[5] = 1
        
        # Mergers/tidal debris
        char += '[%s]' % ('MG','TD','MT','')[weights[26:30].argmax()]
        task_eval[9] = 1
        
        # Odd features
        if max(weights[31:38]) > 0.50:
            char += '(%s)' % ('n','r','l','d','i','o','v')[weights[31:38].argmax()]
            task_eval[10] = 1
        
        # Star/artifact
        if max_t1 == 2:
            char = 'A'
        
        # Discuss
        task_eval[11] = 1
        
        task_ans = [0]*12
        task_ans[0]  = weights[ 0: 3].argmax()+0
        task_ans[1]  = weights[ 3: 5].argmax()+3
        task_ans[2]  = weights[ 5: 7].argmax()+5
        task_ans[3]  = weights[ 7: 9].argmax()+7
        task_ans[4]  = weights[ 9:12].argmax()+9
        task_ans[5]  = weights[12:15].argmax()+12
        task_ans[6]  = weights[15:20].argmax()+15
        task_ans[7]  = weights[20:23].argmax()+20
        task_ans[8]  = weights[23:26].argmax()+23
        task_ans[9]  = weights[26:30].argmax()+26
        task_ans[10] = weights[31:38].argmax()+31
        task_ans[11] = weights[38:40].argmax()+38

    if survey in ('ferengi'):
    
        # Top-level: elliptical, features/disk, artifact
        
        max_t1 = weights[:3].argmax()
        
        char = ''
        task_eval = [0]*12
        
        task_eval[0] = 1
        
        # Smooth galaxies
        if max_t1 == 0:
            char += 'E'
            # Roundness
            char += ('r','i','c')[weights[23:26].argmax()]
            task_eval[8] = 1
        
        # Features/disk galaxies
        if max_t1 == 1:
            char += 'S'
            
            task_eval[1] = 1
            edgeon = weights[3:5]
            # Edge-on disks
            if edgeon[0] >= edgeon[1]:
                char += 'e'
                # Bulge shape
                char += ('r','b','n')[weights[20:23].argmax()]
                task_eval[7] = 1
            # Not edge-on disks
            else:
                task_eval[2] = 1
                task_eval[3] = 1
                task_eval[4] = 1
                if weights[5] > weights[6]:
                    # Barred galaxies
                    char += 'B'
                # Bulge prominence
                char += ('c','b','a')[weights[9:12].argmax()]
                if weights[7] > weights[8]:
                    # Arms number
                    char += ('1','2','3','4','+')[weights[15:20].argmax()]
                    task_eval[6] = 1
                    # Arms winding
                    char += ('t','m','l')[weights[12:15].argmax()]
                    task_eval[5] = 1
        
        # Mergers/tidal debris
        char += '[%s]' % ('MG','TD','MT','')[weights[26:30].argmax()]
        task_eval[9] = 1
        
        # Odd features
        if max(weights[31:38]) > 0.50:
            char += '(%s)' % ('n','r','l','d','i','o','v')[weights[31:38].argmax()]
            task_eval[10] = 1
        
        # Star/artifact
        if max_t1 == 2:
            char = 'A'
        
        # Discuss
        task_eval[11] = 1
        
        task_ans = [0]*12
        task_ans[0]  = weights[ 0: 3].argmax()+0
        task_ans[1]  = weights[ 3: 5].argmax()+3
        task_ans[2]  = weights[ 5: 7].argmax()+5
        task_ans[3]  = weights[ 7: 9].argmax()+7
        task_ans[4]  = weights[ 9:12].argmax()+9
        task_ans[5]  = weights[12:15].argmax()+12
        task_ans[6]  = weights[15:20].argmax()+15
        task_ans[7]  = weights[20:23].argmax()+20
        task_ans[8]  = weights[23:26].argmax()+23
        task_ans[9]  = weights[26:30].argmax()+26
        task_ans[10] = weights[31:38].argmax()+31
        task_ans[11] = weights[38:40].argmax()+38

    return char,task_eval,task_ans

def plurality(datarow,survey='decals',check_threshold = 0.50):

    """ Determine the plurality for the consensus GZ2 classification of a
        galaxy's morphology.
    
    Parameters
    ----------
    datarow : astropy.io.fits.fitsrec.FITS_record
        Iterated element (row) of a final
        GZ2 table, containing all debiased probabilities
        and vote counts
    
    survey : string indicating the survey group that defines
        the workflow/decision tree. Default is 'decals'. 
        Possible options should be:
            
            'candels'
            'candels_2epoch'
            'decals'
            'ferengi'
            'goods_full'
            'illustris'
            'sloan',
            'sloan_singleband'
            'ukidss'

    check_threshold: float indicating the threshold plurality level for
        checkbox questions. If no questions meet this, don't select any answer.
    
    Returns
    -------
    task_eval: array [N]
        1 if question was answered by the plurality path through the tree; 0 if not
    
    task_ans: array [N]
        Each answer gives the index of most common answer
            regardless of if it was in the plurality path or not.
    
    Notes
    -------
    
    """
    
    weights = datarow
    
    if survey in ('decals',):
        
        d = { 0:{'idx': 0,'len':3},       # 'Shape', 'Is the galaxy simply smooth and rounded, with no sign of a disk?', ->
              1:{'idx': 3,'len':2},       # 'Disk', 'Could this be a disk viewed edge-on?', ->
              2:{'idx': 5,'len':2},       # 'Bar', 'Is there any sign of a bar feature through the centre of the galaxy?' ->
              3:{'idx': 7,'len':2},       # "Is there any sign of a spiral arm pattern?"
              4:{'idx': 9,'len':3},       # "How prominent is the central bulge, compared with the rest of the galaxy?" 
              5:{'idx':12,'len':3},       # "How tightly wound do the spiral arms appear?" 
              6:{'idx':15,'len':5},       # "How many spiral arms are there?" 
              7:{'idx':20,'len':3},       # "Does the galaxy have a bulge at its centre? If so, what shape?" 
              8:{'idx':23,'len':3},       # 'Round', 'How rounded is it?', ->
              9:{'idx':26,'len':4},       # "Is the galaxy currently merging or is there any sign of tidal debris?" 
             10:{'idx':31,'len':7},       # "Do you see any of these odd features in the image?"  
             11:{'idx':38,'len':2}}       # "Would you like to discuss this object?"

        task_eval = [0]*len(d)
        task_ans  = [0]*len(d)
        
        # Top-level: smooth/features/artifact
        task_eval[0] = 1
        
        if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() < 2:

            # Smooth galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 0:
                # Roundness
                task_eval[8] = 1

            # Features/disk galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 1:
                # Disk galaxies
                task_eval[1] = 1

                # Edge-on disks
                if weights[d[1]['idx']] > weights[d[1]['idx']+1]:
                    # Bulge shape
                    task_eval[7] = 1
                # Not edge-on disks
                else:
                    task_eval[2] = 1
                    task_eval[3] = 1
                    if weights[d[3]['idx']] > weights[d[3]['idx']+1]:
                        # Spirals
                        task_eval[5] = 1
                        task_eval[6] = 1
                    task_eval[4] = 1
            
            # Merging/tidal debris
            task_eval[9] = 1
            
            # Odd features - only count if it's above some threshold, since this is a checkbox question
            if max(weights[d[10]['idx']:d[10]['idx'] + d[10]['len']]) > check_threshold:
                task_eval[10] = 1
        
        # Discuss
        task_eval[11] = 1
        
    if survey in ('ferengi','goods_full'):

        d = { 0:{'idx':0  ,'len':3},       # 'Shape', 'Is the galaxy simply smooth and rounded, with no sign of a disk?', ->
              1:{'idx':3  ,'len':3},       # 'Round', 'How rounded is it?', leadsTo: 'Is there anything odd?', ->
              2:{'idx':6  ,'len':2},       # 'Clumps', 'Does the galaxy have a mostly clumpy appearance?', ->
              3:{'idx':8  ,'len':6},       # 'Clumps', 'How many clumps are there?', leadsTo: 'Do the clumps appear in a straight line, a chain, or a cluster?', ->
              4:{'idx':14 ,'len':4},       # 'Clumps', 'Do the clumps appear in a straight line, a chain, or a cluster?', leadsTo: 'Is there one clump which is clearly brighter than the others?', ->
              5:{'idx':18 ,'len':2},       # 'Clumps', 'Is there one clump which is clearly brighter than the others?', ->
              6:{'idx':20 ,'len':2},       # 'Clumps', 'Is the brightest clump central to the galaxy?', ->
              7:{'idx':22 ,'len':2},       # 'Symmetry', 'Does the galaxy appear symmetrical?', leadsTo: 'Do the clumps appear to be embedded within a larger object?', ->
              8:{'idx':24 ,'len':2},       # 'Clumps', 'Do the clumps appear to be embedded within a larger object?', leadsTo: 'Is there anything odd?', ->
              9:{'idx':26 ,'len':2},       # 'Disk', 'Could this be a disk viewed edge-on?', ->
             10:{'idx':28 ,'len':3},       # 'Bulge', 'Does the galaxy have a bulge at its center? If so, what shape?', leadsTo: 'Is there anything odd?', ->
             11:{'idx':31 ,'len':2},       # 'Bar', 'Is there any sign of a bar feature through the centre of the galaxy?', leadsTo: 'Is there any sign of a spiral arm pattern?', ->
             12:{'idx':33 ,'len':2},       # 'Spiral', 'Is there any sign of a spiral arm pattern?', ->
             13:{'idx':35 ,'len':3},       # 'Spiral', 'How tightly wound do the spiral arms appear?', leadsTo: 'How many spiral arms are there?', ->
             14:{'idx':38 ,'len':6},       # 'Spiral', 'How many spiral arms are there?', leadsTo: 'How prominent is the central bulge, compared with the rest of the galaxy?', ->
             15:{'idx':44 ,'len':4},       # 'Bulge', 'How prominent is the central bulge, compared with the rest of the galaxy?', leadsTo: 'Is there anything odd?', ->
             16:{'idx':48 ,'len':2},       # 'Discuss', 'Would you like to discuss this object?', ->
             17:{'idx':50 ,'len':2},       # 'Odd', 'Is there anything odd?', ->
             18:{'idx':53 ,'len':7}}       # 'Odd', 'What are the odd features?', ->             # Indexing here skips the a-0 answer.

        task_eval = [0]*len(d)
        task_ans  = [0]*len(d)
        
        # Top-level: smooth/features/artifact
        task_eval[0] = 1
        
        if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() < 2:

            # Smooth galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 0:
                # Roundness
                task_eval[1] = 1

            # Features/disk galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 1:
                task_eval[2] = 1

                # Clumpy question
                if weights[d[2]['idx']] > weights[d[2]['idx']+1]:

                    # Clumpy galaxies
                    task_eval[3] = 1
                    if weights[d[3]['idx']:d[3]['idx'] + d[3]['len']].argmax() > 0:
                        # Multiple clumps
                        if weights[d[3]['idx']:d[3]['idx'] + d[3]['len']].argmax() > 1:
                            # One bright clump
                            task_eval[4] = 1
                        task_eval[5] = 1
                        if weights[d[5]['idx']] > weights[d[5]['idx']+1]:
                            # Bright clump symmetrical
                            task_eval[6] = 1
                    if weights[d[6]['idx']] > weights[d[6]['idx']+1]:
                        task_eval[7] = 1
                        task_eval[8] = 1

                else:
                    # Disk galaxies
                    task_eval[9] = 1
                    # Edge-on disks
                    if weights[d[9]['idx']] > weights[d[9]['idx']+1]:
                        # Bulge shape
                        task_eval[10] = 1
                    # Not edge-on disks
                    else:
                        task_eval[11] = 1
                        task_eval[12] = 1
                        if weights[d[12]['idx']] > weights[d[12]['idx']+1]:
                            # Spirals
                            task_eval[13] = 1
                            task_eval[14] = 1
                        task_eval[15] = 1
            
            # Odd features
            task_eval[17] = 1
            if weights[d[17]['idx']] > weights[d[17]['idx']+1]:
                # Only count if it's above some threshold, since this is a checkbox question
                if max(weights[d[18]['idx']:d[18]['idx'] + d[18]['len']]) > check_threshold:
                    task_eval[18] = 1
        
        # Discuss
        task_eval[16] = 1
        
    if survey in ('gzh',):

        d = { 0:{'len':3},       # 'Shape', 'Is the galaxy simply smooth and rounded, with no sign of a disk?', ->
              1:{'len':2},       # 'Disk', 'Could this be a disk viewed edge-on?', ->
              2:{'len':2},       # 'Bar', 'Is there any sign of a bar feature through the centre of the galaxy?', leadsTo: 'Is there any sign of a spiral arm pattern?', ->
              3:{'len':2},       # 'Spiral', 'Is there any sign of a spiral arm pattern?', ->
              4:{'len':4},       # 'Bulge', 'How prominent is the central bulge, compared with the rest of the galaxy?', leadsTo: 'Is there anything odd?', ->
              5:{'len':2},       # 'Odd', 'Is there anything odd?', ->
              6:{'len':3},       # 'Round', 'How rounded is it?', leadsTo: 'Is there anything odd?', ->
              7:{'len':7},       # 'Odd', 'What are the odd features?', ->            Not a checkbox 
              8:{'len':3},       # 'Bulge', 'Does the galaxy have a bulge at its center? If so, what shape?', leadsTo: 'Is there anything odd?', ->
              9:{'len':3},       # 'Spiral', 'How tightly wound do the spiral arms appear?', leadsTo: 'How many spiral arms are there?', ->
             10:{'len':6},       # 'Spiral', 'How many spiral arms are there?', leadsTo: 'How prominent is the central bulge, compared with the rest of the galaxy?', ->
             11:{'len':2},       # 'Clumps', 'Does the galaxy have a mostly clumpy appearance?', ->
             12:{'len':6},       # 'Clumps', 'How many clumps are there?', leadsTo: 'Do the clumps appear in a straight line, a chain, or a cluster?', ->
             13:{'len':2},       # 'Clumps', 'Is there one clump which is clearly brighter than the others?', ->
             14:{'len':2},       # 'Clumps', 'Is the brightest clump central to the galaxy?', ->
             15:{'len':4},       # 'Clumps', 'Do the clumps appear in a straight line, a chain, or a cluster?', leadsTo: 'Is there one clump which is clearly brighter than the others?', ->
             16:{'len':2},       # 'Symmetry', 'Does the galaxy appear symmetrical?', leadsTo: 'Do the clumps appear to be embedded within a larger object?', ->
             17:{'len':2}}       # 'Clumps', 'Do the clumps appear to be embedded within a larger object?', leadsTo: 'Is there anything odd?', ->

        # Don't need to skip indices since there's no checkbox question
        idx = 0
        for i in range(len(d)):
            d[i]['idx'] = idx
            idx += d[i]['len']

        task_eval = [0]*len(d)
        task_ans  = [0]*len(d)
        
        # Top-level: smooth/features/artifact
        task_eval[0] = 1
        
        if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() < 2:

            # Smooth galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 0:
                # Roundness
                task_eval[1] = 1

            # Features/disk galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 1:
                task_eval[2] = 1

                # Clumpy question
                if weights[d[2]['idx']] > weights[d[2]['idx']+1]:

                    # Clumpy galaxies
                    task_eval[3] = 1
                    if weights[d[3]['idx']:d[3]['idx'] + d[3]['len']].argmax() > 0:
                        # Multiple clumps
                        if weights[d[3]['idx']:d[3]['idx'] + d[3]['len']].argmax() > 1:
                            # Clump arrangement
                            task_eval[4] = 1
                            if weights[d[4]['idx']:d[4]['idx']+d[4]['len']].argmax() == 3:
                                # Bar
                                task_eval[11] = 1
                                # Spiral structure
                                task_eval[12] = 1
                                if weights[d[12]['idx']] > weights[d[12]['idx']+1]:
                                    # Spiral arms
                                    task_eval[13] = 1
                                    task_eval[14] = 1
                                # Bulge prominence
                                task_eval[15] = 1
                        # One clump brighter than others
                        task_eval[5] = 1
                        if weights[d[5]['idx']] > weights[d[5]['idx']+1]:
                            # Bright clump central
                            task_eval[6] = 1
                    if weights[d[6]['idx']] > weights[d[6]['idx']+1]:
                        # Symmetrical clumps
                        task_eval[7] = 1
                        # Clumps embedded
                        task_eval[8] = 1

                else:
                    # Disk galaxies
                    task_eval[9] = 1
                    # Edge-on disks
                    if weights[d[9]['idx']] > weights[d[9]['idx']+1]:
                        # Bulge shape
                        task_eval[10] = 1
                    # Not edge-on disks
                    else:
                        # Bar
                        task_eval[11] = 1
                        # Spiral
                        task_eval[12] = 1
                        if weights[d[12]['idx']] > weights[d[12]['idx']+1]:
                            # Spiral arm numbers and winding
                            task_eval[13] = 1
                            task_eval[14] = 1
                        # Bulge prominence
                        task_eval[15] = 1
            
            # Odd features
            task_eval[16] = 1
            if weights[d[16]['idx']] > weights[d[16]['idx']+1]:
                # Only count if it's above some threshold, since this is a checkbox question
                if max(weights[d[17]['idx']:d[17]['idx'] + d[17]['len']]) > check_threshold:
                    task_eval[17] = 1
        
        # Clumpy questions 5-8 not answered if they were organized in a spiral

        if weights[d[4]['idx']:d[4]['idx']+d[4]['len']].argmax() == 3 and task_eval[4]:
            task_eval[5] = 0
            task_eval[6] = 0
            task_eval[7] = 0
            task_eval[8] = 0

    if survey in ('candels','candels_2epoch'):
        
        d = { 0:{'idx':0 ,'len':3},       # 'Shape', 'Is the galaxy simply smooth and rounded, with no sign of a disk?', ->
              1:{'idx':3 ,'len':3},       # 'Round', 'How rounded is it?', leadsTo: 'Is there anything odd?', ->
              2:{'idx':6 ,'len':2},       # 'Clumps', 'Does the galaxy have a mostly clumpy appearance?', ->
              3:{'idx':8 ,'len':6},       # 'Clumps', 'How many clumps are there?', leadsTo: 'Do the clumps appear in a straight line, a chain, or a cluster?', ->
              4:{'idx':14,'len':4},       # 'Clumps', 'Do the clumps appear in a straight line, a chain, or a cluster?', leadsTo: 'Is there one clump which is clearly brighter than the others?', ->
              5:{'idx':18,'len':2},       # 'Clumps', 'Is there one clump which is clearly brighter than the others?', ->
              6:{'idx':20,'len':2},       # 'Clumps', 'Is the brightest clump central to the galaxy?', ->
              7:{'idx':22,'len':2},       # 'Symmetry', 'Does the galaxy appear symmetrical?', leadsTo: 'Do the clumps appear to be embedded within a larger object?', ->
              8:{'idx':24,'len':2},       # 'Clumps', 'Do the clumps appear to be embedded within a larger object?', leadsTo: 'Is there anything odd?', ->
              9:{'idx':26,'len':2},       # 'Disk', 'Could this be a disk viewed edge-on?', ->
             10:{'idx':28,'len':2},       # 'Bulge', 'Does the galaxy have a bulge at its center?', leadsTo: 'Is there anything odd?', ->
             11:{'idx':30,'len':2},       # 'Bar', 'Is there any sign of a bar feature through the centre of the galaxy?', leadsTo: 'Is there any sign of a spiral arm pattern?', ->
             12:{'idx':32,'len':2},       # 'Spiral', 'Is there any sign of a spiral arm pattern?', ->
             13:{'idx':34,'len':3},       # 'Spiral', 'How tightly wound do the spiral arms appear?', leadsTo: 'How many spiral arms are there?', ->
             14:{'idx':37,'len':6},       # 'Spiral', 'How many spiral arms are there?', leadsTo: 'How prominent is the central bulge, compared with the rest of the galaxy?', ->
             15:{'idx':43,'len':3},       # 'Bulge', 'How prominent is the central bulge, compared with the rest of the galaxy?', leadsTo: 'Is there anything odd?', ->
             16:{'idx':46,'len':4},       #  Merging/tidal debris
             17:{'idx':50,'len':2}}       #  Discuss

        task_eval = [0]*len(d)
        task_ans  = [0]*len(d)
        
        # Top-level: smooth/features/artifact
        task_eval[0] = 1
        
        if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() < 2:

            # Smooth galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 0:
                # Roundness
                task_eval[1] = 1

            # Features/disk galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 1:
                task_eval[2] = 1

                # Clumpy question
                if weights[d[2]['idx']] > weights[d[2]['idx']+1]:

                    # Clumpy galaxies
                    task_eval[3] = 1
                    if weights[d[3]['idx']:d[3]['idx'] + d[3]['len']].argmax() > 0:
                        # Multiple clumps
                        if weights[d[3]['idx']:d[3]['idx'] + d[3]['len']].argmax() > 1:
                            # One bright clump
                            task_eval[4] = 1
                        task_eval[5] = 1
                        if weights[d[5]['idx']] > weights[d[5]['idx']+1]:
                            # Bright clump symmetrical
                            task_eval[6] = 1
                    if weights[d[6]['idx']] > weights[d[6]['idx']+1]:
                        task_eval[7] = 1
                        task_eval[8] = 1

                else:
                    # Disk galaxies
                    task_eval[9] = 1
                    # Edge-on disks
                    if weights[d[9]['idx']] > weights[d[9]['idx']+1]:
                        # Bulge shape
                        task_eval[10] = 1
                    # Not edge-on disks
                    else:
                        task_eval[11] = 1
                        task_eval[12] = 1
                        if weights[d[12]['idx']] > weights[d[12]['idx']+1]:
                            # Spirals
                            task_eval[13] = 1
                            task_eval[14] = 1
                        task_eval[15] = 1
            
            # Merging/tidal debris
            task_eval[16] = 1

        # Discuss
        task_eval[17] = 1
        
    if survey in ('illustris',):
        
        d = { 0:{'idx': 0,'len':3},       # 'Shape', 'Is the galaxy simply smooth and rounded, with no sign of a disk?', ->
              1:{'idx': 3,'len':2},       # 'Disk', 'Could this be a disk viewed edge-on?', ->
              2:{'idx': 5,'len':2},       # 'Bar', 'Is there any sign of a bar feature through the centre of the galaxy?' ->
              3:{'idx': 7,'len':2},       # "Is there any sign of a spiral arm pattern?"
              4:{'idx': 9,'len':4},       # "How prominent is the central bulge, compared with the rest of the galaxy?" 
              5:{'idx':14,'len':7},       # Odd features
              6:{'idx':21,'len':3},       # Round
              7:{'idx':24,'len':3},       # Bulge shape
              8:{'idx':27,'len':3},       # arms winding
              9:{'idx':30,'len':6},       # arms number
             10:{'idx':36,'len':2},       # Is there anything odd?
             11:{'idx':38,'len':2}}       # "Would you like to discuss this object?"

        task_eval = [0]*len(d)
        task_ans  = [0]*len(d)
        
        # Top-level: smooth/features/artifact
        task_eval[0] = 1
        
        if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() < 2:

            # Smooth galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 0:
                # Roundness
                task_eval[6] = 1

            # Features/disk galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 1:
                # Disk galaxies
                task_eval[1] = 1

                # Edge-on disks
                if weights[d[1]['idx']] > weights[d[1]['idx']+1]:
                    # Bulge shape
                    task_eval[7] = 1
                # Not edge-on disks
                else:
                    task_eval[2] = 1
                    task_eval[3] = 1
                    if weights[d[3]['idx']] > weights[d[3]['idx']+1]:
                        # Spirals
                        task_eval[8] = 1
                        task_eval[9] = 1
                    task_eval[4] = 1
            

            # Odd features
            task_eval[10] = 1
            if weights[d[10]['idx']] > weights[d[10]['idx']+1]:
                # Only count if it's above some threshold, since this is a checkbox question
                if max(weights[d[5]['idx']:d[5]['idx'] + d[5]['len']]) > check_threshold:
                    task_eval[5] = 1
        
        # Discuss
        task_eval[11] = 1
        
    if survey in ('sloan','sloan_singleband','ukidss'):
        
        d = { 0:{'idx': 0,'len':3},       # 'Shape', 'Is the galaxy simply smooth and rounded, with no sign of a disk?', ->
              1:{'idx': 3,'len':2},       # 'Disk', 'Could this be a disk viewed edge-on?', ->
              2:{'idx': 5,'len':2},       # 'Bar', 'Is there any sign of a bar feature through the centre of the galaxy?' ->
              3:{'idx': 7,'len':2},       # "Is there any sign of a spiral arm pattern?"
              4:{'idx': 9,'len':4},       # "How prominent is the central bulge, compared with the rest of the galaxy?" 
              5:{'idx':13,'len':2},       # Is there anything odd?
              6:{'idx':16,'len':7},       # Odd features
              7:{'idx':23,'len':3},       # Round
              8:{'idx':26,'len':3},       # Bulge shape
              9:{'idx':29,'len':3},       # arms winding
             10:{'idx':32,'len':6},       # arms number
             11:{'idx':38,'len':2}}       # "Would you like to discuss this object?"

        task_eval = [0]*len(d)
        task_ans  = [0]*len(d)
        
        # Top-level: smooth/features/artifact
        task_eval[0] = 1
        
        if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() < 2:

            # Smooth galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 0:
                # Roundness
                task_eval[7] = 1

            # Features/disk galaxies
            if weights[d[0]['idx']:d[0]['idx']+d[0]['len']].argmax() == 1:
                # Disk galaxies
                task_eval[1] = 1

                # Edge-on disks
                if weights[d[1]['idx']] > weights[d[1]['idx']+1]:
                    # Bulge shape
                    task_eval[8] = 1
                # Not edge-on disks
                else:
                    task_eval[2] = 1
                    task_eval[3] = 1
                    if weights[d[3]['idx']] > weights[d[3]['idx']+1]:
                        # Spirals
                        task_eval[9] = 1
                        task_eval[10] = 1
                    task_eval[4] = 1
            

            # Odd features
            task_eval[5] = 1
            if weights[d[5]['idx']] > weights[d[5]['idx']+1]:
                # Only count if it's above some threshold, since this is a checkbox question
                if max(weights[d[6]['idx']:d[6]['idx'] + d[6]['len']]) > check_threshold:
                    task_eval[6] = 1
        
        # Discuss
        task_eval[11] = 1
        
    # Assign the plurality task numbers

    for i,t in enumerate(task_ans):
        try:
            task_ans[i]  = weights[d[i]['idx']:d[i]['idx'] + d[i]['len']].argmax() + d[i]['idx']
        except ValueError:
            print "ValueError in gz_class: {0:} categories, {1:} answers".format(len(weights),len(task_ans))

    return task_eval,task_ans
