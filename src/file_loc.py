import subprocess
import re
import operator
import sys
ljust_val = 40
kd = 3
PostgresPath = sys.argv[1]
def get_disk_list():
    d = {}
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
            if "Disk" in line:
                disk_list.append(line.split(' ')[0])
    return disk_list

def get_os_disk():
    f = open("os.conf","r")
    file = f.read()
    f.close()
    k = re.findall(r'(.*):\s+\d+\s+:\s+\w+\s+:\s+Installation\s+Part',file)
    return k[0].strip(" ")

def find_free_space():
    p = subprocess.Popen("(export LANG=C; /bin/df -T -m)",stdout=subprocess.PIPE,shell=True)
    text = p.stdout.readlines()
    del text[0]
    text[0]=text[0]+" "+text[1]
    disk_free = {}
    for line in text:
        lm = re.split('\s+',line)
        disk_free[lm[0]] = lm[4]
    return disk_free

def get_checkpoint_seg():
    f = open("recommend.txt","r")
    k = re.findall(r'chk:Recommended_value\s+=\s+(\d+)',f.read())
    f.close()
    return int(k[0])


def get_wal_buffer_size():
    f = open("recommend.txt","r")
    k = re.findall(r'wal_b:Recommended_value\s+=\s+(\w+)',f.read())
    f.close()
    val = k[0]
    if "MB" in val:
        int_val = re.findall(r'\d+',val)
        int_value = int(int_val[0]) * 1024
        return int_value
    else:
        int_val = re.findall(r'\d+',val)
        return int_val[0]

def calculate_pgxlog_Space():
    check_point_seg = get_checkpoint_seg()
    wal_buffer = get_wal_buffer_size()

    return ((int(check_point_seg)*3 + 1 )*int(wal_buffer))/1024


def do_cal():
    f_re = open("recommend.txt","a")
    disks = get_disk_list()
    os_part = get_os_disk()
    free_disk_part = find_free_space()
    cp_disks = []
    os_disk = ""
    for k in disks:
        if k not in os_part:
            cp_disks.append(k)
        else:
            os_disk = k
    free_disk = {}
    for k in disks:
        free_disk[k] = 0
    for k in disks:
        for p in free_disk_part.keys():
            if k in p:
                free_disk[k] = free_disk[k] + int(free_disk_part[p])
    f_re.write("-"*31)
    f_re.write("DISK RECOMMENDATION")
    f_re.write("-"*30)
    f_re.write("\n\n")
    f_re.write("OS installation disk partition".ljust(ljust_val)+"=".ljust(kd)+os_disk)
    f_re.write("\n")
    f_re.write("Remaining disks".ljust(ljust_val)+"=".ljust(kd)+str(cp_disks))
    f_re.write("\n")

    pgxlog_space = calculate_pgxlog_Space()
    f_re.write("PGXLOG space".ljust(ljust_val)+"=".ljust(kd)+str(pgxlog_space)+" MB")
    f_re.write("\n")

    #Algorithm starts here :
    sorted_free_disk = sorted(free_disk.iteritems(),key=operator.itemgetter(1))
    xlog_disk = ""
    sorted_free_disk.pop()
    if len(cp_disks) >= 2:
        flag = 0
        for x in sorted_free_disk:
            if pgxlog_space >= x[1]:
                flag = 1
                xlog_disk = x[0]
                break
        if flag == 0:
            if free_disk[os_disk] >= pgxlog_space:
                f_re.write("Put WAL ON".ljust(ljust_val)+"=".ljust(kd)+os_disk)
                f_re.write("\n")

            else:
                f_re.write("Recommendation to add extra disk with size more than " + str(int(pgxlog_space)+100))
                f_re.write("\n")

        else:
            f_re.write("Put WAL to".ljust(ljust_val)+"=".ljust(kd)+xlog_disk)
            f_re.write("\n")

            cp_disks.remove(xlog_disk)
            free_disk.pop(xlog_disk)
            sorted_free_disk = sorted(free_disk.iteritems(),key=operator.itemgetter(1))

        if len(cp_disks)%2 == 0:
            #even disks
            f_re.write("Put TEMP  on".ljust(ljust_val)+"=".ljust(kd)+str(sorted_free_disk[0][0]))
            f_re.write("\n")

            sorted_free_disk.pop()
            ls = []
            for x in sorted_free_disk:
                ls.append(x[0])
            f_re.write("Put DB on".ljust(ljust_val)+"=".ljust(kd)+str(ls))
            f_re.write("\n")

        else:
            #odd
            if len(free_disk) == 1:
                f_re.write("Put TEMP on".ljust(ljust_val)+"=".ljust(kd)+str(os_disk))
                f_re.write("\n")
                f_re.write("Put DB on".ljust(ljust_val)+"=".ljust(kd)+str(free_disk))
                f_re.write("\n")

            else:
            #even
                f_re.write("Put TEMP on".ljust(ljust_val)+"=".ljust(kd)+str(sorted_free_disk[0][0]))
                f_re.write("\n")
                f_re.write("Put DB on".ljust(ljust_val)+"=".ljust(kd)+str(sorted_free_disk[1][0]))
                f_re.write("\n")

    elif len(cp_disks) < 2:
        if len(cp_disks) == 1:
            if free_disk[os_disk] >= free_disk[cp_disks[0]] and pgxlog_space <= free_disk[os_disk]:
                f_re.write("OS + TEMP + WAL ON DISK".ljust(ljust_val)+"=".ljust(kd)+os_disk)
                f_re.write("\n")
                f_re.write("DB ON".ljust(ljust_val)+"=".ljust(kd)+cp_disks[0])
                f_re.write("\n")

            else:
                f_re.write("OS + WAL ON DISK".ljust(ljust_val)+"=".ljust(kd)+os_disk)
                f_re.write("\n")
                f_re.write("DB + TEMP ON".ljust(ljust_val)+"=".ljust(kd)+cp_disks[0])
                f_re.write("\n")

        elif len(cp_disks) == 0:
            if pgxlog_space >= free_disk[os_disk]:
                f_re.write("Recommendation to add extra disk of size greater than  %s"%pgxlog_space)
                f_re.write("\n")
                f_re.write("OS + WAL + TEMP + DB ON DISK".ljust(ljust_val)+"=".ljust(kd)+os_disk)
                f_re.write("\n")

            else:
                f_re.write("OS + WAL + TEMP + DB ON DISK".ljust(ljust_val)+"=".ljust(kd)+os_disk)
                f_re.write("\n")

    f_re.write("\n")
    f_re.write("-"*32)
    f_re.write("RAID RECOMMENDATIONS")
    f_re.write("-"*32)
    f_re.write("\n\n")
    f_re.write(get_raid_recommendations())
    f_re.write("\n\n")
    f_re.close()

def get_raid_recommendations():
    return "Function            Cache Flushes        Access Patterns        RAID LEVELS\n\n" \
           "Operating System    Rare                 mix of seq and random       1     \n" \
           "Database            Regularly            mix of seq and random       10    \n" \
           "WAL                 Constant             Sequential                  1     \n" \
           "Temp Files          Never                More random as clients inc   None  "


do_cal()
