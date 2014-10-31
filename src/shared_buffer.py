import re
import sys
#Setting shared memory
ljust_val = 40
kd = 3
PostgresConfFile = sys.argv[1]
def setting_shared_buffer():
    comments = []
    f = open("os.conf","r")
    f_re = open("recommend.txt","a")
    file = f.read()
    f.close()
    f_re.write("-"*30+"SHARED MEMORY"+"-"*35+"\n\n")
    #f_re.write("shared_memory\n")
    #f_re.write("-"*70+"\n\n")
    f1 = open(PostgresConfFile,"r")
    postgre_conf = f1.read()
    f1.close()
    os_inst = ""
    p = re.findall(r'os\sinstruction\slength\s+:\s+(\w+)',file)
    d = p[0]
    if '64' in d:
        os_inst = "64bit"
    else:
        os_inst = "32bit"
    #got architecture of os

    recommended_ram = ""
    upper_limit = ""
    f_re.write(" "*40+"SHARED BUFFER")
    f_re.write("\n\n")

    k = re.findall("shared_buffers\s+=\s+(\d+)MB",postgre_conf)
    current_allocation = k[0]
    f_re.write(str("shb:Current_Value").ljust(ljust_val)+"=".ljust(kd)+current_allocation + " MB")
    f_re.write("\n")
    p = re.findall(r'Total\sRAM\s+:\s+(\w+)',file)
    actual_ram = p[0]
    if int(actual_ram) < 1048576:
        recommended_ram = int(actual_ram)*0.15
        upper_limit = str(int(actual_ram) * 0.25)
        comments.append("upper limit "+str(int(actual_ram)/1024) + " MB")
        f.write("shb:Recommended_Value".ljust(ljust_val)+"=".ljust(kd) + str(recommended_ram/1024) + " MB")
        f_re.write("\n")
        f_re.write("shb:Upper_Limit".ljust(ljust_val)+"=".ljust(kd) + upper_limit)
        f_re.write("\n")
    elif os_inst == "64bit":
        upper_limit = "8GB"
        recommended_ram = int(actual_ram) * 0.4
        comments.append("shb:Upper limit "+upper_limit)
        f_re.write("shb:Recommended_Value".ljust(ljust_val)+"=".ljust(kd) + str(recommended_ram/1024) + " MB")
        f_re.write("\n")
        f_re.write("shb:Upper_limit".ljust(ljust_val)+"=".ljust(kd) + upper_limit)
        f_re.write("\n")

    elif os_inst == "32bit":
        if actual_ram > 4 * 10248576:
            comments.append("shb:upgrade system to 64 bit")
        comments.append("shb:upper limit is 2 - 2.5GB")
        upper_limit = "2 - 2.5 GB"
        recommended_ram = int(actual_ram)*0.25
        f_re.write("shb:Recommended_Value".ljust(ljust_val)+"=".ljust(kd) + str(recommended_ram/1024) + " MB")
        f_re.write("\n")
        f_re.write("shb:Upper_Limit".ljust(ljust_val)+"=".ljust(kd) + upper_limit)
        f_re.write("\n")
        if recommended_ram > 2*1024*1024:
            recommended_ram = 2 *1024 *1024
            comments.append("shb:Upgrade system to 64 bit")

    k = re.findall("SHMMAX\s+:\s+(\d+)",file)
    kernel_limit = k[0]

    min_value = "128 KB"
    f_re.write("shb:Lower_Limit".ljust(ljust_val)+"=".ljust(kd) + min_value)
    f_re.write("\n")
    if recommended_ram > kernel_limit:
         comments.append("shb:Need to change SHMMAX to "+recommended_ram+"  $sysctl kern.ipc.shmmax="+recommended_ram)
    else:
        comments.append("shb:No need to change SHMMAX value")
    f_re.writelines(""+x+"\n" for x in comments)
    f_re.close()
setting_shared_buffer()
