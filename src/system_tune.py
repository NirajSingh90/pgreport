__author__ = 'Rushikesh'
#file system and location flowchart
import subprocess
import re
ljust_val = 40
kd = 3

def set_read_ahead():
    comments = []
    p = subprocess.Popen("sudo blockdev --getra /dev/sda",stdout=subprocess.PIPE,stdin=subprocess.PIPE,shell=True)
    read_ahead_val = p.stdout.read().strip("\n")
    recom_read_val = 4096
    comments.append("For postgres performance improvement set value to 4096 ,for better seeks")
    comments.append("set it using \"$sudo blockdev --getra /dev/sda\"")
    return (read_ahead_val,recom_read_val,comments)


def change_file_access_time():
    comments = []

    f = open("os.conf","r")
    file = f.readlines()
    f.close()
    flag = 0
    disk_list = []
    for line in file:
        if "Disks and partitions" in line:
            flag = 1
        elif flag == 1:
            flag =2
        elif flag == 2 and "----" not in line and line != "\n":
            if "File System information" in line:
                break
            disk_list.append(line.split(' ')[0])
    p = subprocess.Popen("mount",stdout=subprocess.PIPE,shell=True)
    line1 = ""
    mount_disk = []
    main_disk = {}
    for line1 in p.stdout.readlines():
        if line1.split(' ')[0] in disk_list:
            mount_disk.append(line1.replace("\n",""))
            main_disk[line1.split()[0]] = "0"
    for mount_line in mount_disk:
        if "noatime" in mount_line:
            main_disk[mount_line.split(' ')[0]] = 1
        else:
            comments.append("add 'noatime' options under \\etc\\fstab for disk  :"+mount_line.split(' ')[0])
    return (main_disk,comments)

def find_swapineess():
    p = subprocess.Popen("sudo cat /proc/sys/vm/swappiness",stdout=subprocess.PIPE,shell=True)
    d = {}
    d["current_val"] = p.stdout.read()
    d["recommended_Val"] = "0"
    d["comments"] = ["$sysctl vm.swappiness = 0"]
    return d["current_val"],d["recommended_Val"],d["comments"]


def overcommit_behav():
    d = {}
    p = subprocess.Popen("sudo cat /proc/sys/vm/overcommit_memory",stdout=subprocess.PIPE,shell=True)
    d["current_val"] = p.stdout.read().replace("\n","")
    d["recommended_Val"] = "2"
    comments = ["$syssctl vm.overcommit_memory=2"]
    d["comments"] = comments
    return d["current_val"],d["recommended_Val"],d["comments"]

def write_cache_sizing():
    d = {}
    p =subprocess.Popen("sudo cat /proc/sys/vm/dirty_background_ratio",stdout=subprocess.PIPE,shell=True)
    d["current_dirty_background_ratio"] = p.stdout.read()

    p =subprocess.Popen("sudo cat /proc/sys/vm/dirty_ratio",stdout=subprocess.PIPE,shell=True)
    d["current_dirty_ratio"] = p.stdout.read()
    f = open("os.conf","r")
    file = f.read()
    f.close()
    k = re.findall(r'kernel\srelease\s+:\s+(.*)',file)
    version = k[0].split('-')[0]
    k = re.findall(r'Total\sRAM\s+:\s+(.*)',file)
    recomm_dirty_background_ratio = ""
    recomm_dirty_ratio = ""
    comments = []
    if int(version.replace(".","")) < 2622:
         d["recomm_dirty_ratio"] = "10"
         d["recomm_dirty_background_ratio"] = "5"
         comments.append("$sysctl vm.dirty_background_ratio = "+d["recomm_dirty_background_ratio"])
         comments.append("$sysctl vm.dirty_ratio = "+d["recomm_dirty_ratio"])

    elif ((float(k[0])/1024)/1024) > 7.1:
         d["recomm_dirty_ratio"] = "2"
         d["recomm_dirty_background_ratio"] = "1"
         comments.append("$sysctl vm.dirty_background_ratio = "+d["recomm_dirty_background_ratio"])
         comments.append("$sysctl vm.dirty_ratio = "+d["recomm_dirty_ratio"])

    else:
         d["recomm_dirty_ratio"] = d["current_dirty_background_ratio"]
         d["recomm_dirty_background_ratio"] = d["current_dirty_ratio"]
         comments.append("no need to tune")
         comments.append("no need to tune")

    return d,comments

def do_proc():
    f_re = open("recommend.txt","a")
    f_re.write("\n\n")
    #f_re.write("-"*70)
    f_re.write("-"*24+"SYSTEM TUNING RECOMMENDATIONS"+"-"*24+"\n\n")
    #f_re.write("-"*70)
    current_val,recommended_val,comments = set_read_ahead()
    #f_re.write("\n\n")
    f_re.write(" "*40+"READ AHEAD VALUE")
    f_re.write("\n\n")
    f_re.write("Current Value".ljust(ljust_val)+"=".ljust(kd)+current_val)
    f_re.write("\n")
    f_re.write("Recommended Value".ljust(ljust_val)+"=".ljust(kd)+str(recommended_val))
    f_re.write("\n")
    f_re.write("Comments".ljust(ljust_val)+"=".ljust(kd)+"\n")
    for com in comments:
        f_re.write(str(com).center(30)+"\n")
    f_re.write("\n")

    current_val,comments = change_file_access_time()
    f_re.write("\n")
    f_re.write(" "*40+"FILE ACCESS TIME")
    f_re.write("\n")
    f_re.write("Current_Values For Disks\n")
    for k in current_val:
        f_re.write(str(k).ljust(ljust_val)+"=".ljust(kd)+str(current_val[k])+"\n")
    f_re.write("Comments".ljust(ljust_val)+"=".ljust(kd)+str(comments))
    f_re.write("\n\n")

    current_val,recommended_val,comments = overcommit_behav()
    f_re.write(" "*40+"OVERCOMMIT BEHAVIOR\n\n")
    f_re.write("Current Value".ljust(ljust_val)+"=".ljust(kd)+current_val)
    f_re.write("\n")
    f_re.write("Recommended Value".ljust(ljust_val)+"=".ljust(kd)+current_val)
    f_re.write("\n")
    f_re.write("Comments".ljust(ljust_val)+"=".ljust(kd)+str(comments))
    f_re.write("\n\n")

    current_val,recommended_val,comments = find_swapineess()
    f_re.write(" "*40+"SWAPINESS\n\n")
    f_re.write("Current_Value".ljust(ljust_val)+"=".ljust(kd)+current_val)
    f_re.write("Recommended_Value".ljust(ljust_val)+"=".ljust(kd)+recommended_val)
    f_re.write("\n")
    f_re.write("Comments".ljust(ljust_val)+"=".ljust(kd)+str(comments))
    f_re.write("\n\n")

    f_re.write(" "*40+"WRITE CHACHE SIZING\n\n")
    d,comments = write_cache_sizing()
    for k in d:
        f_re.write(k.ljust(ljust_val)+"=".ljust(kd)+d[k])
        f_re.write("\n")
    f_re.write("\n")
    f_re.write("Comments".ljust(ljust_val)+"=".ljust(kd)+str(comments))
    f_re.write("\n")
    f_re.close()

do_proc()
