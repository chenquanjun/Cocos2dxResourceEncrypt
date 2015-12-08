#coding=utf-8
#!/usr/bin/python
import os 
import os.path 
import sys, getopt  
import subprocess
import shutil 
import time,  datetime
import platform
from hashlib import md5
import hashlib  
import binascii

def removeDir(dirName):
    if not os.path.isdir(dirName): 
        return
    filelist=[]
    filelist=os.listdir(dirName)
    for f in filelist:
        filepath = os.path.join( dirName, f )
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath,True)

def initEnvironment():
    global APP_ROOT #工程根目录 
    global APP_ANDROID_ROOT #安卓根目录
    global QUICK_ROOT #引擎根目录
    global QUICK_BIN_DIR #引擎bin目录
    global APP_RESOURCE_ROOT #生成app的资源目录
    global APP_RESOURCE_RES_DIR #资源目录

    global APP_BUILD_USE_JIT #是否使用jit

    global PHP_NAME #php
    global SCRIPT_NAME #执行脚本文件名

    global BUILD_PLATFORM #生成app对应的平台

    SYSTEM_TYPE = platform.system() #当前操作系统

    APP_ROOT = os.getcwd() #当前目录
    APP_ANDROID_ROOT = APP_ROOT + "/frameworks/runtime-src/proj.android"
    QUICK_ROOT = os.getenv('QUICK_V3_ROOT')

    if QUICK_ROOT == None: #quick引擎目录未指定，可手动指定路径或者运行引擎目录下相应脚本
        print "QUICK_V3_ROOT not set, please run setup_win.bat/setup_mac.sh in engine root or set QUICK_ROOT path"
        return False

    if(SYSTEM_TYPE =="Windows"): 
        QUICK_BIN_DIR = QUICK_ROOT + "quick/bin"
        PHP_NAME = QUICK_BIN_DIR + "/win32/php.exe" #windows
        BUILD_PLATFORM = "android" #windows dafault build android
        SCRIPT_NAME = "/compile_scripts.bat"
    else:
        PHP_NAME = "php"
        BUILD_PLATFORM = "ios" #mac default build ios
        QUICK_BIN_DIR = QUICK_ROOT + "/quick/bin" #mac add '/'
        SCRIPT_NAME = "/compile_scripts.sh"


    if(BUILD_PLATFORM =="ios"):
        APP_BUILD_USE_JIT = False
        APP_RESOURCE_ROOT = APP_ROOT + "/Resources" 
        APP_RESOURCE_RES_DIR = APP_RESOURCE_ROOT + "/res"

    else:
        APP_BUILD_USE_JIT = True
        APP_RESOURCE_ROOT = APP_ANDROID_ROOT + "/assets" #default build android
        APP_RESOURCE_RES_DIR = APP_RESOURCE_ROOT + "/res"

    print 'App root: %s' %(APP_ROOT)
    print 'App resource root: %s' %(APP_RESOURCE_ROOT)
    return True

def compileScriptFile(compileFileName, srcName, compileMode):
    scriptDir = APP_RESOURCE_RES_DIR + "/code/"
    if not os.path.exists(scriptDir):
        os.makedirs(scriptDir)
    try:
        scriptsName = QUICK_BIN_DIR + SCRIPT_NAME
        srcName = APP_ROOT + "/" + srcName
        outputName = scriptDir + compileFileName
        args = [scriptsName,'-i',srcName,'-o',outputName,'-e',compileMode,'-es','XXTEA','-ek','ilovecocos2dx']

        if APP_BUILD_USE_JIT:
            args.append('-jit')

        proc = subprocess.Popen(args, shell=False, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
        while proc.poll() == None:  
            outputStr = proc.stdout.readline()
            print outputStr,
        print proc.stdout.read(),
    except Exception,e:  
        print Exception,":",e

def packRes():
    if not os.path.exists('PackRes.php'):
        print 'Error: PackRes.php not exist, pack res stop!'
        return

    removeDir(APP_ROOT + "/packres/") #--->删除旧加密资源

    scriptName = QUICK_BIN_DIR + "/lib/pack_files.php"
    try:
        args = [PHP_NAME, scriptName, '-c', 'PackRes.php']
        proc = subprocess.Popen(args, shell=False, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
        while proc.poll() == None:  
            print proc.stdout.readline(),
        print proc.stdout.read()
    except Exception,e:  
        print Exception,":",e

if __name__ == '__main__': 
    isInit = initEnvironment()

    if isInit == True:
        #加密资源
        packRes()

        #将src目录下的所有脚本加密打包成game.zip
        compileScriptFile("game.zip", "src", "xxtea_zip")