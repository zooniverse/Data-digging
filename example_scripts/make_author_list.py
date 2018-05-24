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
    print("    --no_lookup, --nolookup")
    print("       Skip attempted lookup of credited_name (if not already supplied)")
    print("    len=N  (or length=N, line=N)")
    print("       If pre-formatted text, specifies max length of each line (default 72).")
    print("    outcsv=output_of_logged_in_users_only.csv")
    print("       If you want to save a copy of the input file but just for logged-in users")
    print(" The authors will be printed to the output file in the order they appear in the input file (minus not-logged-in users).")
    sys.exit(0)



def clean_email_str(thevalue):
    thestr = str(thevalue)
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
    if "." in thestr:
        for tt in thiswiththat:
            thestr = thestr.replace(tt[0], tt[1])

    return thestr




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


def get_credited_name_all(vols, whichtype='user_id'):
    x = panoptes_connect()

    disp_names = vols.copy()
    i_print = int(len(vols)/10)
    if i_print > 1000:
        i_print = 1000
    elif i_print < 10:
        i_print = 10

    if whichtype == 'user_id':
        # user ID lookup has a different format for the query
        for i, the_id in enumerate(vols):
            user = User.find(int(the_id))
            name_use = user.credited_name
            if name_use == '':
                name_use = user.display_name
                if name_use == '':
                    name_use = user.login

            disp_names.loc[(vols==the_id)] = name_use
            #credited_names[the_id] = user.credited_name
            if i % i_print == 0:
                print("Credited name: lookup %d of %d (%s --> %s)" % (i, len(vols), the_id, name_use))

    else:
        # if we're here we don't have user ID but presumably do have login
        for i, the_login in enumerate(vols):
            name_use = the_login
            for user in User.where(login=the_login):
                name_use = user.display_name
            #credited_names[the_login] = cname
            disp_names.loc[(vols==the_login)] = name_use
            if i % i_print == 0:
                print("Credited name: lookup %d of %d (%s --> %s)" % (i, len(vols), the_login, name_use))



    return disp_names






def get_credited_name(row, author_col, author_col_backup):
    x = panoptes_connect()


    # try standard columns plus whatever was supplied (if it's different)
    loginname_cols = ['user_name', 'username', 'login']
    # if author columns are supplied, try those first
    if (not (author_col_backup.isin(loginname_cols))) & (not (author_col_backup == '')):
        loginname_cols = [author_col_backup] + loginname_cols

    if (not (author_col.isin(loginname_cols))) & (not (author_col == '')):
        loginname_cols = [author_col] + loginname_cols

    try:
        userid = row[1]['user_id']
        user = User.find(int(userid))
        return user.credited_name

    except:
        login_col = ''
        for i_col in range(len(loginname_cols)):
            if loginname_cols[i_col] in row[1].keys():
                login_col = loginname_cols[i_col]
                break

        # if you only know the login you have to search panoptes_client in this way
        for user in User.where(login=login_col):
            return user.credited_name


        if login_col == '':
            # if you're here neither the user_id nor any of the login columns worked
            return login_col

        # you should never get here but hey ho
        return login_col










clean_emails = False
preformat = False
usecol_cl = False
out_logged_in = False
skip_lookup = False

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
        elif (arg[0] == "--no_lookup") | (arg[0] == "--nolookup"):
            skip_lookup = True
        elif (arg[0] == "col") | (arg[0] == "usecol"):
            usecol_cl = True
            author_col = arg[1]
        elif (arg[0] == "len") | (arg[0] == "length") | (arg[0] == "line") | (arg[0] == "linelength"):
            max_line_length_char = int(arg[1])
        elif (arg[0] == "outcsv"):
            out_logged_in = True
            outcsv = arg[1]

# you might be skipping the lookup because you don't have this installed
if not skip_lookup:
    from panoptes_client import User
    from panoptes_connect import panoptes_connect



# Ideally we'd use the user-supplied credited name, but if not available use their username
cols_to_try_preferred = ['credited_name', 'real_name', 'display_name']
login_cols = ['user_name', 'username', 'login']
cols_to_try_backup = login_cols + ['user_id']
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

author_col_backup = author_col

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
# now, try to look up the credited name if we don't already have it
elif ('user_id' in authorlist.columns) & (not skip_lookup):
    authorlist['name_merged'] = get_credited_name_all(authorlist['user_id'])
    author_col = 'name_merged'
else:
    if not skip_lookup:
        for thename in login_cols:
            if thename in authorlist.columns:
                authorlist['name_merged'] = get_credited_name_all(authorlist[thename], whichtype=thename)
                author_col = 'name_merged'
                break


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
    #author_backup = row[0]
    author_backup = row[1][author_col_backup]

    if not isinstance(author, basestring):
        author = str(author)

    if not isinstance(author_backup, basestring):
        author_backup = str(author_backup).strip()

    if len(author) < 1:
        if len(author_backup) < 1:
            i_blank += 1
        else:
            author = author_backup

    if clean_emails:
        author = clean_email_str(author)

    if len(linestr) + len(author) > max_line_length_char:
        fout.write("%s\n" % linestr.encode('utf-8'))
        linestr = prepend

    linestr += author.strip()

    if i_line < n_lines - 1:
        linestr += ", "


# print the last line, if there is one
if len(linestr) > 1:
    try:
        fout.write("%s\n" % linestr.encode('utf-8'))
    except:
        fout.write("%s\n" % linestr.encode('utf8', 'replace'))


fout.close()

print("Author list printed in markdown to %s." % outfile)
print(" Logged-in user count: %d" % len(authorlist))
if i_blank > 0:
    print(" Blank user name count: %d" % i_blank)

if out_logged_in:
    # if we don't set an index an extra i_index col gets printed to the file
    #authorlist.set_index(author_col, inplace=True)
    authorlist.to_csv(outcsv, encoding='utf-8')
    print("Logged-in-only list saved to %s." % outcsv)



#end
