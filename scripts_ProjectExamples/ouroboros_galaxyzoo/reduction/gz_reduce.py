from astropy.table import Table, Column, hstack, join
import string
import gzip
import re
import json
import numpy as np


def parse_tree(stub):
    """Parse a Galaxy Zoo coffeescript tree description file"""
    questions = []
    answers = []
    letters = string.ascii_lowercase
    f = open('{}_tree.coffee'.format(stub))
    for l in f:
        ls = l.strip().split(',')
        if len(ls) > 0:
            lss = ls[0].replace("'", "").split(maxsplit=1)
        if len(lss) > 1:
            test = lss[0].startswith
            value = lss[1].lower().replace(' ', '_')
            if test('@question'):
                qi = 0
                if value in questions:
                    questions[questions.index(value)] += '_a'
                while '{}_{}'.format(value, letters[qi]) in questions:
                    qi += 1
                if qi > 0:
                    value = '{}_{}'.format(value, letters[qi])
                questions.append(value)
                answers.append([])
            elif test('@checkbox'):
                answers[-1].append((value, 'x'))
            elif test('@answer'):
                if value != 'done':
                    answers[-1].append((value, 'a'))
    return questions, answers


def count_matches(col, test, group, anywhere=True):
    """Count the matches of `test` in `col` grouped by `group`"""
    if anywhere:
        matches = np.zeros(len(col), np.bool)
        matches[~col.mask] = np.array([test in x.split(';')
                                       for x in col[~col.mask]])
    else:
        matches = col == test
    matches = Column(matches).group_by(group)
    count = matches.groups.aggregate(np.sum)
    return count


def collate_classifications(indata, stub, questions, answers):
    """Reduce a GZ classification database dump to a table of vote fractions"""
    outdata = Table()
    outdata['subject_id'] = np.unique(indata['subject_id'])
    qindex = 0
    for c in indata.columns:
        if c.startswith(stub):
            q = questions[qindex]
            outcols = Table()
            for aindex, (a, qtype) in enumerate(answers[qindex]):
                test = '{}-{}'.format(qtype, aindex)
                count = count_matches(indata[c], test, indata['subject_id'],
                                      anywhere=(qtype == 'x'))
                name = '{}_{}'.format(q, a)
                outcols[name] = count
                if aindex == 0:
                    total = count
                else:
                    total += count
            name = '{}_total'.format(q)
            outdata[name] = total
            outdata = hstack([outdata, outcols])
            qindex += 1
    return outdata


def recalculate_odd_total(data):
    """Adjust for skipping the odd question without providing any answer"""
    data = data.copy()
    data['odd_total'] = data['shape_total'] - data['shape_star_or_artifact']
    return data


def calculate_fractions(data, questions, answers):
    """Reduce a GZ classification database dump to a table of vote fractions"""
    data = data.copy()
    for qindex in range(len(questions)):
        q = questions[qindex]
        for aindex, (a, qtype) in enumerate(answers[qindex]):
            name = '{}_{}'.format(q, a)
            totalname = '{}_total'.format(q)
            fracname = '{}_frac'.format(name)
            data[fracname] = data[name] / data[totalname]
    return data


def read_subjects(infile, stub, survey_id_field):
    """Parse a dump of the Ouroboros subjects table to get useful ids"""
    subject_id = []
    survey_id = []
    zooniverse_id = []
    # tmp = ''
    for line in gzip.open(infile):
        line = line.decode("utf-8")
        # # fix corruption (if necessary - matches cleaned version by Lee)
        # if re.search('ouroboros', line) is not None:
        #     tmp += re.sub('2017-03.*ouroboros.*', '', line)[:-1]
        #     continue
        # if tmp != '':
        #     line = tmp + line
        #     tmp = ''
        if re.search(stub, line) is not None:
            ls = line.strip().split(',', maxsplit=3)
            match = re.match('ObjectId\((.+)\)', ls[0])
            subject_id.append(match.group(1))
            zooniverse_id.append(ls[1])
            metadata = ls[3].replace('""', '"')[1:-1]
            metadata = json.loads(metadata)
            if survey_id_field in metadata.keys():
                survey_id.append(metadata[survey_id_field])
            else:
                survey_id.append(None)
    subjects = Table([np.array(subject_id), np.array(survey_id, dtype=np.str),
                      np.array(zooniverse_id)],
                     names=('subject_id', 'survey_id', 'zooniverse_id'))
    return subjects


def reduce_data(date, tree='gama', subjectset='gama09',
                survey_id_field='provided_image_id',
                subjectcat='galaxy_zoo_subjects_lee.csv.gz'):
    """Do everything to produce reduced table of ids and vote fractions"""
    questions, answers = parse_tree(tree)
    template = '{}_galaxy_zoo_{}_classifications.csv'
    indata = Table.read(template.format(date, subjectset), fast_reader=False)
    outdata = collate_classifications(indata, tree, questions, answers)
    outdata = recalculate_odd_total(outdata)
    outdata = calculate_fractions(outdata, questions, answers)
    subjects = read_subjects(subjectcat, tree, survey_id_field)
    outdata = join(outdata, subjects, 'subject_id')
    return outdata
