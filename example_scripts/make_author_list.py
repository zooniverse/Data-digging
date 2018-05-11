import sys, os
import numpy as np
import pandas as pd

# I know there is a command-line arg parser package but I haven't gotten around to checking it out
try:
    infile = sys.argv[1]
    outfile = sys.argv[2]
except:
    print("\nUsage: %s users_infile authors_outfile" % sys.argv[0])
    print("      users_infile is a list of usernames, technically a CSV, with column names")
    print("       'credited_name' or 'real_name' (preferred) or the variations on username: 'user', 'user_name', 'username', 'user_id'.")
    print("      The input file can be a user-classification file output by basic_project_stats.py, e.g.\n your-project-name-classifications_nclass_byuser_ranked.csv")
    print("      The output file will be in markdown, e.g. authorlist_out.md")
    print("  Optional extra inputs (no spaces):")
    print("    --clean_emails")
    print("       Try to clean usernames of email addresses etc that might be farmed by bots when these are displayed on the project")
    print("    --pre, --preformatted")
    print("       output the list in pre-formatted tags so markdown won't render")
    print("    col=col_name")
    print("       if the name of your Author name column isn't standard, specify it")
    print("    len=N  (or length=N, line=N)")
    print("       If pre-formatted text, specifies max length of each line (default 72).")
    print("    outcsv=output_of_logged_in_users_only.csv")
    print("       If you want to save a copy of the input file but just for logged-in users")
    print(" The authors will be printed to the output file in the order they appear in the input file (minus not-logged-in users).")
    sys.exit(0)



def clean_email_str(str):
    # alas there are plenty of . characters that shouldn't be replaced
    # so we have to be more specific
    thiswiththat = [
    ("@", "at"),
    (".hotmail", "dothotmail"),
    (".gmail", "dotgmail"),
    (".googlemail", "dotgooglemail"),
    (".yahoo", "dotyahoo"),
    (".ymail", "dotymail"),
    (".com", "dotcom"),
    (".co.", "dotcodot"),
    (".org", "dotorg"),
    (".net", "dotnet"),
    (".edu", "dotedu"),
    (".ac.", "dotacdot"),
    (".au", "dotau"),
    (".gov.", "dotgovdot"),
    (".gov", "dotgov"),
    (".biz", "dotbiz"),
    (".COM", "dotCOM"),
    (".CO.", "dotCOdot"),
    (".ORG", "dotORG"),
    (".NET", "dotNET"),
    (".EDU", "dotEDU"),
    (".AC.", "dotACdot"),
    (".AU", "dotAU"),
    (".GOV.", "dotGOVdot"),
    (".GOV", "dotGOV"),
    (".BIZ", "dotBIZ")
    ]

    # if there isn't a ., save some time
    if "." in str:
        for tt in thiswiththat:
            str = str.replace(tt[0], tt[1])

    return str




def get_best_name(row, author_col, author_col_backup):
    author        = row[1][author_col]
    author_backup = row[1][author_col_backup]

    try:
        if np.isnan(author):
            use_alt = True
        else:
            # if you haven't already failed it's a float but it's not a nan
            # which is weird but uh, go with it
            return str(author)
    except:
        if author == '':
            use_alt = True
        else:
            return author

    # there's no way to still be in the function and not have use_alt be True
    # so I'm just being explicit
    if use_alt:
        if type(author_backup) is float:
            if np.isnan(author_backup):
                return ''
            else:
                return author_backup
        else:
            return author_backup

    # you should never get here but hey ho
    return str(author)






clean_emails = False
preformat = False
usecol_cl = False
out_logged_in = False

# matters if preformatted, if not it's just to make the file itself easier to read
max_line_length_char = 72

