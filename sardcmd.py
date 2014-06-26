#!/usr/bin/env python
import os
import cmd
import docopt
import yaml
import tempfile
import datetime
import random
from sardutils import *

all_storages='vmhost1 vmhost2 vmhost3 storage1 backup1'.split()

class Usuario:
    def __init__(self,name):
        self.name=name
    def listgroups(self):
        return os.popen('groups '+self.name).read().rstrip('\n').split(' ')[2:]
    def criacao(self):
        u=self.name
        command('smbldap-groupadd -a "%s"'%u)
        print 'Sugestao de senha', random.randint(100000,999999)
        command('smbldap-useradd -a -g "%s" -P -s /bin/false -m  "%s"'%((u,)*2))
        command('smbldap-usermod --shadowMax 3650 "%s"'%u)
        self.preenchimento()
    def preenchimento(self):
        u=self.name
        indices=''
        command('mkdir -p /home/%s/.maildir/operacoes'%u)
        command('echo > /home/%s/.maildir/operacoes/subscriptions'%u)
        for g in self.listgroups():
            print "%s\t%s"%(u,g)
            if os.path.isdir('/sard/extracao/'+g):
                if not os.path.exists('/home/%s/ThunderbirdPortable'%u):
                    usuario_zerarthunderbird.main(u)
                command('mkdir -p -m 777 /home/%s/Desktop/operacoes/'%u)
                command('ln -snf /sard/extracao/%s /home/%s/Desktop/operacoes/%s'%(g,u,g))
                if os.path.exists('/storage1/mnt/config/subscriptions/%s.subscriptions'%g):
                    command('cat /storage1/mnt/config/subscriptions/%s.subscriptions >> /home/%s/.maildir/operacoes/subscriptions'%(g,u))
        self.permissoes()
    def permissoes(self):
        command('chmod o-rwx -R /home/"%s" '%self.name)
        command('chown -h -R "%s":"%s" /home/"%s" '%((self.name,)*3))
    def zerar_thunderbird(self):
        u=self.name
        if os.path.exists('/home/%s/ThunderbirdPortable'%u):
            command("rm -r '/home/%s/ThunderbirdPortable'"%u)
        command('cp -r /git/sard-old/auxiliar/ThunderbirdPortable /home/%s/'%u)
        command("echo 'user_pref(\"mail.server.server2.userName\", \"%s\");' >> /home/%s/ThunderbirdPortable/Data/profile/prefs.js"%(u,u))
        command('chown -R %s:%s /home/%s/ThunderbirdPortable '%(u,u,u))
    def zerar_senha(self):
        print 'Sugestao de senha', random.randint(100000,999999)
        command('smbldap-passwd "%s"'%u)
        command('smbldap-usermod --shadowMax 3650 "%s"'%u)
        

class Operacao:
    def __init__(self,name):
        self.name=name
    def criacao(self):
        op=self.name
        command('smbldap-groupadd "%s"'%op)
        for x in all_storages:
            command('mkdir /storages/%s/extracao/"%s"'%(x,op))
        self.permissoes()
    def permissoes(self):
        op=self.name
        for x in all_storages:
            command('chown -R -h root:"%s" /storages/%s/extracao/"%s"'%(op,x,op))
            command('chmod -R u=rX,g=rX,o-rwx /storages/%s/extracao/"%s"'%(x,op))

            
class Sard(cmd.Cmd):
    def do_operacao(self,line):
        """
Usage:
        operacao criacao OPERACAO
        operacao permissoes OPERACAO

"""
        try:
            args=docopt.docopt(self.do_operacao.__doc__,line.split(),help=False)
            operacao=Operacao(args['OPERACAO'])
            for x in 'criacao permissoes'.split():
                if args[x]:
                    print Operacao.__dict__[x](operacao)
        except (docopt.DocoptExit) as e:
            print e
    
    
    def do_usuario(self,line):
        """
Usage:
        usuario criacao USUARIO
        usuario preenchimento USUARIO
        usuario permissoes USUARIO
        usuario listgroups USUARIO
        usuario zerar_thunderbird USUARIO
        usuario zerar_senha USUARIO

"""
        try:
            args=docopt.docopt(self.do_usuario.__doc__,line.split(),help=False)
            usuario=Usuario(args['USUARIO'])
            for x in 'criacao preenchimento permissoes listgroups zerar_thunderbird zerar_senha'.split():
                if args[x]:
                    print Usuario.__dict__[x](usuario)
        except (docopt.DocoptExit) as e:
            print e

    def do_EOF(self, line):
        """quit"""
        return True
    do_quit=do_exit=do_EOF

    def postloop(self):
        print

if __name__=='__main__':
    Sard().cmdloop()
