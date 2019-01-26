import sys, os
import numpy as np
import pandas as pd
import logging



def clean_email_str(thevalue):
    if isinstance(thevalue, basestring):
        thestr = thevalue
    else:
        thestr = str(thevalue).decode('utf-8').encode('utf-8', 'replace')

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
    (".ca", "dotca"),
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
    (".CA", "dotCA"),
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







def get_credited_name_all(vols, whichtype='user_id', verbosity=2):
    from panoptes_client import User

    # nevermind, we don't need this because credited names and usernames are public
    # from panoptes_connect import panoptes_connect

    # x = panoptes_connect()

    disp_names = vols.copy()
    i_print = int(len(vols)/10)
    if i_print > 1000:
        i_print = 1000
    elif i_print < 10:
        i_print = 10


    # print("whichtype = %s" % whichtype)


    # we can look up the credited_name either via user_id or user_name
    # currently classification exports call it "user_name" and the Panoptes DB
    #    calls it "login"

    missing_ids = []

    if whichtype == 'user_id':
        # user ID lookup has a different format for the query

        # also it fails with an error instead of a 0-length array
        # so let's catch those but keep trying

        for i, the_id in enumerate(vols):
            id_ok = True
            try:
                user = User.find(int(the_id))
            except Exception as e:
                id_ok = False
                print(e)
                missing_ids.append(int(the_id))

            if id_ok:
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
                if i % i_print == 0:
                    print("Credited name: lookup %d of %d (%s --> ___MISSING_OR_ERROR___%d___)" % (i, len(vols), the_id, len(missing_ids)))
               


    else:
        # if we're here we don't have user ID but presumably do have login/username
        for i, the_login in enumerate(vols):
            name_use = the_login
            the_user = User.where(login=the_login)
            if the_user.object_count > 0:
                for user in the_user:
                    try:
                        name_use = user.credited_name
                    except:
                        name_use = user.display_name
                #credited_names[the_login] = cname
                disp_names.loc[(vols==the_login)] = name_use
                if i % i_print == 0:
                    print("Credited name: lookup %d of %d (%s --> %s)" % (i, len(vols), the_login, name_use))
            else:
                # the name lookup didn't work, so save it
                missing_ids.append(the_login)
                print("  WARNING: User not found: %s" % the_login)
                if i % i_print == 0:
                    print("Credited name: lookup %d of %d (%s --> ___MISSING_OR_ERROR___%d___)" % (i, len(vols), the_login, len(missing_ids)))



    if (len(missing_ids) > 0) & (verbosity > 0):
        print(" WARNING: id search turned up %d bad result(s), your list may be incomplete!" % len(missing_ids))

        if verbosity >= 2:
            print("  Here are the ids it returned an error on:")
            print(missing_ids)



    return disp_names






def make_userfile_from_classfile(classfile):
        cols_keep = ["classification_id", "user_name", "user_id", "user_ip"]  # , "workflow_id", "workflow_version"]
        try:
            classifications = pd.read_csv(classfile, usecols=cols_keep)
        except:
            # if this breaks something's gone very wrong (these cols should always be present) so you want it to crash
            classifications = pd.read_csv(classfile, usecols=["classification_id", "user_name"])

        # we don't need unregistered users
        is_unreg_class = [q.startswith("not-logged-in") for q in classifications.user_name]
        class_reg = classifications[np.invert(is_unreg_class)].copy()
        by_user = class_reg.groupby("user_name")

        # we could just do classifications.user_name.unique() but this doesn't take that long
        # and adds lots of info, so why not?
        nclass_byuser = by_user.classification_id.aggregate("count")

        nclass_byuser.name = 'user_name'
        nc_unranked = pd.DataFrame(nclass_byuser)
        nc_unranked.columns = ['n_class']

        if "user_id" in classifications.columns:
            user_ids = by_user['user_id'].first()
            nc_unranked['user_id'] = user_ids

        nclass_byuser_ranked = nc_unranked.copy()
        nclass_byuser_ranked.sort_values('n_class', inplace=True, ascending=False)

        nclass_file = classfile.replace(".csv", "_userlist_with_nclass.csv")
        # just in case the infile doesn't have .csv? shouldn't happen but just in case
        if nclass_file == classfile:
            nclass_file = classfile + "_userlist_with_nclass.csv"

        nclass_byuser_ranked.to_csv(nclass_file)
        
        print("Extracted %d users from %d registered classifications and saved to %s..." % (len(nclass_byuser_ranked), len(class_reg), nclass_file))

        return nclass_file







