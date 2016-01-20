#!/usr/bin/env python
'''
Adjusts report output according to foxoG filter score and summarizes results

Usage: ./calc_score_output_pass.py <pair_list> <config_file>

Arguments:
<pair_list>     list of pairs that were run
<config_file>   json file with parameters pertaining to object store locations

Options
-h

'''

import json
import sys
import pdb
sys.path.append('/home/ubuntu/TOOLS/Scripts/utility')
from date_time import date_time
import subprocess
from docopt import docopt


def parse_config(config_file):
    config_data = json.loads(open(config_file, 'r').read())
    return (config_data['refs']['cont'], config_data['refs']['annotation'])


def calc_pass(foxog, tlod, coeff1, coeff2):
    state = 'FAIL'
    # pdb.set_trace()
    score = float(coeff1) + (float(coeff2) * float(foxog))
    if float(tlod) > score:
        state = 'PASS'
    return (score, state)


args = docopt(__doc__)
config_file = args['<config_file>']
src_cmd = '. ~/.novarc;'
deproxy = 'unset http_proxy; unset https_proxy;'

fh = open(args['<pair_list>'])
(cont, anno_dir) = parse_config(config_file)

# score calculation for passing grade: tumor_lod > 10 + (100/3) FoxoG
coeff1 = 10
coeff2 = float(100 / 3)
# makes custom capture assumption, may need some work to be more flexible
sys.stdout.write('Sample\toriginal on target\toriginal off target\tfiltered on target\tfiltered off target\n')

for line in fh:
    line = line.rstrip('\n')
    pair = line.split('\t')
    sys.stderr.write(date_time() + 'Getting files for ' + pair[0] + '\n')
    report = anno_dir + '/' + pair[0] + '/OUTPUT/' + pair[0] + '.vcf.keep.eff.xls'
    metalfox_out = 'FOXOG/' + pair[0] + '.foxog_scored_added.out'
    get_files = src_cmd + deproxy + 'swift download ' + cont + ' ' + report + ' ' + metalfox_out\
                + ' >> dl.log 2>> dl.log'
    subprocess.call(get_files, shell=True)
    sys.stderr.write(date_time() + 'Processing\n')
    mo = open(metalfox_out, 'r')
    ro = open(report, 'r')
    head = next(ro)
    # create filtered report and a score summary in case one  wants to review and adjust coefficients
    cur = pair[0] + '.report_filtered.xls'
    score_sum = pair[0] + '.score_summary.txt'
    score_sum_out = open(score_sum, 'w')
    score_sum_out.write('chr\tpos\tgene\ttumor_lod\toxo score\tstate\n')
    cur_out = open(cur, 'w')
    cur_out.write(head)
    skip = next(mo)
    sys.stdout.write(pair[0])
    # initialize summary variables
    orig = {'ON': 0, 'OFF': 0}
    filt = {'ON': 0, 'OFF': 0}
    for entry in mo:
        rpt_entry = next(ro)
        report_info = rpt_entry.rstrip('\n').split('\t')
        gene = report_info[13]
        info = entry.rstrip('\n').split('\t')
        chrom = info[0]
        pos = info[1]
        tlod = info[18]
        foxog = info[51]
        target = report_info[-1]
        orig[target] += 1
        if foxog == 'NA':
            cur_out.write(rpt_entry)
            score_sum_out.write('\t'.join((chrom, pos, gene, tlod, foxog, 'NA')) + '\n')
            filt[target] += 1
        else:
            (score, state) = calc_pass(foxog, tlod, coeff1, coeff2)
            if state == 'PASS':
                cur_out.write(rpt_entry)
                filt[target] += 1
            score_sum_out.write('\t'.join((chrom, pos, gene, tlod, str(score), state)) + '\n')
    mo.close()
    score_sum_out.close()
    cur_out.close()
    sys.stdout.write('\t' + '\t'.join((str(orig['ON']), str(orig['OFF']), str(filt['ON']), str(filt['OFF']))) + '\n')
fh.close()
sys.stderr.write(date_time() + 'Process  complete\n')
