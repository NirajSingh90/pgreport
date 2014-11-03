_author__ = 'Rushikesh'
import subprocess
from datetime import datetime
import sys
test_version = "alpha v1.0"
#setting path os postgres conf file
try:
    PostgreConf_path = sys.argv[1]
except:
    PostgreConf_path = "/etc/postgresql/9.1/main/postgresql.conf"

#print "postgresql.conf file location   :"+PostgreConf_path
now_time = datetime.now().time()
now_date = datetime.now().date()

#pg_version =postgre_info.get_postgre_version()
p0 = subprocess.Popen("python src/postgre_info.py",stdout=subprocess.PIPE,shell=True)
pg_version = p0.stdout.read()

#print "postgres version:-"+pg_version
f = open("recommend.txt","w")
f.write("-"*22)
#f.write("\n")
#f.write(" "*23+"POSTGRESQL STATIC ANALYSER REPORT\n")
f.write("POSTGRESQL STATIC ANALYSER REPORT")
f.write("-"*22)
f.write("\n\n")

flag = 0
if pg_version!="":
    f.write("PostgreSQL Version       =  "+pg_version)
    f.write("Postgesql.conf file path =  "+PostgreConf_path)
    f.write("\n")
    flag = 0
else:
    f.write("PostgreSQL is not available")
    f.write("\n")
    flag = 1
f.write("Current Time             =  "+str(now_time))
f.write("\n")
f.write("Current Date             =  "+str(now_date))
f.write("\n")
f.write("TestVersion              =  "+test_version)
f.write("\n\n")

p1 = subprocess.Popen("python src/os_info.py",stdout=subprocess.PIPE,shell=True)
p1.wait()
f_os = open("os.conf","r")
f.write(f_os.read())
f_os.close()
f.write("\n")

#f.write("#"*70)
f.write("\n\n"+"-"*29+"POSTGRESQL PARAMETERS"+"-"*29+"\n\n")
f.write("Memory units are in KB\n")
f.write("shb            :   shared_buffer\n")
f.write("wm             :   work_memory\n")
f.write("temp           :   temp_file_limit\n")
f.write("fsync          :   fsync\n")
f.write("sy_c           :   synchronous_commit\n")
f.write("wal_b          :   wal_buffers\n")
f.write("full_pgw       :   full_page_writes\n")
f.write("chk            :   checkpoint_segments\n")
f.write("chkTime        :   checkpoint_timeout\n")
f.write("chkComplete    :   checkpoint_completion_target\n\n")
#f.write("#"*70)
f.write("\n\n")
f.close()

if flag == 0:
    p2 = subprocess.Popen("python src/shared_buffer.py %s"%PostgreConf_path,stdout=subprocess.PIPE,shell=True)
    p2.wait()
    print p2.stdout.read()

    p3 = subprocess.Popen("python src/work_mem.py %s"%PostgreConf_path,stdout=subprocess.PIPE,shell=True)
    p3.wait()
    print p3.stdout.read()

    p4 = subprocess.Popen("python src/wal_buffer.py %s"%PostgreConf_path,stdout=subprocess.PIPE,shell=True)
    p4.wait()
    print p4.stdout.read()
    p5 = subprocess.Popen("python src/check_points.py %s"%PostgreConf_path,stdout=subprocess.PIPE,shell=True)
    p5.wait()
    print p5.stdout.read()

    p6 = subprocess.Popen("python src/file_loc.py %s"%PostgreConf_path,stdout=subprocess.PIPE,shell=True)
    p6.wait()
    print p6.stdout.read()


    p7 = subprocess.Popen("python src/system_tune.py %s"%PostgreConf_path,stdout=subprocess.PIPE,shell=True)
    p7.wait()
    print p7.stdout.read()

#generating report
f = open("recommend.txt","r")
file = f.read()
f.close()
f = open("report","w")
f.write(file)
f.close()

p8 = subprocess.Popen("python src/pdf_convert.py report",stdout=subprocess.PIPE,shell=True)
p8.wait()
p9 = subprocess.Popen("rm recommend.txt report os.conf",stdout=subprocess.PIPE,shell=True)

print(p8.stdout.read())
