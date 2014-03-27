#setting checkpoint segment parameters
import re
import sys
#setting path os postgres conf file
#PostgreConf_path = "/etc/postgresql/9.1/main/postgresql.conf"
PostgreConf_path = sys.argv[1]
ljust_val = 40
kd = 3

def get_shared_buffer():
    f = open("recommend.txt","r")
    k = re.findall(r'shb:Recommended_Value\s+=\s+(.*)\s+MB',f.read())
    f.close()
    return float(k[0])

def get_wal_buffer():
    f = open("recommend.txt","r")
    k = re.findall(r'wal_b:Recommended_value\s+=\s+(\d+)',f.read())
    f.close()
    return int(k[0])

def get_current_val_chkSeg():
    f = open(PostgreConf_path,"r")
    k = re.findall(r'[#]checkpoint_segments\s+=\s+(\d+)',f.read())
    f.close()
    return int(k[0])



def get_total_RAM():
    f = open("os.conf","r")
    k = re.findall(r'Total\s+RAM\s+:\s+(\w+)',f.read())
    f.close()
    return int(k[0])


def set_chkSeg():
    shared_buffer = get_shared_buffer()*1024
    wal_buffer = get_wal_buffer()
    total_ram = get_total_RAM()

    ava_ram = (float(total_ram*80)/float(100))

    req_ram_wal_chk = ava_ram - float(shared_buffer)
    no_chk = int(req_ram_wal_chk/1024)/int(wal_buffer)
    default_val = 3
    return default_val,no_chk,req_ram_wal_chk


def set_chk_completion_target(no_chk):
    set_val = 0.5
    if no_chk < 10:
        set_val = 0.5
    elif no_chk>=10 and no_chk <=32:
        set_val = 0.6
    else:
        set_val = 0.9
    return set_val


def set_chk_timeout():
    #increase in value in check_point_segment will reduce I/O load
    #EDIT : find current io load and set accordingly.
    shared_buffer = int(get_shared_buffer())*1024
    total_ram = int(get_total_RAM())
    if shared_buffer > total_ram*0.3:
        return "5 min to 10min"
    elif shared_buffer < total_ram*0.3:
        return "15 min"

def recommendation_checkpoints():
    return "For bulk load  :Set 128 (2GB) to 256 (4GB)\n" \
           "For OLAP load  :Set 10 (160MB) to 64 (1GB)\n"

def recommendation_completion():
    return "Checkpoint_completion_target should be in range 0.6 to 0.9 \n" \
           "Increase in value in check_point_completion_target will reduce I/O load"

def get_current_chkTimeout():
    f = open(PostgreConf_path,"r")
    k = re.findall(r'[#]checkpoint_timeout\s+=\s+(\w+)',f.read())
    f.close()
    return k[0]

def get_chkcompletion():
    f = open(PostgreConf_path,"r")
    k = re.findall(r'[#]checkpoint_completion_target\s+=\s+([.\d]+)',f.read())
    f.close()
    return k[0]


def checkpoint_flow():
    f_re = open("recommend.txt","a")
    f_re.write("\n\n")
    f_re.write("-"*70+"\n")
    f_re.write("##CHECKPOINTS\n")
    f_re.write("-"*70+"\n\n")
    f_re.write(">>checkpoint_segments\n\n")
    default_val,recommended_Chk_Value,ram_req = set_chkSeg()
    f_re.write("chk:default_Value".ljust(ljust_val)+"=".ljust(kd)+str(default_val))
    f_re.write("\n")
    f_re.write("chk:Recommended_value".ljust(ljust_val)+"=".ljust(kd)+str(recommended_Chk_Value))
    f_re.write("\n")
    f_re.write("chk:Memory Req for Checkpoints * WAL_BUFFERS =".ljust(ljust_val)+"=".ljust(kd)+str(ram_req))
    f_re.write("\n")
    f_re.write("#chk:[ "+recommendation_checkpoints() + "  ]")

    f_re.write("\n\n")
    f_re.write(">>checkpoint_timeout\n\n")
    current_Val = get_current_chkTimeout()
    recommended_Value = set_chk_timeout()
    f_re.write("chkTime:Current_value".ljust(ljust_val)+"=".ljust(kd)+current_Val)
    f_re.write("\n")
    f_re.write("chkTime:Recommended_Value".ljust(ljust_val)+"=".ljust(kd)+recommended_Value)
    f_re.write("\n")
    f_re.write("#chkTime: [ "+recommendation_completion()+" ]")
    f_re.write("\n\n")

    recommended_Value = set_chk_completion_target(recommended_Chk_Value)
    f_re.write(">>checkpoint_completion_target\n\n")
    current_Val = get_chkcompletion()
    f_re.write("chk_comp:Current_Value".ljust(ljust_val)+"=".ljust(kd)+current_Val)
    f_re.write("\n")
    f_re.write("chk_comp:Recommended_Value".ljust(ljust_val)+"=".ljust(kd)+str(recommended_Value))
    f_re.write("\n\n")
    f_re.close()

checkpoint_flow()
