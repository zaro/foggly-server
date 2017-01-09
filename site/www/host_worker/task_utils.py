import os, subprocess
import glob
import shlex, shutil
import re, random, sys

from jinja2 import Template


if os.path.exists( '/host_srv' ):
    TOP_DIR = '/host_srv'
else:
    TOP_DIR = '/srv'


class DomainConfig:
    IS_LIST = ['REDIRECT_ALIASES']

    def __init__(self, cfgFile, path=None, override=False):
        self.path = path
        self.cfgFile = cfgFile
        self.usedValues = {}
        self.currentValues = {}
        self.override(override)
        self.existing = False
        if path:
            for f in glob.glob(path):
                self.readFile(f, self.addUsedValue)

        def updateCV(k, v):
            self.currentValues[k] = v
        if os.path.exists(cfgFile):
            self.readFile(cfgFile, updateCV)
            self.existing = True

    def override(self, override):
        self._override = override

    def asDict(self):
        return self.currentValues

    def exists(self):
        return self.existing is not None

    def readFile(self, path, handler):
        print("Reading: ", path)
        cfgVars = []
        with open(path, 'r') as cfgFile:
            for line in cfgFile.readlines():
                if re.match(r'^\s*#', line):
                    continue
                mo = re.match('\s*(\w+)=(.*)', line)
                if mo:
                    key = mo.group(1)
                    val = mo.group(2)
                    if key in self.IS_LIST:
                        mo = re.match('^\((.*)\)\s*$', val)
                        if mo:
                            val = shlex.split(mo.group(1))
                        else:
                            val = shlex.split(val)
                    handler(key, val)

    def addUsedValue(self, name, value):
        if name not in self.usedValues:
            self.usedValues[name] = []
        self.usedValues[name].append( value )

    def genUniqInt(self, name, minVal, maxVal):
        if name in self.currentValues and self._override is False:
            return
        used = {}
        while len(used) <= (maxVal - minVal):
            i = str(random.randint(minVal, maxVal))
            if name not in self.usedValues or i not in self.usedValues[name]:
                self.set(name, i)
                return
            used[i] = True
        raise Exception('Failed to find free uniq int in range [{},{}] for {}'.format(minVal, maxVal, name))

    def set(self, name, val):
        if name in self.currentValues and self._override is False:
            return
        self.currentValues[name] = val

    def get(self, name):
        return self.currentValues.get(name)

    def write(self ):
        with open(self.cfgFile, 'w') as cfgFile:
            for k, v in self.currentValues.items():
                if k in self.IS_LIST:
                    qv = []
                    if type(v) is list or type(v) is tuple:
                        for arrayVal in v:
                            qv.append( shlex.quote(arrayVal) )
                        v = '(' + " ".join(qv) + ')'
                    else:
                        if v is not None:
                            v = '(' + shlex.quote(str(v)) + ')'
                        else:
                            v = ''
                else:
                    if v is not None:
                        v = shlex.quote(str(v))
                    else:
                        v=''
                cfgFile.write("{}={}\n".format(k, v))


def allDomainDirs():
    for userDir in os.listdir(TOP_DIR):
        userDirPath = os.path.join(TOP_DIR, userDir)
        if not userDir.startswith('_') and os.path.isdir( userDirPath ):
            for domainDir in os.listdir(userDirPath):
                domainDirPath = os.path.join(userDirPath, domainDir)
                if os.path.isdir( domainDirPath ):
                    yield DirCreate(domainDirPath)


def getDomainDir(user, domain):
    d = DirCreate(TOP_DIR)
    d.pushd( user )
    d.pushd( domain )
    return d


