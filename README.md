# qg09-py
A python re-implement of qg09, without linda support

**Note**: you can ***easily*** modify this script to fit gaussian 16 (just use `g16` to replace `g09`) 

## Some tips

I \'d like to use `alias qg09='/<path_to_q.py>/q.py -r yes '` to set command and override options

## What you can set in config file and CLI

Type `q.py -h` and get helps

    -b B         the number of files in each batch job 
    -e {yes,no}  email notification when ended? 
    -l L         addition to PBS resource list 
    -m M         memory used per node <Amomut><Unit> 
    -n N         the number of nodes used  <- I think you should keep it in 1
    -p P         the number of processors used per node 
    -q Q         the queue to submit the job 
    -r {yes,no}  submit the job? 
    -s S         scratch space to use 
    -t T         the amount of wall clock time (format: hh:mm:ss) 
    -x X         additional PBS node features required 

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

Sample: [qg09.jsonc](./qg09.jsonc), Type: [JSON w/ Comments](https://commentjson.readthedocs.io/en/latest/)

## Major difference compare with original qg09

 - Use_linda is **deprecated**. Multi-processor superserver is much cheaper & more powerful
 - When processing multi inputs, if batch size equals 1, it will use \<input_file_name\>.pbs but **not** a generated pbs name
 - Ability to add custom shell commands in *.pbs file, e.g. 
    - you can add `%Chk=` line to `$QG09_GAU_INP_FILE` by shell in **Pre_run_Gaussian**
    - then add `formchk xxx.chk` in **Post_run_Gaussian** to get `*.fchk` 
    - Available env: `GAUSS_SCRDIR` `QG09_GAU_INP_FILE` `QG09_GAU_LOG_FILE`
    - (You can add whatever you want by editing the executable)
    - **DONT FORGET CHECKING YOUR SETTING BEFORE SUBMIT IT**

Original version: [qg09 from MSU](https://github.com/msi-appdev/qg09)

