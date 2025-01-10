python - << EOF
import subprocess
import re
def getmemperc (value):
    try:
        return float(re.split('\s+', value)[6][:-1])
    except:
        return 0
proc = subprocess.Popen(['docker','stats'],stdout=subprocess.PIPE)
arr = []    
for line in iter(proc.stdout.readline,''):
    line = line.rstrip().decode()
    if (line.startswith('\x1b[2J\x1b[H')):
        if arr != []:
            print(arr.pop(0))
            arr = sorted(arr, key=lambda x: getmemperc(x), reverse=True)
            for a in arr:
                print(a)
        arr = []
    arr.append(line)
EOF
