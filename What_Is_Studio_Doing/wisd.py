import psutil
import time
import os
import platform
import argparse
import sys

parser = argparse.ArgumentParser(
                    prog=sys.argv[0],
                    description='List and optionally kill processes',
                    epilog='Default behavior is to list processes.  Kill mode loops until no processes are left.')
                    
parser.add_argument('-k', '--kill', action='store_true')
parser.add_argument('--cwd', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('--replace', help='replace default base folders with comma delimited list')
parser.add_argument('--add', help='supplement default base folders with comma delimited list')

args = parser.parse_args()

OS = platform.system()
if None != args.replace :
    bases = args.replace.split(',')
elif 'Linux' == OS :
    bases = [os.environ.get("HOME")+'/.silabs','/opt/SimplicityInstaller']
elif 'Windows' == OS :
    bases = [os.environ.get("HOME")+'\\.silabs']
elif 'Darwin' == OS :
    bases = [os.environ.get("HOME")+'/.silabs','/Application/SimplicityInstaller.app']
else :
    print('Unhandled OS: %s'%(OS))
    quit()
if None != args.add :
    bases += args.add.split(',')
    
class Processes :
    def __init__(self) :
        self.ppid = {}
        self.name = {}
        self.cwd = {}
        self.processes = {}
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'ppid', 'cwd']):
            try:
                # proc.info['exe'] contains the absolute filesystem path
                if proc.info['exe']:
                    pe = proc.info['exe']
                    for pb in bases :
                        if len(pe) < len(pb) :
                            continue
                        if pe[:len(pb)] != pb :
                            continue
                        pid = proc.info['pid']
                        self.ppid[pid] = proc.info['ppid']
                        self.name[pid] = proc.info['name']
                        self.cwd[pid] = proc.info['cwd']
                        self.processes[pid] = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip system processes or processes with strict access permissions
                pass
        
    def get_children(self,pid) :
        children = []
        for p in self.ppid :
            if self.ppid[p] == pid :
                children.append(p)
        children.sort()
        return children

    def get_orphans(self) :
        orphans = []
        for p in self.ppid :
            pp = self.ppid.get(p) 
            if None == self.ppid.get(pp) :
                orphans.append(pp)
        orphans.sort()
        return orphans
    
    def ishow(self, pid, depth) :
        if 0 == depth and args.cwd :
            extra = " CWD:"+self.cwd[pid]
        else :
            extra = ""
        if not self.processes[pid].is_running() :
            extra += " (terminated)"
        print(depth*"    "+self.name[pid]+" (%d)"%(pid)+extra)
        for c in self. get_children(pid) :
            self.ishow(c,depth+1)

    def show(self) :
        for p in self.get_orphans() :
            for c in self.get_children(p) :
                self.ishow(c,0)

    def kill(self) :
        for pid in self.processes :
            proc = self.processes[pid]
            if (args.verbose) :
                print('killing %s (%d)'%(proc.info['name'],pid))
            proc.kill()

    def count(self) :
        return len(self.processes)

# If kill requested, loop until no remaining processes
# If kill not requested exit after first iteration
while True :
    studio_processes = Processes()
    if args.kill :
        if studio_processes.count() < 1 :
            print('No processes left')
            break
        studio_processes.kill()
    studio_processes.show()
    if not args.kill :
        break
