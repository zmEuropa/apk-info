import sys
import re
import os
import hashlib
import subprocess
import zipfile
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

def ToDealWithVersionNameString(string):
    str = ''
    for word in string:
        if word >= '0' and word <= '9':
            str += word
        elif word is '.':
            str += word
        else :
            break
    return  str;
        

def getIconPath(res):
    show = ''
    for line in res:
        if line.find('application:') == 0:
            show += line
            break;
    reg = re.compile(
        "application: label='(?P<label>.*)' icon='(?P<icon>.*)'")
    regMatch = reg.match(show)
    if regMatch:
        linebits = regMatch.groupdict()
        if linebits['icon'] is '':
            return None
        else:
            return linebits['icon']
    else:
        return None

def parse_icon(filePath, iconPath):
    if iconPath == None:
        return
    zip = zipfile.ZipFile(filePath)
    iconData = zip.read(iconPath)
    saveIconName = "icon.png"
    with open(saveIconName,'w+b') as saveIconFile:
        saveIconFile.write(iconData)


def getAppName(res1, res2):
    show1 = ''
    for line1 in res1:
        if line1.find('application:') == 0:
            show1 += line1
            break;
    reg1 = re.compile(
        "application: label='(?P<label>.*)' ")
    regMatch1 = reg1.match(show1) 
    if regMatch1:
        linebits1 = regMatch1.groupdict()
        if linebits1['label'] is '':
            show2 = ''
            for line2 in res2:
                if line2.find('String #0:') == 0:
                    show2 += line2
                    break;
            if show2 is '':
                return None
            else:
                return show2.split(': ')[-1]
        else:
            return linebits1['label']
    else:
        return None
    
def getIconPix(path, res):
#    os.popen('ERASE /Q icon.png')
    for root, dirs, files in os.walk('./'):
        for name in files:
            if(name.endswith(".png")):
                os.remove(os.path.join(root, name))
    parse_icon(path,getIconPath(res))
    pix = QPixmap('icon.png')
    return pix  

def getPackage(res, path):
    show = ''
    for line in res:
        if line.find('package') == 0:
            show += line 
            break;
    reg = re.compile(
        ".*name='(?P<packageName>.*)' versionCode='(?P<versionCode>.*)' versionName='(?P<versionName>.*)'")
    regMatch = reg.match(show)
    if regMatch:
        linebits = regMatch.groupdict()
        return "true", "apk文件分析成功", linebits['packageName'], linebits['versionCode'], ToDealWithVersionNameString(linebits['versionName'])
    else:
        return "false", "apk文件aapt分析操作失败，请确保文件路径({})是否书写正确".format(path), None, None, None


def getSdkVersion(res):
    show = ''
    for line in res:
        if line.find('sdkVersion') == 0:
            show += line
            break;
    reg = re.compile(
        "sdkVersion:'(?P<sdkVersion>.*)'")
    regMatch = reg.match(show)
    if regMatch:
        linebits = regMatch.groupdict()
        return linebits['sdkVersion']
    else:
        return None

def getTargetSdkVersion(res):
    show = ''
    for line in res:
        if line.find('targetSdkVersion') == 0:
            show += line
            break;
    reg = re.compile(
        "targetSdkVersion:'(?P<targetSdkVersion>.*)'")
    regMatch = reg.match(show)
    if regMatch:
        linebits = regMatch.groupdict()
        return linebits['targetSdkVersion']
    else:
        return None
    

def getPermission(res):
    string = ''
    for line in res:
        if line.find('uses-permission') == 0:
            string += re.search("\'.*\'", line).group() +'\r\n'
    return string.replace('\'', '')

def getDensities(res):
    string = ''
    for line in res:
        if line.find('densities') == 0:
            string += re.search("\'.*\'", line).group() +'\r\n'
    return string.replace('\'', '')

def getSupportsScreens(res):
    string = ''
    for line in res:
        if line.find('supports-screens') == 0:
            string += re.search("\'.*\'", line).group() +'\r\n'
    return string.replace('\'', '')

def getApplication(res):
    string = ''
    for line in res:
        if line.find('application:') == 0:
            string += line +'\r\n'
    return string


# 获取文件的md5
def getBigFileMD5(filepath):
    md5obj = hashlib.md5()
    maxbuf = 8192
    try:
        f = open(filepath, 'rb')
    except Exception as err:
        return "获取文件的md5失败,找不到文件，请确保文件路径（{}）是否书写正确".format(filepath)
    while True:
        buf = f.read(maxbuf)
        if not buf:
            break
        md5obj.update(buf)
    f.close()
    hash = md5obj.hexdigest()
    return str(hash).upper()


# 字节bytes转化kb\m\g
def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        return "Error,传入的字节格式不对"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%fG" % G
        else:
            return "%fM" % M
    else:
        return "%fkb" % kb


# 获取文件大小
def getFileSize(path):
    size = os.path.getsize(path)
    return formatSize(size)


