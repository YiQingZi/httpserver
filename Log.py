__author__ = 'guozixiang'
__version__ = "1.0.0"
# @createtime:2021/8/11 - 17:23

import logging
import os
import sys
import time


def get_FileSize(filePath):
    """
    返回文件大小 MB
    """
    try:
        filesize = os.path.getsize(filePath)
        filesize = filesize / float(1024 * 1024)
        return round(filesize, 2)
    except IOError as err:
        print(err)
        return 0

def strTimeName():
    """
    格式化时间，返回当前时间
    """
    t = time.localtime(time.time())
    strT = time.strftime('%Y-%m-%d-%H-%M-%S', t)
    #%Y-%m-%d-%H-%M-%S  Y 年  m月 d日  H时 M分 S秒
    return str(strT)

def get_sys_path():
    """
    返回运行路径
    """
    return str(sys.path[0])

def Find_newest_log():
    dir = r'{0}\Log'.format(get_sys_path())
    lists = os.listdir(dir)
    if len(lists) == 0:
        p =r'{0}\Log\HTTPLog-{1}.log'.format(get_sys_path(), strTimeName())
        with open(p,mode='w+') as f:
            f.write(p)
        return p
    lists.sort(key=lambda fn: os.path.getmtime(dir + "\\" + fn))  # 按时间排序
    file_new = os.path.join(dir, lists[-1])
    return file_new

def log(loglevel,logcontent):
    #创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)# Log等级总开关
    #logname = r'{0}\Log\RunTestLog-{1}.log'.format(get_sys_path(), TimeUtils.strTimeName())
    logname = Find_newest_log()
    if get_FileSize(logname) > 2.0:
        logname = r'{0}\Log\HTTPLog-{1}.log'.format(get_sys_path(), strTimeName())
    fh = logging.FileHandler(logname)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s-[MEIG]-%(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    #将logger添加到handler里面
    logger.addHandler(fh)
    logger.addHandler(ch)
    loglevel = loglevel.lower()
    if loglevel == "info":
        logger.info(logcontent)
        logger.removeHandler(fh)
        logger.removeHandler(ch)
    elif loglevel == "error":
        logger.error(logcontent)
        logger.removeHandler(fh)
        logger.removeHandler(ch)
    elif loglevel == "warning":
        logger.warning(logcontent)
        logger.removeHandler(fh)
        logger.removeHandler(ch)
    else:
        logger.debug(logcontent)
        logger.removeHandler(fh)
        logger.removeHandler(ch)