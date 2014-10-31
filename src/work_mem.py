__author__ = 'Rushikesh'
import re
import sys
#setting path os postgres conf file
PostgreConf_path =sys.argv[1]
ljust_val = 40
kd = 3

def get_default_val():
    f = open(PostgreConf_path,"r")
    k = re.findall(r'[#]work_mem\s+=\s+(\w+)\s+#\s*min\s+(\w+)',f.read())
    f.close()
    return k[0][0],k[0][1]

def get_shared_mem():
    f = open("recommend.txt","r")
    file = f.read()
    f.close()
    k = re.findall(r'shb:Recommended_Value\s+=\s+(.*)\s+MB',file)
    return float(k[0])*1024

def setting_work_mem():
    f1 = open(PostgreConf_path,"r")
    file1 = f1.read()
    f1.close()
    k = re.findall(r'[#]work_mem\s+=\s+(\w+)',file1)
    current_val = k[0]
    f2 = open("os.conf","r")
    file2 = f2.read()
    f2.close()
    k = re.findall(r'Total\s+RAM\+SWAP\s+:\s+(\d+)',file2)
    os_cache = int(k[0])

    k = re.findall(r'max_connections\s+=\s+(\d+)',file1)
    max_connections = int(k[0])
    shared_mem = float(get_shared_mem())

    k = re.findall(r'Total\s+RAM\s+:\s+(\d+)',file2)
    total_ram = k[0]
    work_mem = 0
    x = 2
    cnt = 0
    while True:

        work_mem = (os_cache/max_connections)/x

        if (int(shared_mem)+(int(work_mem)*max_connections)) > int(total_ram)*0.9:
            if work_mem > 1024:
                if x <= 16:
                    x = x * 2
                else:
                    work_mem = 64
                    break
            else:
                work_mem = 1024
                break
        else:
            break
        cnt = cnt + 1
        if cnt == 4:
            work_mem = 64
            break
    f = open("recommend.txt","a")
    f.write("\n\n")
    f.write(" "*40+"WORK MEMORY\n")
    f.write("\n\n")
    default_val,min_val = get_default_val()
    f.write("wm:Default_Value".ljust(ljust_val)+"=".ljust(kd)+default_val)
    f.write("\n")
    f.write("wm:Recommended_value".ljust(ljust_val)+"=".ljust(kd)+str(work_mem) + " KB")
    f.write("\n")
    f.write("wm:Lower_Limit".ljust(ljust_val)+"=".ljust(kd)+default_val)
    f.write("\n")
    f.close()

def get_temp_file_Value():
    f = open(PostgreConf_path,"r")
    k = re.findall(r'[#]temp_file_limit\s+=\s+(\w+)',f.read())
    f.close()
    if k:
        return k[0]
    else:
        return ""


def set_temp_file():
    f_re = open("recommend.txt","a")
    f_re.write("\n")
    f_re.write(" "*40+"TEMP FILE LIMIT")
    f_re.write("\n\n")
    current_val = get_temp_file_Value()
    if current_val == "":
        f_re.write("temp:Only Supported by PostgreSQL > 9.2")
        f_re.write("\n")
        f_re.close()
    else:
        f_re.write("temp:Current_Value".ljust(ljust_val)+"=".ljust(kd)+current_val)
        f_re.write("\n")
        f_re.write("temp:Recommended_Value  =  -1")
        f_re.close()
    f_re.close()


setting_work_mem()
set_temp_file()
