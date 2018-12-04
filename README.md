# qg09-py
A python re-implement of qg09, without linda support

It can modify gaussian input files to assigned proccessor number and memory and run multiple gaussian job in batch

**Note**: you can ***easily*** modify this script to fit gaussian 16 (just use `g16` to replace `g09`) 

## Installation

Download or `git clone` this repo, then `/usr/bin/env python2.7 -m pip install -r requirements.txt [--user]` 

_(if you dont have permission to install packages in global, use_ `--user` _instead)_

Add execute permission to q.py, __NOW YOU CAN__ `/path/to/q.py [options] Gaussian_inputs` 

#### Some tips

I\'d like to use `alias qg09='/<path_to_q.py>/q.py -r yes '` to set command and override options


## What you can set in config file and CLI

Type `q.py -h` and get helps

    -h, --help     show this help message and exit
    -b B           the number of files in each batch job 
    -e {yes,no}    email notification when ended? 
    -f F           the preFix of multi jobs pbs file name 
    -l L           addition to PBS resource list 
    -m M           memory used per node <Amomut><Unit> 
    -n N           the number of nodes used  <- I think you should keep it in 1
    -p P           the number of processors used per node 
    -q Q           the queue to submit the job 
    -r {yes,no}    submit the job? 
    -s S           scratch space to use 
    -t T           the amount of wall clock time (format: hh:mm:ss) 
    -V             display version information and exit
    -v, --verbose  print extra informations and makes you annoyed 
    -x X           additional PBS node features required 

## What you can set in config file
    Scratch_maps        <= you can set the alias of scratch directory
    PBS_envs            <= what you need to run before Gaussian start (env setting)
    Pre_run_Gaussian    <= do before each gaussian job start
    Post_run_Gaussian   <= do after  each gaussian job ended

## Params overriding order

Note: you might need to ***CHECK*** the params and generated files after you changed the configs 

     LOW priority
         |    Pre_defined_config_in_executable
         |    <executable dir>/qg09.jsonc 
         |    $HOME/.qg09.jsonc
        \|/   $PWD/qg09.jsonc
         V    Command-line params
    HIGH priority

Sample: [qg09.jsonc](./qg09.jsonc), JSONC Spec: [JSON w/ Comments](https://commentjson.readthedocs.io/en/latest/)

## Major difference compare with original qg09

 - Use_linda is **deprecated**. Multi-processor superserver is much cheaper & more powerful
 - When processing multi inputs, if batch size equals 1, it will use \<input_file_name\>.pbs but **not** a generated pbs name
 - Batch check the existance of Gaussian input files
 - Ability to add custom shell commands in *.pbs file, e.g. 
    - you can add `%Chk=` line to `$QG09_GAU_INP_FILE` by shell in **Pre_run_Gaussian**
    - then add `formchk xxx.chk` in **Post_run_Gaussian** to get `*.fchk` 
    - Available env: `GAUSS_SCRDIR` `QG09_GAU_INP_FILE` `QG09_GAU_LOG_FILE`
    - (You can add whatever you want by editing the executable)
    - **DONT FORGET CHECKING YOUR SETTING BEFORE SUBMIT IT**

Original version: [qg09 from MSU](https://github.com/msi-appdev/qg09)

_if you DO have interest in the example above, I can show you the code. But remember, careful editing and keep testing_

```bash
# write them into Pre_Gaussian_run, line feed should be replaced by \n and double quotes should be escaped

    es_gau_chk=$( echo "%chk=${QG09_GAU_INP_FILE%.*}.chk" | sed "s/\//\\\\\//g" ) 
    if grep -io '%chk' $QG09_GAU_INP_FILE >/dev/null ; then 
        sed -i 's/^%chk=.*/'"$es_gau_chk"'/ig' $QG09_GAU_INP_FILE ; 
    else
        sed -i '1s/^/'"$es_gau_chk\n"'/' $QG09_GAU_INP_FILE; fi 


# What you should do in Post_run_Gaussian

    formchk ${QG09_GAU_INP_FILE%.*}.chk
```

Finally, the config in `qg09.jsonc` (I do some linting, actually)

```json
{
    "Pre_run_Gaussian": "es_gau_chk=$( echo \"%chk=${QG09_GAU_INP_FILE%.*}.chk\" | sed \"s/\\//\\\\\\\\\\//g\" ) \nif grep -io '%chk' $QG09_GAU_INP_FILE >/dev/null ; then \n    sed -i 's/^%chk=.*/'\"$es_gau_chk\"'/ig' $QG09_GAU_INP_FILE ; \nelse \n    sed -i '1s/^/'\"$es_gau_chk\\n\"'/' $QG09_GAU_INP_FILE; fi \n\n\n#>>> GO Gaussian GO <<<",
    "Post_run_Gaussian": "formchk ${QG09_GAU_INP_FILE%.*}.chk"
}
```

_Note:_ `\\\\\\\\\\/` _means the escape of_ `\\\\\/` _(Python string processing) and_ `\\\\\/` _is the escape of_ `\\/` _(what sed get), so we have_ `$es_gau_chk` _equals_ `%chk=.\/t-p0\/oxonium54.chk` _Then following_ `sed` _will drop the remaining backslash out and we got the correct line to insert into gaussian input file._

thus a part of generated `*.pbs` file would be like:

```bash

cd <whatever directory>
mkdir -p /tmp/$USER/$PBS_JOBID
export GAUSS_SCRDIR="/tmp/$USER/$PBS_JOBID"
export QG09_GAU_INP_FILE="oxonium53.com"
export QG09_GAU_LOG_FILE="oxonium53.log"

es_gau_chk=$( echo "%chk=${QG09_GAU_INP_FILE%.*}.chk" | sed "s/\//\\\\\//g" ) 
if grep -io '%chk' $QG09_GAU_INP_FILE >/dev/null ; then 
    sed -i 's/^%chk=.*/'"$es_gau_chk"'/ig' $QG09_GAU_INP_FILE ; 
else 
    sed -i '1s/^/'"$es_gau_chk\n"'/' $QG09_GAU_INP_FILE; fi

#>>> GO Gaussian GO <<<
/usr/bin/time g09 < $QG09_GAU_INP_FILE >& $QG09_GAU_LOG_FILE
if ls "/tmp/$USER/$PBS_JOBID/*.rwf" 2>&1; then rm "/tmp/$USER/$PBS_JOBID/*.rwf"; fi 

formchk ${QG09_GAU_INP_FILE%.*}.chk

```