# check for other command-line arguments
if len(sys.argv) > 2:
    # if there are additional arguments, loop through them
    for i_arg, argstr in enumerate(sys.argv[2:]):
        arg = argstr.split('=')

        if (arg[0] == "--clean_emails") | (arg[0] == "--clean"):
            clean_emails = True
        elif (arg[0] == "--pre") | (arg[0] == "--preformatted") | (arg[0] == "--preformat"):
            preformat = True
        elif (arg[0] == "col") | (arg[0] == "usecol"):
            usecol_cl = True
            author_col = arg[1]
        elif (arg[0] == "len") | (arg[0] == "length") | (arg[0] == "line") | (arg[0] == "linelength"):
            max_line_length_char = int(arg[1])
        elif (arg[0] == "outcsv"):
            out_logged_in = True
            outcsv = arg[1]


# Ideally we'd use the user-supplied credited name, but if not available use their username
cols_to_try_preferred = ['credited_name', 'real_name', 'display_name']
cols_to_try_backup = ['user_name', 'username', 'login', 'user_id']
# use the first column name if it exists, then the second, etc.
cols_to_try_ranked = ['name_merged'] + cols_to_try_preferred + cols_to_try_backup


# Read the infile
authorlist_all = pd.read_csv(infile)



# figure out the user column

if usecol_cl:
    if not (author_col in authorlist_all.columns):
        print("OOPS: specified author column name not in infile!")
        print("  Trying standard column names...")
        usecol_cl = False


if not usecol_cl:
    author_col = ''
    for i_col in range(len(cols_to_try_ranked)):
        if cols_to_try_ranked[i_col] in authorlist_all.columns:
            author_col = cols_to_try_ranked[i_col]
            break

    if author_col == '':
        print("OOPS: no author column found! Nothing to print, exiting.")
        exit(0)

# credited name is not always supplied so we need a backup column
if author_col in cols_to_try_preferred:
    author_col_backup = ''
    for i_col in range(len(cols_to_try_backup)):
        if cols_to_try_backup[i_col] in authorlist_all.columns:
            author_col_backup = cols_to_try_backup[i_col]
            break

    if author_col_backup == '':
        print("WARNING: no backup author column found! There may be blank entries.")



# great, we have an author column and we can start working with it.
# first things first: we can only credit logged-in users
is_unreg = [q.startswith("not-logged-in") for q in authorlist_all[author_col].astype(str)]
is_reg   = np.invert(is_unreg)

if sum(is_reg) < 1:
    print("OOPS: no registered users to give credit to! Exiting...")
    exit(0)

authorlist = authorlist_all[is_reg]

if author_col in cols_to_try_preferred:
    # deal with blank user-supplied columns
    authorlist['name_merged'] = [get_best_name(q, author_col, author_col_backup) for q in authorlist.iterrows()]
    author_col = 'name_merged'


# these are unnecessary if you're running this from a prompt but if you're copy-pasting in iPython they're needed so things below don't break
try:
    del fout
except:
    pass

# this is a markdown file
fout = open(outfile, "w")

if preformat:
    # preformatting in markdown is marked with spaces at the start of a line
    prepend = "    "
else:
    prepend = ""


i_line = 0
i_blank = 0
n_lines = len(authorlist)

# string assignments like this are copies so it doesn't need to be .copy()
linestr = prepend

for i_line, row in enumerate(authorlist.iterrows()):
    author = row[1][author_col]
    author_backup = row[1][author_col_backup]

    if author == '':
        if author_backup == '':
            i_blank += 1
        else:
            author = author_backup

    if clean_emails:
        author = clean_email_str(author)

    if len(linestr) + len(author) > max_line_length_char:
        fout.write("%s\n" % linestr)
        linestr = prepend

    linestr += author

    if i_line < n_lines - 1:
        linestr += ", "


# print the last line, if there is one
if len(linestr) > 1:
    fout.write("%s\n" % linestr)



fout.close()

print("Author list printed in markdown to %s." % outfile)
print(" Logged-in user count: %d" % len(authorlist))
if i_blank > 0:
    print(" Blank user name count: %d" % i_blank)

if out_logged_in:
    # if we don't set an index an extra i_index col gets printed to the file
    authorlist.set_index(author_col, inplace=True)
    authorlist.to_csv(outcsv)
    print("Logged-in-only list saved to %s." % outcsv)



#end
