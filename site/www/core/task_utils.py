import os, subprocess
import glob
import shlex, shutil
import re, random

from jinja2 import Template

class DomainConfig:
    def __init__(self, cfgFile, path=None, override=False):
        self.path = path
        self.cfgFile = cfgFile
        self.usedValues = {}
        self.currentValues = {}
        self.override = override
        self.existing = False
        if path :
            for f in glob.glob(path):
                self.readFile(f, self.addUsedValue)
        def updateCV(k,v):
            self.currentValues[k]=v
        if os.path.exists(cfgFile):
            self.readFile(cfgFile, updateCV)
            self.existing = True

    def exists(self):
        return self.existing != None

    def readFile(self, path, handler):
        print("Reading: ", path)
        cfgVars = []
        with open(path, 'r') as cfgFile:
            cfgVars = shlex.split(cfgFile.read(), comments=True)
        for var in cfgVars:
            mo = re.match('(\w+)=(.*)', var)
            if mo:
                handler(mo.group(1), mo.group(2))


    def addUsedValue(self, name, value):
        if name not in self.usedValues:
            self.usedValues[name] = []
        self.usedValues[name].append( value )

    def genUniqInt(self, name, minVal, maxVal):
        if name in self.currentValues and self.override == False:
            return
        used = {}
        while len(used) <= (maxVal-minVal):
            i = str(random.randint(minVal, maxVal))
            if name not in self.usedValues or i not in self.usedValues[name]:
                self.set(name, i)
                return
            used[i] = True
        raise Exception('Failed to find free uniq int in range [{},{}] for {}'.format(minVal, maxVal, name))

    def set(self, name, val):
        if name in self.currentValues and self.override == False:
            return
        self.currentValues[name] = val

    def get(self, name):
        return self.currentValues.get(name)

    def asDict(self):
        return self.currentValues

    def write(self ):
        with open(self.cfgFile, 'w') as cfgFile:
            for k,v in self.currentValues.items():
                cfgFile.write("{}={}\n".format(k,shlex.quote(v)))

def getDomainDir(user, domain):
    d = DirCreate('/srv')
    d.pushd( user )
    d.pushd( domain )
    return d

class DirCreate:
    def __init__(self, path):
        self.base = path
        self.paths = [ path ]
        self.path = path

    def clone(self):
        return DirCreate(self.base)

    def pushd(self, path):
        if path :
            self.paths.append(path)
            self.path = os.path.join( *self.paths )
            self.path = os.path.abspath(self.path)
        print("pushd :" , self.path)

    def popd(self):
        self.paths.pop()
        self.path = os.path.join( *self.paths )
        self.path = os.path.abspath(self.path)
        print("popd " , self.path)

    def filename(self, filename):
        return os.path.join( self.path, filename )

    def _mkdir(self, uid=-1, gid=-1, mode=None):
        try:
            os.makedirs(self.path)
        except FileExistsError:
            pass
        if uid >= 0 or gid >= 0:
            os.chown(self.path, uid, gid)
        if mode:
            os.chmod(self.path, mode)

    def mkdir(self, paths=None, uid=-1, gid=-1, mode=None):
        if not paths or len(paths)==0:
            return self._mkdir(uid, gid, mode)

        if type(paths) != list:
            paths = [ paths ]
        for path in paths:
            self.pushd(path)
            self._mkdir(uid, gid, mode)
            self.popd()
    def exists(self, *paths):
        if len(paths) == 0:
            return os.path.exists( self.path )
        for path in paths:
            if not os.path.exists( os.path.join( self.path, path ) ):
                return False
        return True
    def rm(self, *paths):
        for path in paths:
            try:
                os.unlink( os.path.join( self.path, path ) )
            except FileNotFoundError:
                pass

    def mv(self, fromFile, toFile):
        os.rename( os.path.join( self.path, fromFile ), os.path.join( self.path, toFile ) )

    def run(self, cmd, *args):
        subprocess.check_call(cmd, shell=True, cwd=self.path, *args)

class TemplateDir:
    def __init__(self, path, cfg):
        self.path = path
        self.destination = None
        self.cfg = cfg

    def walk(self, dirHandler, fileHandler):
        for root, dirs, files in os.walk(self.path):
            relRoot = os.path.relpath(root, self.path)
            dirHandler(root, relRoot, dirs)
            fileHandler(root, relRoot, files)

    def copyDirs(self, root, relRoot, dirs):
        self.destination.pushd(relRoot)
        self.destination.mkdir(dirs)
        self.destination.popd()

    def copyFiles(self, root, relRoot, files):
        self.destination.pushd(relRoot)
        for f in files:
            srcName = os.path.join(root, f)
            if f.endswith('.jinja2'):
                content = "???FAILED TEMPLATE PROCESSING"
                with open(srcName,'r') as fd:
                    t = Template(fd.read())
                    content = t.render(self.cfg)
                newFileName = f[0:-7]
                with open(self.destination.filename(newFileName),'w') as wfd:
                    wfd.write(content)
            else:
                shutil.copyfile(srcName, self.destination.filename(f))
                shutil.copymode(srcName, self.destination.filename(f))
        self.destination.popd()

    def copyTo(self, destination):
        self.destination = DirCreate(destination)
        self.walk(self.copyDirs, self.copyFiles)