class DirCreate:
    def __init__(self, path):
        self.base = path
        self.paths = [ path ]
        self.path = path

    def getDockerLocation(self, topDir='/srv'):
        return re.sub('^' + TOP_DIR, "/srv", self.path, 1 )

    def clone(self):
        return DirCreate(self.base)

    def pushd(self, path):
        if path:
            self.paths.append(path)
            self.path = os.path.join( *self.paths )
            self.path = os.path.abspath(self.path)
        print("pushd :" + self.path)

    def popd(self):
        self.paths.pop()
        self.path = os.path.join( *self.paths )
        self.path = os.path.abspath(self.path)
        print("popd " + self.path)

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
        if not paths or len(paths) == 0:
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
        if len(paths) == 0:
            paths = ('',)
        for path in paths:
            try:
                os.unlink( os.path.join( self.path, path ) )
            except FileNotFoundError:
                pass

    def rmtree(self, *paths):
        if len(paths) == 0:
            paths = ('',)
        for path in paths:
            try:
                shutil.rmtree( os.path.join( self.path, path ), ignore_errors=False )
            except FileNotFoundError:
                pass

    def chmod(self, mode, *paths):
        if len(paths) == 0:
            os.chmod( self.path, mode )
        for path in paths:
            os.chmod( os.path.join( self.path, path ), mode  )

    def chown(self, uid, gid, *paths):
        if len(paths) == 0:
            os.chown(self.path, uid, gid)
        for path in paths:
            os.chown(os.path.join( self.path, path ), uid, gid)

    def mv(self, fromFile, toFile):
        print("mv " + str(fromFile) + " " + str(toFile))
        os.rename( os.path.join( self.path, fromFile ), os.path.join( self.path, toFile ) )

    def cp(self, fromFile, toFile=None):
        print("cp " + str(fromFile) + " " + str(toFile))
        if not toFile:
            toFile = os.path.join( self.path, os.path.basename(fromFile))
        shutil.copyfile(fromFile, toFile)
        shutil.copymode(fromFile, toFile)

    def cpIfExist(self, fromFile, toFile=None):
        print("cpIfExist " + str(fromFile) + " " + str(toFile))
        if os.path.exists( fromFile ):
            self.cp(fromFile, toFile)
        else:
            print("cpIfExist missing: " + str(fromFile))

    def run(self, cmd, *args):
        subprocess.check_call(cmd, shell=True, cwd=self.path, *args)

    def writeFile(self, path, contents):
        with open(self.filename(path), 'w') as f:
            f.write(contents)

    def readFile(self, path):
        try:
            with open(self.filename(path), 'r') as f:
                return f.read()
        except:
            return None


class TemplateDir:
    TEMPLATE_EXTENSION = '.jinja2'

    def __init__(self, path, cfg):
        self.path = path
        self.destination = None
        self.cfg = cfg
        if not os.path.exists( self.path ):
            raise Exception("Missing template dir:" + str(self.path))

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
            print("{} -> {}".format(srcName, self.destination.filename(f)))
            if f.endswith(self.TEMPLATE_EXTENSION):
                content = "???FAILED TEMPLATE PROCESSING"
                with open(srcName, 'r') as fd:
                    t = Template(fd.read())
                    content = t.render(self.cfg)
                newFileName = f[0:-7]
                with open(self.destination.filename(newFileName), 'w') as wfd:
                    wfd.write(content)
            else:
                shutil.copyfile(srcName, self.destination.filename(f))
                shutil.copymode(srcName, self.destination.filename(f))
        self.destination.popd()

    def copyTo(self, destination):
        self.destination = DirCreate(destination)
        print("Template.copyTo {} -> {}".format(str(self.path), str(destination)))
        self.walk(self.copyDirs, self.copyFiles)

    def copyFileTo(self, fileName, destination):
        self.destination = DirCreate(destination)
        print("Template.copyFileTo {}/{} -> {}".format(str(self.path), fileName, str(destination)))
        if self.destination.exists(fileName + self.TEMPLATE_EXTENSION) and not self.destination.exists(fileName):
            fileName += self.TEMPLATE_EXTENSION
        self.copyFiles( self.path, "", [ fileName ])


class AuthorizedKeysFile:
    def __init__(self, domainDir):
        self.domainDir = domainDir
        self.readFile()

    def readFile(self):
        try:
            with open(self.domainDir.filename('.ssh/authorized_keys'), 'r') as f:
                self.lines = [ l.strip() for l in f.readlines()]
        except FileNotFoundError:
            self.lines = []

    def writeFile(self):
            with open(self.domainDir.filename('.ssh/authorized_keys'), 'w') as f:
                f.writelines([l + '\n' for l in self.lines])

    def addKey(self, key):
        key = key.strip()
        if key not in self.lines:
            self.lines.append( key )

    def removeKey(self, key):
        key = key.strip()
        while True:
            try:
                self.lines.remove(key)
            except ValueError:
                break

if __name__ == '__main__':
    dc = DomainConfig(sys.argv[1],override=True)
    print(dc.asDict())
