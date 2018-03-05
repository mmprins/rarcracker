#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import subprocess,os
from multiprocessing import Pool,Manager
COUNT=0
PASSWD=''
q=Manager().Queue()
def cracktest(passwd,q):
    if subprocess.call(['unrar','t','-inul','-p%s'%passwd,'/tmp/ASTM_2015_Standards.rar','ASTM_2015_Standards/ASTM 2015 PART IA/ASTM 2015 Volume 01.01 Steel - Piping, Tubing, Fittings/A1014A1014M-10_Standard_Specification_for_Precipitation-Hardening_Bolting_(UNS_N07718)_for_High_Temperature_Service.pdf'],stdout = open('/dev/null','w'),stderr = subprocess.STDOUT):
        print('%d passwd %s test faild'%(COUNT,passwd))
    else:
        print('the correct passwd is:%s'%passwd)
        q.put(passwd)
        return True
with open('28GBwordlist.dic','r') as fp:
    while True:
        chunk_list=fp.readlines(102400000)#100MB
        count=0
        if chunk_list:
            print('a new chunks start now!')
            while True:
                if not q.empty():
                    PASSWD=q.get()
                    print('PASSWD=%s'%PASSWD)
                    exit()
                if count == len(chunk_list):
                    break
                P=Pool(os.cpu_count())
                for i in range(os.cpu_count()):
                    if count == len(chunk_list):
                        print('chunk end')
                        break
                    testpasswd=chunk_list[count]
                    count+=1
                    COUNT+=1
                    P.apply_async(cracktest,args=(testpasswd[:-1],q))
                P.close()
                P.join()
        else:
            print('all passwd have been checked,exit now!')
            break
