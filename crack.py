#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import subprocess,os,sys
from multiprocessing import Pool,Manager,Process
class cracker(object):
    def __init__(self,filename,filetype,dictfile,COUNT,target_file):
        self.filename=filename
        self.filetype=filetype
        self.dictfile=dictfile
        self.COUNT=COUNT
        self.target_file=target_file
        self.PASSWD=''
        self.q=Manager().Queue()
    def _subproc(self,passwd,filename,q):
        '''subprocess.call 运行程序完全正常执行返回0,否则按照不同错误返回其他值'''
        if subprocess.call([self.filetype,'t','-y','-p%s'%passwd,filename,self.target_file],stdout = open('/dev/null','w'),stderr = subprocess.STDOUT):
            print('%d passwd %s test failed'%(self.COUNT,passwd))
        else:#subprocess.call返回0即密码测试成功
            q.put(passwd)
    def _wordlist(self):#内置破解字典生成器,6位纯数字
        for i in range(1000000):
            yield '000000'[:-len(str(i))]+str(i)+'\n'#000000-->999999六位纯数字
    def CrackFromBuildin(self):#使用内建6位纯数字字典生成器检验密码
        wordlist=self._wordlist()
        subprocount=0
        for i in range(self.COUNT):#跳过上次已完成检验任务
            next(wordlist)
        for passwd_test in wordlist:
            self.COUNT+=1
            if not self.q.empty():#队列q非空取值时即为正确密码
                self.PASSWD=self.q.get()
                print('PASSWD=%s'%self.PASSWD)
                break
            else:
                if subprocount == 0:
                    P=Pool(os.cpu_count())
                P.apply_async(self._subproc,args=(passwd_test[:-1],self.filename,self.q))
                subprocount+=1
                if not passwd_test:#字典文件读完结束退出
                    P.close()
                    P.join()
                    print('all passwd have been checked,exit now!')
                    break
                if subprocount == os.cpu_count():#收集子程序数等于CPU核心数量
                    P.close()
                    P.join()
                    subprocount=0#子程序运行结束，重置subproc数量归0
    def CrackFromDicfile(self):#使用外部字典表文件检验密码
        with open(self.dictfile,'r') as fp:
            subprocount=0#初始化subproc计数
            while True:
                passwd_test=fp.readline()
                for i in range(self.COUNT):#跳过上次已完成检验任务
                    fp.readline()
                if not self.q.empty():#队列q非空取值时即为正确密码
                    self.PASSWD=self.q.get()
                    print('PASSWD=%s'%self.PASSWD)
                    break
                else:
                    if subprocount == 0:
                        P=Pool(os.cpu_count())
                    P.apply_async(self._subproc,args=(passwd_test[:-1],self.filename,self.q))
                    subprocount+=1
                    self.COUNT+=1
                    if not passwd_test:#字典文件读完结束退出
                        P.close()
                        P.join()
                        print('all passwd have been checked,exit now!')
                        break
                    if subprocount == os.cpu_count():#收集子程序数等于CPU核心数量
                        P.close()
                        P.join()
                        subprocount=0#子程序运行结束，重置subprocount数量归0
if __name__=='__main__':
    filename='test.7z'
    filetype='7za'
    dictfile='buildin'
    COUNT=0#用于恢复被中断的破解过程
    target_file=''#指定单个测试用目标文件文件
    args=['',filename,filetype,dictfile,COUNT,target_file] 
    if len(sys.argv) > 1:
        for i in range(len(sys.argv)):
            args[i]=sys.argv[i]#根据sys.argv重置参数值
        sss=cracker(args[1],args[2],args[3],args[4],args[5])
        if args[3] == 'buildin':
            sss.CrackFromBuildin()
        else:
            sss.CrackFromDicfile()
    else:
        print("useage : crack [filename] [7za|unrar] [dictfile] [COUNT] [target_file]") 
