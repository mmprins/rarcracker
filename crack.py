#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import subprocess,os,sys
from multiprocessing import Pool,Manager,Process
from tkinter import *
def __parameters(args):
    global filename,filetype,COUNT,target_file,dictfile
    if len(args) == 1:
        print("useage : crack [-f filename] [-t 7za|unrar] [-N COUNT] [-T target_file] [-d bulidin|dictfile] ")
        return -1
    for arg in args:
        if arg[0] == '-':
            if not arg in ('-f','-t','-N','-d','-T'):
                print('parameter "%s" was not definded'%arg)
                return -1
    if '-f' in args:#压缩文件名称
        if os.path.exists(args[args.index('-f')+1]):
            filename=args[args.index('-f')+1]
        else:
            print("filename is not exists")
            return -1
    else:
        print("filename must be specified!")
        return -1
    if '-t' in args:#压缩文件类型，支持7za和unrar两种类型
        if not args[args.index('-t')+1] in ['7za','unrar']:
            print("unsupported filetype definded!")
            return -1
        filetype=args[args.index('-t')+1]
    if '-N' in args:#用于恢复被中断的破解过程
        try:
            COUNT=int(args[args.index('-N')+1])
        except:
            print("COUNT must be a int number!")
            return -1
    if '-d' in args:#指定使用的外部字典文件
        if os.path.exists(args[args.index('-d')+1]):
            dictfile=args[args.index('-d')+1]
        else:
            print("filename is not exists")
            return -1
    if '-T' in args:#指定压缩包内单个测试用目标文件
            target_file=args[args.index('-T')+1]
    return 0
def guistart():
    root=Tk()
    guisubproc=GUI(root)
    guisubproc.mainloop()
    guisubproc.destroy()
    root.destroy()
class GUI(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master,height=300,width=300)
        self.vtype=IntVar()
        self.pack(fill=X,padx=5,pady=5)
        self.createWidgets()
    def createWidgets(self):
        self.mainLabel=Label(self,text='RAR/7zip files crack application')
        self.mainLabel.pack()
        self.quitButton=Button(self,text='quit',command=self.quit).pack(side=BOTTOM)
        self.confirmButton=Button(self,text='confirm',command=self.quit).pack(side=BOTTOM)
        self.radiobutton(self.vtype)
    def radiobutton(self,value):
        vtype=value
        vtype.set(0)
        self.radioButton1=Radiobutton(self,text='7za',variable=vtype,value=0).pack()
        self.radioButton2=Radiobutton(self,text='Rar',variable=vtype,value=1).pack()
class cracker(object):
    def __init__(self,filename,filetype='7za',COUNT=0,target_file='./',dictfile='buildin'):
        self.filename=filename
        self.filetype=filetype
        self.COUNT=COUNT
        if self.filetype == '7za':
            if target_file == './':
                self.target_file=""
        else:
            self.target_file=target_file
        self.dictfile=dictfile
        self.PASSWD=''
        self.q=Manager().Queue()
    def _subproc(self,passwd,filename,q):
        '''subprocess.call 运行程序完全正常执行返回0,否则按照不同错误返回其他值'''
        if subprocess.call([self.filetype,'t','-y','-p%s'%passwd,filename,self.target_file],stdout = open('/dev/null','w'),stderr = subprocess.STDOUT):
            print('NU:%d passwd=%s test failed'%(self.COUNT,passwd))
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
            for i in range(self.COUNT):#跳过上次已完成检验任务
                fp.readline()
            while True:
                passwd_test=fp.readline()
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
    filename=''
    filetype='7za'
    COUNT=0#用于恢复被中断的破解过程
    target_file='./'#指定单个测试用目标文件文件
    dictfile='buildin'
    if __parameters(sys.argv) == 0:
        sss=cracker(filename,filetype,COUNT,target_file,dictfile)
        if dictfile == 'buildin':
            sss.CrackFromBuildin()
        else:
            sss.CrackFromDicfile()
