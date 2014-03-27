
__author__ = 'Rushikesh'
import subprocess
import re
import os
def find_os_info():
#showing operating system information
    d1 = {}
    p = subprocess.Popen("uname",stdout=subprocess.PIPE,shell=True)
    d1["operating system name"] = p.stdout.read()
    p = subprocess.Popen("uname -m",stdout=subprocess.PIPE,shell=True)
    d1["os instruction length"] = p.stdout.read()
    p = subprocess.Popen("uname -r",stdout=subprocess.PIPE,shell=True)
    d1["kernel release"] = p.stdout.read()
    p = subprocess.Popen("uname -p",stdout=subprocess.PIPE,shell=True)
    d1["Processor type"] = p.stdout.read()
    return d1


def find_mem(info):
    d1 = {}

    k = re.findall(r'MemTotal:\s+(\d+)',info)
    d1["Total RAM"] = k[0]
    s1 = int(k[0])

    k = re.findall(r'SwapTotal:\s+(\d+)',info)
    d1["Total SWAP"] = k[0]
    s2 = int(k[0])

    d1["Total RAM+SWAP"] = s1 + s2

    k = re.findall(r'MemFree:\s+(\d+)',info)
    d1["Free RAM"] = k[0]

    k = re.findall(r'SwapFree:\s+(\d+)',info)
    d1["Free SWAP"] = k[0]
    d1["Total RAM+SWAP"] = int(d1["Free SWAP"]) + int(d1["Free RAM"])

    k = re.findall(r'Buffers:\s+(\d+)',info)
    d1["Buffers"] = k[0]

    k = re.findall(r'Cached:\s+(\d+)',info)
    d1["Cached Mem"] = k[0]
    d1["Total OS Cached"] =   int(d1["Free SWAP"]) + int(d1["Buffers"]) +  int(d1["Cached Mem"])
    return d1

def find_kernel_info(info):
    d = {'SHMMAX' : 'max total shared memory (kbytes)',
         'SHMMIN' : 'min seg size (bytes)',
         'SHMALL' : 'max total shared memory (kbytes)',
         'SHMSEG' : 'max number of segments',
         'SEMMNS' : 'max semaphores system wide',
         'SEMMNI' : 'max number of arrays',
         'SEMMSL' : 'max semaphores per array ',
         'SEMVMX' : 'semaphore max value'}
    d3 = {}

    for l in d:
        str1 = d[l].replace(' ','\s+').replace('(','\(').replace(')','\)') + '\s+=\s+(\d+)'
        try:
            k = re.findall(str1,info)
            if k:
                d3[l] = k[0]
        except:
            pass
    return d3

def find_cpu_info(info):
    d4 = {}
    p = subprocess.Popen("nproc",stdout=subprocess.PIPE,shell=True)
    d4['number of cpu'] = p.stdout.read().replace("\n","").lstrip('')
    p = subprocess.Popen("lscpu | grep \'MHz\'",stdout=subprocess.PIPE,shell=True)
    l = []
    for k in p.stdout.readlines():
        d4['cpu speed'] = k.split(':')[1].replace("\n","").lstrip(' ')
        l.append(float(k.split(':')[1].replace("\n","").lstrip(' ')))
    d4['cpu avg'] = sum(l)/len(l)

    return d4

def find_raid_conf(info):
    d5 = {}
    str1 = info.split('\n')[0]
    str2 = info.split('\n')
    del str2[0]
    str3 = ""
    for k in str2:
        str3 = str3 + k + "\n"
    p = re.findall(r'\[(\w+)\]',str1)
    d5['RAID levels supported by kernel'] = p
    p = re.findall(r'(\w+)\s:(.*)',str3)
    cnt = len(p)
    for l in range(cnt):
        d5['Device' + str(l) + ' ' + p[l][0]] = p[l][1]
    d5['SW RAID numbers of disks'] = cnt

    return d5


def find_disk_fs(info):
    d6 = {}
    m = re.findall(r'Disk\s+(/.*):\s(\d+)',info)
    for l in range(len(m)):
        d6[m[l][0]] = str(m[l][1].strip(" ") + 'MB').ljust(10)+':'.ljust(3) + "Disk".ljust(17) +':'.ljust(3)+'NONE'

    layout = []
    index = 0
    in_pt = False
    re_pt = re.compile(r"\s*Device\s+Boot\s+Start\s+End")
    p = subprocess.Popen("(export LANG=C; /usr/bin/sudo /sbin/fdisk -l)", stdout=subprocess.PIPE, shell=True)
    f = p.stdout.read().split(os.linesep)

    for l in f:
        if re_pt.match(l):
            in_pt = True
            layout.append(l + os.linesep)
        elif in_pt:
            if l == "":
                index = index + 1
                in_pt = False
            else:
                layout[index] = layout[index] + l + os.linesep
                if '*' in l:
                    m = re.split(r'\s+',l)
                    d6[m[0]] = m[3].ljust(10) + ':'.ljust(3) + m[6].ljust(17) + ':'.ljust(3) + "Installation Part"
                else:
                    m = re.split(r'\s+',l)
                    d6[m[0]] = m[3].ljust(10) + ':'.ljust(3) + m[5].ljust(17) + ':'.ljust(3) + 'NONE'
    return d6

