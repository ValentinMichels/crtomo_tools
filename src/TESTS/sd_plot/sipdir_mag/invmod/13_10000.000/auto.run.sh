#!/bin/bash
# DO NOT EDIT THIS FILE - generated by th_run_all_depth_3.sh
cd /home/mweigand/Uni/Programme/CRLab/sample_data/Inversions/Sipdirs2_rawdata/./sipdir2_dc/invmod/13_10000.000
if [[ ! -e inv/run.ctr || `cat inv/run.ctr | grep CPU -c` -eq 0 ]]; then
  cd exe
  bash -c "/home/mweigand/bin/CRMod"  
  # run pre_crtomo.sh, if present in tomodir
  if [ -e "../pre_crtomo.sh" ]; then 
    cd .. 
    bash "pre_crtomo.sh" 
    cd exe    
  fi 
  bash -c "/home/mweigand/bin/CRTomo" 
  # run post_crtomo.sh, if present in tomodir
  if [ -e "../post_crtomo.sh" ]; then 
    cd .. 
    bash "post_crtomo.sh" 
    cd exe    
  fi 
else
  echo already finished
fi
