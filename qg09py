#!/usr/bin/env python2.7

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
        import os, sys

        if args.verbose: print "The calculation {} has been submitted".format(qfile)
        else: 
            print qfile, "\t\t", 
            sys.stdout.flush()  # It is ... It is a feature
        os.system("qsub " + qfile)
    else:
        if args.verbose: print "The queue script {} has been created\nTo Run the Calculation type: qsub {}".format(qfile, qfile)
        else: print qfile, "Unsubmitted"

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

    return "\n".join(map(lambda x: x.rstrip(), Out)) + "\n"

def make_Gau_job_Block(Gau_inp_filename, Gau_log_filename, work_dir, scr_dir):

    A = "\n".join([
        "",
        "cd {}",
        "mkdir -p {}",
        "export GAUSS_SCRDIR=\"{}\"", 
        "export QG09_GAU_INP_FILE=\"{}\"",
        "export QG09_GAU_LOG_FILE=\"{}\"", ""]).format(
            work_dir,
            scr_dir,
            scr_dir,
            Gau_inp_filename,
            Gau_log_filename
        )
    
    B = "\n".join([
        "/usr/bin/time g09 < $QG09_GAU_INP_FILE >& $QG09_GAU_LOG_FILE",
        "if ls \"{}/*.rwf\" 2>&1; then rm \"{}/*.rwf\"; fi ", ""
    ]).format(
        scr_dir, scr_dir
    )

    return A, B

def Merge_Config(Default_cfg, Override_config):
    
    Default_cfg = copy.deepcopy(Default_cfg)

    for key in Default_cfg.keys():
        if key in Override_config:
            if isinstance(Default_cfg[key], dict):
                # Merge dictDefauDefault_cfg
                assert isinstance(Override_config[key], dict), "Overriding config key %s is not a dictionary"
                Default_cfg[key].update(Override_config[key])
            else:
                # replace value
                Default_cfg[key] = Override_config[key]
    
    return Default_cfg

# ============= Args checking functions ========

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
        string=os.path.realpath(string)
        print "\n!! WARNING: you are using scratch %s, Please ensure what you are doing !!\n"%string
        return string

def Check_gau_inp(string):
    if os.path.isfile(string): return string
    else: raise argparse.ArgumentTypeError("Gaussian input file \"%s\" does not exist!"%string)

# ================ MAIN ========================

import argparse
import copy
import os
import pprint
import re
import time

import commentjson
import humanfriendly

__VERSION__ = "0.2.1"
__AUTHOR__  = "NKUCodingCat"

Defaults = {
    "Options_default":{
        'b': 1,
        'e': "no",
        'f': "Gau_batch_",
        'l': "",
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

    "PBS_envs": "",
    "Pre_run_Gaussian":  "",
    "Post_run_Gaussian": "",
}


for i in [ os.path.join(os.path.split(os.path.realpath(__file__))[0], "qg09.jsonc"), os.path.join(os.path.expanduser("~"), ".qg09.jsonc"), os.path.join(os.getcwd(), "qg09.jsonc")  ]:
    if os.path.isfile(i):
        with open(i) as conf:
            Defaults = Merge_Config(Defaults, commentjson.loads(conf.read()))

# ========= Args Check functions & arguments ================


parser = argparse.ArgumentParser(prog="qg09py", description="qg09-py Ver %s - Process multiple Gaussian input as torque jobs"%__VERSION__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-b', help='the number of files in each batch job', type=int, default=Defaults["Options_default"]["b"])
parser.add_argument('-e', help='email notification when ended?', type=str, choices=['yes', 'no'], default=Defaults["Options_default"]["e"])
parser.add_argument('-f', help='the preFix of multi jobs pbs file name', type=str, default=Defaults["Options_default"]["f"])
parser.add_argument('-l', help='addition to PBS resource list', type=str, default=Defaults["Options_default"]["l"])
parser.add_argument('-m', help='memory used per node <Amomut><Unit>', type=Check_mem_string, default=Defaults["Options_default"]["m"])
parser.add_argument('-n', help='the number of nodes used', type=int, default=Defaults["Options_default"]["n"])
parser.add_argument('-p', help='the number of processors used per node', type=int, default=Defaults["Options_default"]["p"])
parser.add_argument('-q', help='the queue to submit the job', default=Defaults["Options_default"]["q"])
parser.add_argument('-r', help='submit the job?', type=str, choices=['yes', 'no'], default=Defaults["Options_default"]["r"])
parser.add_argument('-s', help='scratch space to use (<Absolute or relative path> / {})'.format(" / ".join(map(lambda x: "\"%s\""%str(x), Defaults["Scratch_maps"].keys()))), type=Check_scr_string, default=Defaults["Options_default"]["s"])
parser.add_argument('-t', help='the amount of wall clock time (format: hh:mm:ss)', type=Check_time_string, default=Defaults["Options_default"]["t"])
parser.add_argument('-V', help='display version information and exit', action='version', version='%(prog)s v{} - By {}'.format(__VERSION__, __AUTHOR__))
parser.add_argument('-v', '--verbose', help="print extra informations and makes you annoyed", action='store_true')
parser.add_argument('-x', help='additional PBS node features required', default=Defaults["Options_default"]["x"])

parser.add_argument('Gau_inputs', nargs="+", type=Check_gau_inp, help='Gaussian INPUT file (*.com or *.gjf)')

args = parser.parse_args()

# ========== Parse args done, start some patch =============

vars(args)["PBS_envs"] = Defaults["PBS_envs"]
vars(args)["Work_dir"] = os.getcwd()
vars(args)["Pre_run_Gaussian"] = Defaults["Pre_run_Gaussian"]
vars(args)["Post_run_Gaussian"] = Defaults["Post_run_Gaussian"]
if args.verbose: 
    pprint.pprint(vars(args))
    print "============= START PROCESSING GAUSSIAN INPUT =================="

# ==========================================================

def batch_Gen(batch, args, Gau_inps):

    for idx, inp in enumerate(Gau_inps):

        if batch == 1 : scr_dir = os.path.join(args.s, "$USER", "$PBS_JOBID")
        else:           scr_dir = os.path.join(args.s, "$USER", "$PBS_JOBID", str(idx%batch))
        
        if args.verbose: print "\tProcessing %s ..."%inp, 

        with open(inp) as f:
            Q = f.read()
            Q = fix_input(Q, "^%nprocs[^=]*=[^=]+$", "%%NProcShared=%d"%args.p)
            Q = fix_input(Q, "^%mem[^=]*=[^=]+$",    "%%mem=%dmb"%args.m)
        
        with open(inp, "w") as f:
            f.write(Q)

        if args.verbose: print "Done"

        f_base = os.path.splitext(inp)[0]

        pre_gau, gau = make_Gau_job_Block(inp, f_base+".log", args.Work_dir, scr_dir)
        Gau_block = pre_gau + "\n" +\
                    args.Pre_run_Gaussian + "\n" + \
                    gau + "\n" + \
                    args.Post_run_Gaussian + "\n"

        #                                                        5: submit!  
        yield ( inp, f_base, idx/batch, idx%batch, Gau_block , (idx+1)%batch == 0)

        
Start_time = time.time()
job_List = []
for f in batch_Gen(args.b, args, args.Gau_inputs):

    if args.b == 1 : batch_file_name = f[1]
    else:            batch_file_name = args.f + str(f[2]) + "_" + str(Start_time)

    job_List.append(f[4])

    if f[5]: 
        submit_pbs_job(batch_file_name, job_List, args)
        job_List = []

if not f[5]:
    submit_pbs_job(batch_file_name, job_List, args)

# TODO: Unittest
