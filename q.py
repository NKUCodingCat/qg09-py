__VERSION__ = "0.0.1"

def submit_pbs_job(resources, job_file, jobs):

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


    if args.n > 1: pbs_resources += 'uniq $PBS_NODEFILE | xargs -I {} ssh {} mkdir -p ' + resources['scr'] +  "\n"

    with open(qfile, "w") as submit_fh:
        print >>submit_fh, pbs_header + pbs_resources
        for i in jobs: print >>submit_fh, i

    if args.r == "yes" : 
        print "The calculation {} has been submitted".format(qfile)
        import os; os.system("qsub " + qfile)
    else:
        print "The queue script {} has been created".format(qfile)
        print "To run the calculation type: qsub " + qfile


# ================ MAIN ========================

import argparse, re, humanfriendly

def Check_time_string(string):
    if None == re.match("\d+:\d\d:\d\d", string):
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



parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-e', help='email notification when ended?', type=str, choices=['yes', 'no'], default='no')
parser.add_argument('-r', help='submit the job?', type=str, choices=['yes', 'no'], default='no')
parser.add_argument('-p', help='the number of processors used per node', type=int, default=20)
parser.add_argument('-m', help='memory used per node <Amomut><Unit>', type=Check_mem_string, default='15000mb')
parser.add_argument('-x', help='additional PBS node features required', default='')
parser.add_argument('-q', help='the queue to submit the job', default='batch')
parser.add_argument('-l', help='email notification when job ended?', type=str, choices=['yes', 'no'], default='no')
parser.add_argument('-n', help='the number of nodes used', type=int, default=1)
parser.add_argument('-t', help='the amount of wall clock time (format: hh:mm:ss)', type=Check_time_string, default="168:00:00")

# TODO: -b -s 

parser.add_argument('Gaussian_input', help='Gaussian INPUT file (*.com or *.gjf)')

# TODO: filename/file process

# TODO: default value & fix_input

# TODO: MAKE gaujob

args = parser.parse_args()
print args
submit_pbs_job({"queue":"batch", "scr": "/tmp/$USER/$PBS_JOBID"}, "oxoium", [])