def make_author_list(infile, outfile, clean_emails=False, preformat=False, usecol_cl=False, author_col=None, skip_lookup=False, out_logged_in=False, outcsv=None, max_line_length_char=72):

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Ideally we'd use the user-supplied credited name, but if not available use their username
    cols_to_try_preferred = ['credited_name', 'real_name', 'display_name']
    login_cols = ['user_name', 'username', 'login']
    cols_to_try_backup = login_cols + ['user_id']
    # use the first column name if it exists, then the second, etc.
    cols_to_try_ranked = ['name_merged'] + cols_to_try_preferred + cols_to_try_backup


    # Read the infile
    authorlist_all = pd.read_csv(infile)



    # figure out the user column

    # if a column has been manually specified, use it, always
    if author_col is not None:
        usecol_cl = True



    if usecol_cl:
        if not (author_col in authorlist_all.columns):
            logger.warn("OOPS: specified author column name not in infile!\n  Trying standard column names...")
            usecol_cl = False


    if not usecol_cl:
        author_col = ''
        for i_col in range(len(cols_to_try_ranked)):
            if cols_to_try_ranked[i_col] in authorlist_all.columns:
                author_col = cols_to_try_ranked[i_col]
                break

        if author_col == '':
            logger.error("OOPS: no author column found! Nothing to print, exiting.")
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
            logger.warn("WARNING: no backup author column found! There may be blank entries.")



    # great, we have an author column and we can start working with it.
    # first things first: we can only credit logged-in users
    is_unreg = [q.startswith("not-logged-in") for q in authorlist_all[author_col].astype(str)]
    is_reg   = np.invert(is_unreg)

    if sum(is_reg) < 1:
        logger.error("OOPS: no registered users to give credit to! Exiting...")
        exit(0)

    authorlist = authorlist_all[is_reg]

    if author_col in cols_to_try_preferred:
        # deal with blank user-supplied columns
        authorlist['name_merged'] = [get_best_name(q, author_col, author_col_backup) for q in authorlist.iterrows()]
        author_col = 'name_merged'
    # now, try to look up the credited name if we don't already have it
    # if it's specified what we need to use, use that. Otherwise try to use user_id, or if not, use what you have
    elif usecol_cl & (author_col != 'user_id'):
        print("Using column %s to determine author list..." % author_col)
        authorlist['name_merged'] = get_credited_name_all(authorlist[author_col], whichtype=author_col)
        author_col = 'name_merged'   
    elif ('user_id' in authorlist.columns) & (not skip_lookup):
        print("Using column user_id to determine author list...")
        authorlist['name_merged'] = get_credited_name_all(authorlist['user_id'])
        author_col = 'name_merged'
    else:
        if not skip_lookup:
            for thename in login_cols:
                if thename in authorlist.columns:
                    print("Using column %s to determine author list..." % thename)
                    authorlist['name_merged'] = get_credited_name_all(authorlist[thename], whichtype=thename)
                    author_col = 'name_merged'
                    break


    # try to write the file but if you come up with an error for some reason,
    # still return the author list back so you don't have to start from scratch next time
    try:

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
                # the strings are generally not unicode so we have to decode first, then encode
                # I mean, maybe, unless that crashes it
                try:
                    fout.write("%s\n" % linestr.decode('utf-8').encode('utf-8'))
                except:
                    try:
                        fout.write("%s\n" % linestr.decode('utf-8').encode('utf-8', 'replace'))
                    except:
                        fout.write("%s\n" % linestr.encode('utf-8'))
                linestr = prepend

            linestr += author.strip()

            if i_line < n_lines - 1:
                linestr += ", "


        # print the last line, if there is one
        if len(linestr) > 1:
            try:
                fout.write("%s\n" % linestr.decode('utf-8').encode('utf-8'))
            except:
                try:
                    fout.write("%s\n" % linestr.decode('utf-8').encode('utf-8', 'replace'))
                except:
                    fout.write("%s\n" % linestr.encode('utf-8'))

        fout.close()

        logger.info("Author list saved in markdown to %s." % outfile)
        logger.info(" Logged-in user count: %d" % len(authorlist))
        if i_blank > 0:
            logger.info(" Blank user name count: %d" % i_blank)

        if out_logged_in:
            # if we don't set an index an extra i_index col gets printed to the file
            #authorlist.set_index(author_col, inplace=True)
            authorlist.to_csv(outcsv, encoding='utf-8')
            logger.info("Logged-in-only list saved to %s." % outcsv)


        return authorlist

    except Exception, e:
        logger.error('Failed to write to files: ' + str(e), exc_info=True)
        logger.info(" Returning author list so you don't have to start from scratch")
        return authorlist

    # end of make_author_list()






def make_author_list_help():
    print("\nUsage: (users_infile, outfile, clean_emails=False, preformat=False, usecol_cl=False, author_col=None, skip_lookup=False, out_logged_in=False, outcsv=None, max_line_length_char=72, is_classfile=False)")
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
    print("    --is_classfile")
    print("       If you don't have a file of unique logged-in users and your input file is instead a classification export file")
    print(" The authors will be printed to the output file in the order they appear in the input file (minus not-logged-in users).")



# if this is a command-line call etc.

if __name__ == '__main__':


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
        print("  Optional extra inputs (no spaces before/after = sign, if used):")
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
        print("    --is_classfile")
        print("       If you don't have a file of unique logged-in users and your input file is instead a classification export file")
        print(" The authors will be printed to the output file in the order they appear in the input file (minus not-logged-in users).")
        sys.exit(0)

    clean_emails = False
    preformat = False
    usecol_cl = False
    out_logged_in = False
    skip_lookup = False
    author_col = None
    outcsv=None
    is_classfile=False

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
            elif (arg[0] == "col") | (arg[0] == "usecol") | (arg[0] == "author_col"):
                usecol_cl = True
                author_col = arg[1]
            elif (arg[0] == "len") | (arg[0] == "length") | (arg[0] == "line") | (arg[0] == "linelength"):
                max_line_length_char = int(arg[1])
            elif (arg[0] == "outcsv"):
                out_logged_in = True
                outcsv = arg[1]
            elif (arg[0] == "--is_classfile") | (arg[0] == "--classfile"):
                is_classfile=True


    # if we don't yet have a users file, we need to make one first.
    # it's better to use basic_classification_processing.py to make one, but this quick-and-dirty will work.
    if is_classfile:
        infile_class = infile
        infile = make_userfile_from_classfile(infile)


    make_author_list(infile, outfile, clean_emails=clean_emails, preformat=preformat, usecol_cl=usecol_cl, author_col=author_col, skip_lookup=skip_lookup, out_logged_in=out_logged_in, outcsv=outcsv, max_line_length_char=max_line_length_char)



#end
