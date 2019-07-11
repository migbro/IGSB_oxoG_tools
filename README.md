## Oxidative Damage Detection and Removal Tools
### Purpose: Especially on samples with variant calls heavy with C-to-A, G-to-T, to calculate FoxoG score, a metric for measuring oxidative damage and filter out offending variants to salvage data from the damaged sample

### Caveats:
Designed to run on a vm pulling from an object store therefore may need to change src_cmd variables to point to correct
novarc file.  Files also have expected suffixes

### TOOLS:

#### metalfox_pipe.py:
##### Description
Wrapper script to run an edited version of metalfox (original was obtained here:
https://github.com/cpwardell/bin/blob/master/metalfox.py) to calculate foxoG scored for each variant
##### Usage:

 ```
 ./metalfox_pipe.py -j <config_file> -sp <sample_pairs_list> -r <reference_mount> 
 ```

 Input description:

 config_file: json-formatted text file.  See example file - only relevant variables are:
 'tools':'metalfox', 'refs':'cont', 'refs':'obj', 'refs':'mapability', 'params':'threads', 'params':'ram'
 
 sample_pairs_list: tumor normal pairs as bionimbus ids, formatted as such:
 2016-123_2016-124  2016-123    2016-124
 
 reference_mount: Cinder block mount point or directory in which references have been downloaded in ephemeral mount

#### metal_fox.py
##### Description:
Can be run separately from above wrapper if only one sample to be used.  Need to have downloaded relevant files ahead
 of time
##### Usage:

```
./metalfox.py -f1 full path to exome directory -f full path to MuTect call_stats.out file -f3 full path to bam
-m mapability file
```

Input description:

f1:  Not sure and haven't used it.  It's optional and we haven't needed it for our purposes.

f: The .out file from mutect calls

f3: bam file that used for the .out output

m: optional mapability file
 
#### oxog_check.py
##### Description
 Runs picard CollectOxoGMetrics which give a sample/bam file global damage scores for each base change type.  Scores 
 above 30 are considered little to no damage, 20-30, concerning, and below 20 severe.
##### Usage: 

```
./oxog_check.py  -j <config_file> -f <lane_list> -r <reference_mount>
 ```

 Input description:

 config_file: json-formatted text file.  See example file - only relevant variables are:
 'tools':'java', 'tools':'picard', 'refs':'fa_ordered','refs':'intervals', 'refs':'cont', 'refs':'obj',
 'params':'threads', 'params':'ram'
 
 lane_list: Individual sample lane list in format:

 2016-129	capture	160308_D00422_0286_BHKH5JBCXX_1, 160308_D00422_0286_BHKH5JBCXX_2

 2016-128	capture	160308_D00422_0286_BHKH5JBCXX_1, 160308_D00422_0286_BHKH5JBCXX_2
 
 reference_mount: Cinder block mount point or directory in which references have been downloaded in ephemeral mount
 
#### calc_score_output_pass.py
##### Description
Downloads reports and adjusts based out metalfox output showing only variants that passed, limited to on-target
##### Usage:

```
./calc_score_output_pass.py <pair_list> <config_file>
```
 Input description:

pair_list: tumor normal pairs as bionimbus ids, formatted as such:

 2016-123_2016-124  2016-123    2016-124
 
 config_file: json-formatted text file.  See example file - only relevant variables are: 'refs':'cont', 'refs':'annotation'

#### oxog_summary.py
##### Description:
Summarizes all samples oxog damage from output of oxog_check.py
##### Usage:

```
./oxog_summary.py <file_list> <suffix>
```
 
 Input description:
 
 file_list: List of files output from oxog_check
 
 suffix: File suffix from output to remove from headers.  Typically '.oxo_summary.txt'
