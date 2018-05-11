import sys, os
import pandas as pd
import numpy as np

try:
    infile1 = sys.argv[1]
    infile2 = sys.argv[2]

except:

    print("Usage:\n > %s namefile_nocredited.csv namefile_withcredited.csv [namefile_out_matched.csv]")
    print("  This program is only needed if you have the usernames in the order you want them in the first file *but* no credited names, and with the credited_name / display_name you want to use in the second file *but* with no way to rank them properly by the second file alone.")
    sys.exit(0)

login1 = pd.read_csv(infile1)
login2 = pd.read_csv(infile2)

try:
    outfile = sys.argv[3]
except:
    outfile = infile1.replace(".csv", "_matched_credited.csv")

cols_to_try = ['user_name', 'username', 'login', 'user_id']


author_col1 = ''
for i_col in range(len(cols_to_try)):
    if cols_to_try[i_col] in login1.columns:
        author_col1 = cols_to_try[i_col]
        break

author_col2 = ''
for i_col in range(len(cols_to_try)):
    if cols_to_try[i_col] in login2.columns:
        author_col2 = cols_to_try[i_col]
        break


if author_col1 == '':
    print("OOPS: no author column found in %s! Nothing to match on, exiting." % infile1)
    exit(0)
if author_col2 == '':
    print("OOPS: no author column found in %s! Nothing to match on, exiting." % infile2)
    exit(0)


login_both = pd.merge(login1, login2, left_on=author_col1, right_on=author_col2, suffixes=('', '_2'))

login_both.to_csv(outfile)
print("... matched file with %d rows saved to %s." % (len(login_both), outfile))


# end
