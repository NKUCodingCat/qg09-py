def submit_pbs_job(job_file, jobs, args):

    bfile = job_file
    qfile, qerr, qout = bfile+".pbs", bfile+".ER", bfile+".OU"
    queue, nodes, mem = args.q, args.n, args.m

    pbs_header = "\n".join([
       "#!/bin/bash -l",
       "#",
       "# Job: {}",
       "#",
       "#",
       "# qg09_py version {}",
       "#",
       "# To submit this script to the queue type:",
       "#    qsub {}",
       "#", ""]).format(bfile, __VERSION__, qfile)


    pbs_resources = "#PBS -m " + ( "e" if args.e == "yes" else "n" ) + " \n"

    extra_options  = args.x + ":" if "" != args.x else ""
    if "" != args.l : pbs_resources += "#PBS -l %s\n" % args.l

    pbs_resources += "\n".join([
        "#PBS -l nodes={}:{}ppn={}",
        "#PBS -l walltime={}",
        "#PBS -l mem={}mb",
        "#PBS -e {}",
        "#PBS -o {}",
        "#PBS -q {}",
        "",
        "",
        "cd $PBS_O_WORKDIR",
        "",
        "",
        "ulimit -s unlimited", ""]).format(nodes, extra_options, args.p, args.t, mem, qerr, qout, queue)


    if args.n > 1: pbs_resources += 'uniq $PBS_NODEFILE | xargs -I {} ssh {} mkdir -p ' + args.s +  "\n"

    with open(qfile, "w") as submit_fh:
        print >>submit_fh, pbs_header + pbs_resources + "\n# >>> PBS envs <<< \n" + args.PBS_envs + "\n# >>> PBS envs ends <<< \n"
        for i in jobs: print >>submit_fh, i

    if args.r == "yes" : 
        print "The calculation {} has been submitted".format(qfile)
        import os; os.system("qsub " + qfile)
    else:
        print "The queue script {} has been created".format(qfile)
        print "To run the calculation type: qsub " + qfile

def fix_input(Gau_job_text, Res_regex, Res_value):
    # Input must be generated as handle.read()
    # Replace Res_regex resource line in Gaufile to Res_value
    # Eg. \%nprocs[^=]+=[^=]+$ will match a line %nprocs=1 => %NprocShared=16
    # Use **re.match** to determine and subplace the **WHOLE** line

    import StringIO; buf = StringIO.StringIO(Gau_job_text)

    Out = buf.readlines()
    is_resource_line_exist = False

    for i, v in enumerate(Out):
        if re.match(Res_regex, v, flags=re.IGNORECASE): 
            is_resource_line_exist = True
            Out[i] = Res_value
    if not is_resource_line_exist: Out = [Res_value, ] + Out

    return "\n".join(map(lambda x: x.rstrip(), Out))

def make_Gau_job_Block(Gau_inp_filename, Gau_log_filename, args):
    return "\n".join([
        "",
        "cd {}",
        "mkdir -p {}",
        "export GAUSS_SCRDIR={}",
        "/usr/bin/time g09 < {} >& {}",
        "rm {}/*.rwf",
        "",
    ]).format(
        args.Work_dir,
        args.s,
        args.s,
        Gau_inp_filename, Gau_log_filename,
        args.s
    )

# TODO: a merge config function

# ================ MAIN ========================

import argparse, re, humanfriendly, copy, os

__VERSION__ = "0.0.1"

Defaults = {
    "Options_default":{
        'b': 1,
        'e': "no",
        'l': "no",
        'm': "15000mb",
        'n': "1",
        'p': 20,
        'q': "batch",
        'r': "no",
        's': "local",
        't': "168:00:00",
        'x': "",
    },
    
    "Scratch_maps": {
        "local": "/tmp/",
        "~": "$HOME"
    },

    "PBS_envs": "export PATH=/opt/nbo6/bin:$PATH \nexport GAUSS_EXEDIR=/opt/soft/g09_E01_Purdue/g09/bsd:/opt/soft/g09_E01_Purdue/g09:/opt/soft \nsource /opt/soft/g09_E01_Purdue/g09/bsd/g09.profile \nexport GAUSS_EXEDIR=/opt/soft/g09_E01_Purdue/g09:$GAUSS_EXEDIR\n"
}