# 获取文件夹大小
def getFileDirSize(path):
    sumsize = 0
    try:
        filename = os.walk(path)
        for root, dirs, files in filename:
            for fle in files:
                size = os.path.getsize(path + fle)
                sumsize += size
        return True, "成功得到文件夹大小", formatSize(sumsize)
    except Exception as err:
        return False, "获取文件夹大小失败,失败原因：{}".format(str(err)), None



class UI_init(QWidget):
    def __init__(self):
        super(UI_init, self).__init__()
        # 窗口标题
        self.setWindowTitle('CVTE-APK-INFO')
        # 定义窗口大小
        self.resize(700, 500)
        self.setFixedSize(700,500)
        
        self.QLabl = QLabel(self)
        self.QLabl.setText('请输入apk的路径:')
        self.QLabl.setFont(QFont("Timers", 12))
      #  self.QLabl.setGeometry(20, 20, 100, 150)
        #调用Drops方法
        self.setAcceptDrops(True)

        self.QLabl2 = QLabel(self)
        self.QLabl2.setText('Path:')
        self.QLabl2.move(0, 27)
        self.QLabl2.setFont(QFont("Timers", 12))
        self.editpath = QLineEdit('', self)
        self.editpath.setDragEnabled(True)
        self.editpath.setGeometry(50,25,550,25)

        self.btn1 = QPushButton('确定',self)
        self.btn1.setFont(QFont("Timers", 13))
        self.btn1.move(620, 27)
        self.btn1.clicked.connect(self.determine)
    
        self.appName = QLabel(self)
        self.appName.setText('应用名称')
        self.appName.setFont(QFont("Timers", 10))
        self.appName.move(0, 60)
        self.appNameIs = QLineEdit(self)
        self.appNameIs.setFont(QFont("Timers", 10))
        self.appNameIs.setGeometry(150,60,450,20)
        self.appNameIs.setReadOnly(True)

        self.version = QLabel(self)
        self.version.setText('发布版本/架构版本')
        self.version.setFont(QFont("Timers", 10))
        self.version.move(0, 85)
        self.pubilcVersionIs = QLineEdit(self)
        self.pubilcVersionIs.setFont(QFont("Timers", 10))
        self.pubilcVersionIs.setGeometry(150,85,350,20)
        self.pubilcVersionIs.setReadOnly(True)
        self.frameworkVersionIs = QLineEdit(self)
        self.frameworkVersionIs.setFont(QFont("Timers", 10))
        self.frameworkVersionIs.setGeometry(510,85,90,20)
        self.frameworkVersionIs.setReadOnly(True)

        self.packageName = QLabel(self)
        self.packageName.setText('原始包名')
        self.packageName.setFont(QFont("Timers", 10))
        self.packageName.move(0, 110)
        self.packageNameIs = QLineEdit(self)
        self.packageNameIs.setFont(QFont("Timers", 10))
        self.packageNameIs.setGeometry(150,110,450,20)
        self.packageNameIs.setReadOnly(True)

        self.SDKName = QLabel(self)
        self.SDKName.setText('最低/目标编译 SDK')
        self.SDKName.setFont(QFont("Timers", 10))
        self.SDKName.move(0, 135)
        self.sdkVersionIs = QLineEdit(self)
        self.sdkVersionIs.setFont(QFont("Timers", 10))
        self.sdkVersionIs.setGeometry(150,135,270,20)
        self.sdkVersionIs.setReadOnly(True)
        self.targetSdkVersionIs = QLineEdit(self)
        self.targetSdkVersionIs.setFont(QFont("Timers", 10))
        self.targetSdkVersionIs.setGeometry(430,135,260,20)
        self.targetSdkVersionIs.setReadOnly(True)

        self.screenName = QLabel(self)
        self.screenName.setText('屏幕尺寸')
        self.screenName.setFont(QFont("Timers", 10))
        self.screenName.move(0, 160)
        self.screenNameIs = QLineEdit(self)
        self.screenNameIs.setFont(QFont("Timers", 10))
        self.screenNameIs.setGeometry(150,160,540,20)
        self.screenNameIs.setReadOnly(True)
        
        self.densityName = QLabel(self)
        self.densityName.setText('密度')
        self.densityName.setFont(QFont("Timers", 10))
        self.densityName.move(0, 185)
        self.densityNameIs = QLineEdit(self)
        self.densityNameIs.setFont(QFont("Timers", 10))
        self.densityNameIs.setGeometry(150,185,540,20)
        self.densityNameIs.setReadOnly(True)
        

        self.permissionsName = QLabel(self)
        self.permissionsName.setText('权限')
        self.permissionsName.setFont(QFont("Timers", 10))
        self.permissionsName.move(0, 220)
        self.permissionsNameIs = QTextEdit(self)
        self.permissionsNameIs.setFont(QFont("Timers", 10))
        self.permissionsNameIs.setGeometry(150,220,540,80)
        #self.permissionsNameIs.setContextMenuPolicy(Qt.NoContextMenu)
        self.permissionsNameIs.setReadOnly(True)


        self.attributeName = QLabel(self)
        self.attributeName.setText('属性')
        self.attributeName.setFont(QFont("Timers", 10))
        self.attributeName.move(0, 310)
        self.attributeNameIs = QTextEdit(self)
        self.attributeNameIs.setFont(QFont("Timers", 10))
        self.attributeNameIs.setGeometry(150,310,540,80)
        self.attributeNameIs.setReadOnly(True)

        self.fileSizeName = QLabel(self)
        self.fileSizeName.setText('文件大小')
        self.fileSizeName.setFont(QFont("Timers", 10))
        self.fileSizeName.move(0, 400)
        self.fileSizeNameIs = QLineEdit(self)
        self.fileSizeNameIs.setFont(QFont("Timers", 10))
        self.fileSizeNameIs.setGeometry(150,400,540,20)
        self.fileSizeNameIs.setReadOnly(True)

        self.fileMD5Name = QLabel(self)
        self.fileMD5Name.setText('文件MD5值')
        self.fileMD5Name.setFont(QFont("Timers", 10))
        self.fileMD5Name.move(0, 425)
        self.fileMD5NameIs = QLineEdit(self)
        self.fileMD5NameIs.setFont(QFont("Timers", 10))
        self.fileMD5NameIs.setGeometry(150,425,540,20)
        self.fileMD5NameIs.setReadOnly(True)

        self.currentName = QLabel(self)
        self.currentName.setText('当前名称')
        self.currentName.setFont(QFont("Timers", 10))
        self.currentName.move(0, 450)
        self.currentNameIs = QLineEdit(self)
        self.currentNameIs.setFont(QFont("Timers", 10))
        self.currentNameIs.setGeometry(150,450,540,20)
        self.currentNameIs.setReadOnly(True)

        self.newName = QLabel(self)
        self.newName.setText('新名称')
        self.newName.setFont(QFont("Timers", 10))
        self.newName.move(0, 475)
        self.newNameIs = QLineEdit(self)
        self.newNameIs.setFont(QFont("Timers", 10))
        self.newNameIs.setGeometry(150,475,540,20)
        self.newNameIs.setReadOnly(True)

        self.picture = QLabel(self)
        self.picture.setGeometry(610,60,88,70)
       # self.picture.setStyleSheet("border: 2px solid red")

    
    # 鼠标拖入事件
    def dragEnterEvent(self, evn):
     #   self.setWindowTitle('鼠标拖入窗口了')
        self.editpath.setText(evn.mimeData().text().split('///')[-1])
        #鼠标放开函数事件
        evn.accept()

            
    def determine(self):
        self.cleanedit()
        self.setDisplay()

    def cleanedit(self):
        self.appNameIs.clear()
        self.pubilcVersionIs.clear()
        self.frameworkVersionIs.clear()
        self.packageNameIs.clear()
        self.sdkVersionIs.clear()
        self.targetSdkVersionIs.clear()
        self.screenNameIs.clear()
        self.densityNameIs.clear()
        self.permissionsNameIs.clear()
        self.attributeNameIs.clear()
        self.fileSizeNameIs.clear()
        self.fileMD5NameIs.clear()
        self.currentNameIs.clear()
        self.newNameIs.clear()
        self.picture.clear()

    def setDisplay(self):
        path = self.editpath.text()#'C:/Users/user/Desktop/cvte-TvService-2.6.0.apk'
        commond1 = 'aapt dump badging %s' % path
        res1=''
        try:
            adb1 = subprocess.Popen(commond1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            res1 = adb1.communicate()[0].decode().split("\r\n")
        except Exception as err:
            1+1 #空操作
        
        commond2 = 'aapt dump strings %s' % path
        res2=''
        try:
            adb2 = subprocess.Popen(commond2, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            res2 = adb2.communicate()[0].decode().split("\r\n")
        except Exception as err:
            1+1 #空操作
           # print(commond2+',Command parsing results are too long!')
           # QMessageBox.warning(self,"Warning", commond2+',Command parsing results are too long!')

        b, w, packageName, versionCode, versionName = getPackage(res1,path)
        if b is "true":
            self.appNameIs.setText(getAppName(res1,res2))
            self.pubilcVersionIs.setText(versionName)
            self.frameworkVersionIs.setText(versionCode)
            self.packageNameIs.setText(packageName)
            self.sdkVersionIs.setText(getSdkVersion(res1))
            self.targetSdkVersionIs.setText(getTargetSdkVersion(res1))
            self.screenNameIs.setText(getSupportsScreens(res1))
            self.densityNameIs.setText(getDensities(res1))
            self.permissionsNameIs.setPlainText(getPermission(res1))
            self.attributeNameIs.setPlainText(getApplication(res1))
            self.fileSizeNameIs.setText(getFileSize(path))
            self.fileMD5NameIs.setText(getBigFileMD5(path))
            self.currentNameIs.setText(path.split('/')[-1])
            self.newNameIs.setText(getAppName(res1,res2)+' '+versionName+'.'+versionCode+'.apk')
            self.picture.setPixmap(getIconPix(path,res1))
        else:
            QMessageBox.warning(self,"Error", w)
        

            
class child(UI_init):
    pass
        
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = UI_init()
    ex.show()
 #   ex1 = child()
 #   ex1.show()
    sys.exit(app.exec_())