def find_file_system():
    fstype = {}
    p = subprocess.Popen("(export LANG=C; /bin/df -T -x tmpfs)", stdout=subprocess.PIPE, shell=True)
    f = p.stdout.read().split(os.linesep)
    f.pop(0)
    for l in f:
        s = l.split()
        if len(s) > 1:
            fstype[s[0]] = s[1]
    return fstype


def find_read_speed():
    p = subprocess.Popen("sudo fdisk -l",stdout=subprocess.PIPE,shell=True)
    m = re.findall(r'Disk\s+(/.*):\s\d+',p.stdout.read())

    speed = {}
    for disk_name in m:
        proc = subprocess.Popen(['sudo','hdparm','-tT',disk_name],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        proc.stdin.close()
        pr = proc.stdout.read()
        proc.wait()
        a = re.findall("Timing\scached\sreads:.*=\s+(.*)", pr)
        b = re.findall("Timing\sbuffered\sdisk\sreads:.*=\s+(.*)", pr)
        speed[disk_name] = str(a) + '    ' + str(b)
    return speed

def find_write_speed():
    str1 = "sync ;sudo dd if=/dev/sda of=testfile bs=100k count=1k  && sync"
    import time
    start = time.time()
    p = subprocess.Popen(str1,shell=True,stdout=subprocess.PIPE)

    t1 = time.time() - start
    p = subprocess.Popen("rm testfile",shell=True)



d1 = find_os_info()
p = subprocess.Popen("cat /proc/meminfo",stdout=subprocess.PIPE,shell=True)
d2 = find_mem(p.stdout.read())
#kernel limits
p = subprocess.Popen("/usr/bin/ipcs -msl",stdout=subprocess.PIPE,shell=True)
d3 = find_kernel_info(p.stdout.read())
#cpu info
p = subprocess.Popen("cat /proc/cpuinfo",stdout=subprocess.PIPE,shell=True)
d4 = find_cpu_info(p.stdout.read())
#raid info
p = subprocess.Popen("cat /proc/mdstat",stdout=subprocess.PIPE,shell=True)
d5 = find_raid_conf(p.stdout.read())
#disk info
disks = []
p = subprocess.Popen("sudo fdisk -l",stdout=subprocess.PIPE,shell=True)
d6 = find_disk_fs(p.stdout.read())

#File system information
d7 = find_file_system()
#find speed info
d8 = find_read_speed()
#find write speed
#d9 = find_write_speed()


f = open("os.conf","w")
f.write("-"*70+"\n")
f.write(""*30+"OS Configurations"+"\n")
f.write("-"*70+"\n\n")

#ram info
for k in d1:
    str1 = "%s  :  %s\n"%(str(k).ljust(30),str(d1[k]))
    f.write(str1)
f.write("-"*70+"\n")
f.write("Memory Info            All values in KB"+"\n")
f.write("-"*70+"\n\n")
for k in d2:
    str1 = "%s  :  %s\n"%(str(k).ljust(30),str(d2[k]))
    f.write(str1)

f.write("-"*70+"\n")
f.write("kernel resources"+"\n")
f.write("-"*70+"\n\n")
for k in d3:
    str1 = "%s  :  %s\n"%(str(k).ljust(30),str(d3[k]))
    f.write(str1)

f.write("-"*70+"\n")
f.write("CPU info"+"\n")
f.write("-"*70+"\n\n")
for k in d4:
    str1 = "%s  :  %s\n"%(str(k).ljust(30),str(d4[k]))
    f.write(str1)

f.write("-"*70+"\n")
f.write("RAID info"+"\n")
f.write("-"*70+"\n\n")
for k in d5:
    str1 = "%s  :  %s\n"%(str(k).ljust(30),str(d5[k]))
    f.write(str1)

f.write("-"*70+"\n")
f.write("Disks and partitions"+"\n")
f.write("-"*70+"\n\n")
for k in d6:
    str1 = "%s  :  %s\n"%(str(k).ljust(16),str(d6[k]))
    f.write(str1)

f.write("-"*70+"\n")
f.write("File System information"+"\n")
f.write("-"*70+"\n\n")
for k in d7:
    str1 = "%s  :  %s\n"%(str(k).ljust(30),str(d7[k]))
    f.write(str1)

f.write("-"*70+"\n")
f.write("Disk Read speed"+"\n")
f.write("-"*70+"\n\n")
str1 = "%s  :  %s   %s\n"%(str("").ljust(30),str("cached reads").ljust(20),str("disk reads"))
f.write(str1)
for k in d8:
    str1 = "%s  :  %s\n"%(str(k).ljust(30),str(d8[k]))
    f.write(str1)

f.close()


def tune_scheduler():
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

    for disk in disk_list:
        disk_name = disk.split("/")[2]
        str1 = "cat /sys/block/%s/queue/scheduler"%disk_name
        p = subprocess.Popen(str1,stdout=subprocess.PIPE,shell=True)

        d[disk] = p.stdout.read().strip("\n").rstrip(" ")
    return d


d = tune_scheduler()

f = open("os.conf","a")
f.write("\n")
f.write("-"*70+"\n")
f.write("Scheduler information"+"\n")
f.write("-"*70+"\n\n")
for k in d:
    str1 = "%s  :  %s\n"%(str(k).ljust(30),str(d[k]))
    f.write(str1)
f.close()

