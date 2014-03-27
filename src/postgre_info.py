#finding postgresql info
import re
import subprocess
def get_postgre_version():
    p = subprocess.Popen("psql --version",stdout=subprocess.PIPE,shell=True)
    k = re.findall(r'psql\s+\(PostgreSQL\)\s+(.*)',p.stdout.read())
    postgre_version = k[0]
    return postgre_version

