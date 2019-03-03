
#!/usr/bin/python

from subprocess import call
from shutil import copyfile
import os
import fileinput
import re
import sys
import datetime

systems=["h0","h1","h3"]
#systems=["h0","h1","h2","h3"]
#systems=["h0","h1","h2","h3","h4","h5","h6","h7","h8"]
ssh_str = "ssh -o StrictHostKeyChecking=no "
project_id = ".abhilasj.PrescriptiveMem"

#date and time of experiment
now = datetime.datetime.now();
#calling directory
cur_dir = os.getcwd()
#results directory
result_dir = cur_dir + '/results/'+ str(now.month) + '_' + str(now.day) +'_' + str(now.hour) + '_' + str(now.minute) 

run_test = True
configure_system = True
num_runs = "1"

############################################################################################################
#hardware counters 
#hwc = " -e task-clock,instructions,cycles,branches,branch-misses,L1-icache-load-misses,L1-dcache-load-misses,L1-dcache-loads,L1-dcache-stores"
hwc = " -e task-clock,instructions,cycles,L1-dcache-loads,L1-dcache-stores,L1-dcache-prefetches,L1-dcache-prefetch-misses"

#l2 flags
l2flags = ""
#l2flags = (#" -e cpu/event=0x51,umask=0x1/"           #l1d.replacement
#           " -e cpu/event=0x24,umask=0xff/"          #l2_rqsts.references 
#           #" -e cpu/event=0x24,umask=0xe7/"          #l2_rqsts.all_demand_references
#           #" -e cpu/event=0x24,umask=0xe2/"          #l2_rqsts.all_rfo (L1-demand and L1-pref)
#           " -e cpu/event=0x24,umask=0x3f/"          #l2_rqsts.miss
#           #" -e cpu/event=0x24,umask=0x27/"          #l2_rqsts.all_demand_miss
#           " -e cpu/event=0x24,umask=0xf8/"          #l2_rqsts.all_pf
#           " -e cpu/event=0x24,umask=0x50/"          #l2_rqsts.l2_pf_hit 
#           " -e cpu/event=0x24,umask=0x30/")         #l2_rqsts.l2_pf_miss 

#llc flags
#llcflags = " -e  cache-references,cache-misses,LLC-loads,LLC-stores,LLC-load-misses,LLC-store-misses"
llcflags = " -e  cache-references,cache-misses"

#prefetcher flags
prefflags = ()

#offcore 
#dramflags = (" -e mem-loads,mem-stores"
#             " -e cpu/event=0x2e,umask=0x41/"      #longest_lat_cache.miss
#             " -e cpu/event=0x2e,umask=0x4f/")     #longest_lat_cache.reference
##############################################################################################################

mcvi_dir = "/users/abhilasj/mcvi/problems/"

examples = {}
examples = ["corridor",
            "corridorDiscrete",
            "corridorPorta",
            "pacmanHerding",
            "underwater",]

#delays = {}
##delays = ["2000", "5000", "10000", "15000"]
#delays = ["2000"]

#fuction to check utilization
def check_utilization ( system ):
    call(ssh_str + system + project_id + " 'top -b -n2 | grep \"Cpu(s)\" | tail -n 1 ' > temp.txt",shell=True)
    f = open("temp.txt")
    usage = f.read()
    match = re.search("Cpu\(s\):\s*(\d+\.\d+)",usage)
    usage1 = float(match.group(1))
    print(system + ": " + "CPU USAGE: " + str(usage1))
    f.close()
    call(ssh_str + system + project_id + " 'top -b -n2 | grep \"Cpu(s)\" | tail -n 1 ' > temp.txt",shell=True)
    f = open("temp.txt")
    usage = f.read()
    match = re.search("Cpu\(s\):\s*(\d+\.\d+)",usage)
    usage2 = float(match.group(1))
    print(system + ": " + "CPU USAGE: " + str(usage2))
    f.close()
    util = max(usage1,usage2);
    return util;

for system in systems:
    print(ssh_str + system + project_id + ' \'sudo sh -c "echo 0 >/proc/sys/kernel/nmi_watchdog"\'')
    call(ssh_str + system + project_id + ' \'sudo sh -c "echo 0 >/proc/sys/kernel/nmi_watchdog"\'',shell=True)
    print(ssh_str + system + project_id +' \'sudo sh -c "echo 1 >/proc/sys/kernel/perf_event_paranoid"\'')
    call(ssh_str + system + project_id +' \'sudo sh -c "echo 1 >/proc/sys/kernel/perf_event_paranoid"\'',shell=True)
    print(ssh_str + system + project_id + ' \'source ~/scripts/set_env.sh\'')
    if configure_system:
        call(ssh_str + system + project_id + ' \'source ~/scripts/set_env.sh\'',shell=True)

#enter the results directory
if not os.path.isdir(result_dir): 
    os.mkdir(result_dir)
os.chdir(result_dir)

system_no = 0
for example in examples:
    #for delay in delays:
    file_name = result_dir + '/' + example
    #file_name = result_dir + '/' + config.split('-')[0] + #'_' + planner + '_' + direction + '_' + delay
    test = 0
    while not test:
        for system in systems:
            usage = check_utilization(system)
            if usage < 70:
                test = 1
                print(ssh_str + system + project_id + ' \'' + ' perf stat -r ' + num_runs + ' -o ' + file_name + hwc + l2flags + llcflags + ' ' + mcvi_dir + example + '/Solver -o ' + mcvi_dir + example + '/policy' + ' &> ' + example + '.log &\'')
                if run_test:
                    call(ssh_str + system + project_id + ' \'' + ' perf stat -r ' + num_runs + ' -o ' + file_name +  hwc + l2flags + llcflags + ' ' + mcvi_dir + example + '/Solver -o ' + mcvi_dir + example +'/policy' + ' &> ' + example + '.log &\'',shell=True)
                break


print("All tests launched...")
# monitor cpu usage
#for system in systems:
#    usage = 100.0
#    while usage > 20:
#        usage = check_utilization(system)
#
#for system in systems:
#    print(ssh_str + system + project_id + ' \'sudo sh -c "echo 1 >/proc/sys/kernel/nmi_watchdog"\'')
#    call(ssh_str + system + project_id + ' \'sudo sh -c "echo 1 >/proc/sys/kernel/nmi_watchdog"\'',shell=True)
#
#print("Begin Parsing...")
##parsing
#time = [] 
#data = []
#x = 0
#
#file_name = "test"
##file_name = config.split('-')[0] + '_' + planner + '_' + direction + '_' + delay
#f1 = open(file_name, 'r')
#f2 = open(file_name + '.csv', 'w+')
##f2.write('time, task-clock,instrunctions,cycles,L1-dcache-loads,L1-dcache-stores,L2-refrences,l2-misses,l2-prefetch,l2-pf-hit,l2-pf-miss, LLC-ref, LLC-miss\n')
#f2.write('time, task-clock,instructions,cycles,L1-dcache-loads,L1-dcache-stores,L1-dcache-prefetches, L1-dcache-perfetch-misses, LLC-ref, LLC-miss\n')
##time.clear()
##data.clear()
#del time[:]
#del data[:]
#x = 0
#for line in f1:
#    if "started" in line:
#        pass
#    else :
#        if not line.strip():
#            pass
#        else:
#            contents = (line.strip()).split(",");
#            time.append(contents[0])
#            data.append(contents[1])
#            x = x + 1
#for y in range(0,x,9):
#    f2.write(time[y])
#    f2.write(',')
#    f2.write(','.join(data[y:y+9]))
#    f2.write('\n')
#f1.close()
#f2.close()
#print("All Done...")
