import re
import sys
#setting path os postgres conf file
#PostgreConf_path = "/etc/postgresql/9.1/main/postgresql.conf"
PostgreConf_path = sys.argv[1]

ljust_val = 40
kd = 3

def get_FSYNC():
    f = open(PostgreConf_path,'r')
    file = f.read()
    f.close()
    k = re.findall(r'[#]fsync\s+=\s+(\w+)\s+',file)
    print "#getting default value for FSYNC"
    return k[0]


def get_wal_buffer():
    f = open(PostgreConf_path,"r")
    k = re.findall(r'[#]wal_buffers\s=\s([-]*\d+)\s+#\s+min\s+(\w+)',f.read())
    print "#getting defalut value for wal_buffers"
    return k[0][0],k[0][1]

def get_synchronousCommit():
    f = open(PostgreConf_path,'r')
    file = f.read()
    f.close()
    k = re.findall(r'[#]synchronous_commit\s+=\s+(\w+)\s+',file)
    print "#getting default value for synchronousCommit"
    return k[0]

def get_wal_syncMethod():
    f = open(PostgreConf_path,'r')
    file = f.read()
    f.close()
    k = re.findall(r'[#]wal_sync_method\s+=\s+(\w+)\s+',file)
    print "#getting defalut value for wal_sync_Method"
    return k[0]

def get_full_pageWrite():
    f = open(PostgreConf_path,'r')
    k = re.findall(r'[#]full_page_writes\s+=\s+(\w+)',f.read())
    f.close()
    print "#getting default value for full_pageWrites"
    return k[0]

def get_total_ram():
    f = open("os.conf","r")
    k = re.findall(r'Total\s+RAM\s+:\s+(\w+)',f.read())
    f.close()
    print "#getting total RAM"
    return int(k[0])


def get_filesystem_recommendations():
    return "EXT2 use for DB Disks with WAL_SYNC_METHOD = OPENSYNC\n" \
           "-----------------------------------------------------\n" \
           "[EXT3,EXT4,ZFS] or File systems supports journaling For WAL,OS disks with data = 'writeback'\n" \
           "    and WAL_SYNC_METHOD = 'FSYNC'\n" \
           "-------------------------------------------------------"

def set_wal_buffer():
    total_ram = int(get_total_ram())
    set_val = "-1(64 KB)"
    if 0.03*total_ram >=16*1024:
        set_val = "16 MB"
    elif 0.03*total_ram <= 64:
        set_val = "64 KB"
    else:
        set_val = str(0.03*total_ram) + "MB"
    return set_val

def walFlow():
    #fsync = get_FSYNC()
    #print "fsync should be always on\n"
    #synchronousCommit = get_synchronousCommit()
    #print "Recommended value fo synchronousCommit is On \n"

    #first set fync   current value , recommended value ,  comment on why
    f_re = open("recommend.txt","a")
    f_re.write("\n\n")
    f_re.write("-"*70+"\n")
    f_re.write("##WRITE AHEAD LOG\n")
    f_re.write("-"*70+"\n\n")
    f_re.write(">>fsync")
    f_re.write("\n\n")
    current_val = get_FSYNC()
    f_re.write("fync:Current_Value".ljust(ljust_val)+"=".ljust(kd)+current_val.upper())
    f_re.write("\n")
    f_re.write("fync:Recommended_Value".ljust(ljust_val)+"=".ljust(kd)+"ON")

    f_re.write("\n\n")
    f_re.write(">>synchronous_commit")
    f_re.write("\n\n")
    current_val = get_synchronousCommit()
    f_re.write("sy_c:Current_Value".ljust(ljust_val)+"=".ljust(kd)+current_val.upper())
    f_re.write("\n")
    f_re.write("sy_c:Recommended_Value".ljust(ljust_val)+"=".ljust(kd)+"ON")
    f_re.write("\n")
    f_re.write("#sy_c:Value depends directly on 'fsync'")

    f_re.write("\n\n")
    f_re.write(">>wal_buffers")
    current_val,min_value = get_wal_buffer()
    recommended_value = set_wal_buffer()
    f_re.write("\n\n")
    f_re.write("wal_b:Current_value".ljust(ljust_val)+"=".ljust(kd)+current_val)
    f_re.write("\n")
    f_re.write("wal_b:Recommended_value".ljust(ljust_val)+"=".ljust(kd)+recommended_value)
    f_re.write("\n")
    f_re.write("wal_b:Minimum_value".ljust(ljust_val)+"=".ljust(kd)+min_value)
    f_re.write("\n")
    f_re.write("#wal_b:For heavy load value should be in between 1MB - 16 MB")

    f_re.write("\n\n")
    f_re.write(">>full_page_writes")
    current_val = get_full_pageWrite()
    f_re.write("\n\n")
    f_re.write("full_pgw:Current_value".ljust(ljust_val)+"=".ljust(kd)+current_val.upper())
    f_re.write("\n")
    f_re.write("full_pgw:Recommended_value".ljust(ljust_val)+"=".ljust(kd)+"ON")
    f_re.write("\n")
    f_re.write("#full_pgw:Recovers from partial page writes and Improve IO performance")
    f_re.close()



walFlow()