# TODO:  system admin override default here => ./qg09rc
# TODO:          user override default here => $HOME/.qg09rc
# TODO: Working space override default here => $PWD/qg09rc

# ========= Args Check functions & arguments ================

def Check_time_string(string):
    if None == re.match(r"\d+:\d\d:\d\d", string):
        msg = "%r does not fit format: hh:mm:ss" % string
        raise argparse.ArgumentTypeError(msg)
    return string

def Check_mem_string(string):
    try:
        m = humanfriendly.parse_size(string, binary=True)/float(1<<20)
        if m < 256: print "\n!! WARNING: Memory is smaller than 256MB !!\n"
        return int(m)
    except:
        raise argparse.ArgumentTypeError("Cannot parse memory string: %s"%string)

def Check_scr_string(string):
    t = Defaults["Scratch_maps"]
    if string in t:
        return t[string]
    else:
        print "\n!! WARNING: you are using scratch %s, Please ensure what you are doing !!\n"%string
        return string

def Check_gau_inp(string):
    if os.path.isfile(string): return string
    else: raise argparse.ArgumentTypeError("Gaussian input file %s does not exist!"%string)

parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-b', help='the number of files in each batch job', type=int, default=Defaults["Options_default"]["b"])
parser.add_argument('-e', help='email notification when ended?', type=str, choices=['yes', 'no'], default=Defaults["Options_default"]["e"])
parser.add_argument('-l', help='email notification when job ended?', type=str, choices=['yes', 'no'], default=Defaults["Options_default"]["l"])
parser.add_argument('-m', help='memory used per node <Amomut><Unit>', type=Check_mem_string, default=Defaults["Options_default"]["m"])
parser.add_argument('-n', help='the number of nodes used', type=int, default=Defaults["Options_default"]["n"])
parser.add_argument('-p', help='the number of processors used per node', type=int, default=Defaults["Options_default"]["p"])
parser.add_argument('-q', help='the queue to submit the job', default=Defaults["Options_default"]["q"])
parser.add_argument('-r', help='submit the job?', type=str, choices=['yes', 'no'], default=Defaults["Options_default"]["r"])
parser.add_argument('-s', help='scratch space to use (<Absolute path> / {})'.format(" / ".join(map(lambda x: "\"%s\""%str(x), Defaults["Scratch_maps"].keys()))), type=Check_scr_string, default=Defaults["Options_default"]["s"])
parser.add_argument('-t', help='the amount of wall clock time (format: hh:mm:ss)', type=Check_time_string, default=Defaults["Options_default"]["t"])
parser.add_argument('-x', help='additional PBS node features required', default=Defaults["Options_default"]["x"])

parser.add_argument('Gau_inputs', nargs="+", type=Check_gau_inp, help='Gaussian INPUT file (*.com or *.gjf)')

args = parser.parse_args()

# ========== Parse args done, start some patch =============

vars(args)["PBS_envs"] = Defaults["PBS_envs"]
vars(args)["Work_dir"] = os.getcwd()
print args


# TODO: filename/file process

# Target: Read Gaussian inputs file then make batch pbs 

Q = open(args.Gau_inputs[0]).read()
Q = fix_input(Q, "^%nprocs[^=]+=[^=]+$", "%%NProcShared=%d"%args.p)
Q = fix_input(Q, "^%mem[^=]+=[^=]+$",    "%%mem=%d"%args.m)
print Q

S = make_Gau_job_Block(args.Gau_inputs[0], args.Gau_inputs[0]+".log", copy.deepcopy(args))


submit_pbs_job("oxoium", [S, ], copy.deepcopy(args))