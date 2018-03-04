#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import subprocess,os
from multiprocessing import Pool,Manager
COUNT=0
PASSWD=''
q=Manager().Queue()
def cracktest(passwd,q):
    if subprocess.call(['unrar','t','-inul','-p%s'%passwd,'ASTM_2015_Standards.rar','ASTM_2015_Standards/ASTM 2015 PART IA/ASTM 2015 Volume 01.01 Steel - Piping, Tubing, Fittings/A1014A1014M-10_Standard_Specification_for_Precipitation-Hardening_Bolting_(UNS_N07718)_for_High_Temperature_Service.pdf'],stdout = open('/dev/null','w'),stderr = subprocess.STDOUT):
        print('%d passwd %s test faild'%(COUNT,passwd))
    else:
        print('the correct passwd is:%s'%passwd)
        q.put(passwd)
        return True
with open('28GBwordlist.dic','r') as fp:
    while True:
        P=Pool(os.cpu_count())
        for i in range(os.cpu_count()):
            testpasswd=fp.readline()
            if testpasswd:
                P.apply_async(cracktest,args=(testpasswd[:-1],q))
            COUNT+=1
        P.close()
        P.join()
        if not q.empty():
            PASSWD=q.get()
            print('PASSWD=%s'%PASSWD)
            break
