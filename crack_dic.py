#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import subprocess,os,sys
from multiprocessing import Pool,Manager
class cracker(object):
    def __init__(self,filename='test.7z',filetype='7za',dictfile='wordlist.txt',COUNT=0,target_file=None):
        self.filename=filename
        self.filetype=filetype
        self.dictfile=dictfile
        self.COUNT=COUNT
        self.target_file=target_file
        self.PASSWD=''
    def _subproc(self,passwd,filename,q):
        if subprocess.call([self.filetype,'x','-p%s'%passwd,filename,self.target_file],stdout = open('/dev/null','w'),stderr = subprocess.STDOUT):
            print('%d passwd %s test faild'%(self.COUNT,passwd))
        else:
            print('the correct passwd is:%s'%passwd)
            q.put(passwd)
    def cracktest(self):
        with open(self.dictfile,'r') as fp:
            q=Manager().Queue()
            if self.COUNT:
                print('start continue with COUNT value lines')
                for i in range(self.COUNT-os.cpu_count()):
                    fp.readline()
                self.COUNT=self.COUNT-os.cpu_count()
            while True:
                chunk_list=fp.readlines(10240000)#10MB
                with open('crack.log','w') as fw:
                    fw.write(str(self.COUNT))
                count=0
                if chunk_list:
                    print('a new chunks start now!')
                    while True:
                        if not q.empty():
                            self.PASSWD=q.get()
                            print('PASSWD=%s'%self.PASSWD)
                            exit()
                        elif count == len(chunk_list):
                            break
                        else:
                            P=Pool(os.cpu_count())
                            for i in range(os.cpu_count()):
                                if count == len(chunk_list):
                                    print('chunk end')
                                    break
                                else:
                                    testpasswd=chunk_list[count]
                                    count+=1
                                    self.COUNT+=1
                                    P.apply_async(self._subproc,args=(testpasswd[:-1],self.filename,q))
                            P.close()
                            P.join()
                else:
                    print('all passwd have been checked,exit now!')
                    break
if __name__=='__main__':
    if len(sys.argv) > 1:
        target_file='form.csv'
        COUNT=0
        sss=cracker(sys.argv[1],filetype='unrar',dictfile='wordlist.txt',COUNT=COUNT,target_file=target_file)
        sss.cracktest()
    else:
        pass
