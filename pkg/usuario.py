import os
import random
import zipfile

from operacao import Operacao
from mkrdp import mkrdp
from command import command

def listusers():
    return [x.split(':')[0] for x in os.popen('getent passwd').read().rstrip('\n').split('\n')]

class Usuario:
    def __init__(self, name, args=None):
        self.name = name
        self.args = args

    def listgroups(self):
        return os.popen('id -Gnz '+self.name).read().rstrip('\x00').split('\x00')

    def kill(self):
        for x in command("smbstatus -bpu %s | tail -n1 | awk '{print $1}' | xargs kill"%self.name):
            yield x

    def criacao(self):
        u = self.name
        if u in listusers():
            raise Exception('user already exists')
        senha = random.randint(100000, 999999)
        print 'Senha inicial:', senha
        for x in command('smbldap-groupadd -a "%s"'%u): #if exit code not zero:
            yield x
        for x in command('smbldap-useradd -a -g "%s" -s /bin/false -m "%s"'%(u, u)):
            yield x
        for x in command('smbldap-usermod --shadowMax 3650 "%s"'%u):
            yield x
        for x in command('echo "%s" | smbldap-passwd -p "%s"'%(senha, u)):
            yield x
        for x in self.grupo('Domain Users'):
            yield x
        for x in self.preenchimento():
            yield x
    def preenchimento(self):
        u = self.name
        if not u in listusers():
            if os.system('sss_cache -U -G'):
                #if can not reset cache, wait a minute to refresh
                for x in command('sleep 60'):
                    yield x
            if not u in listusers():
                raise Exception('user doesn\'t exist')
        for x in command('mkdir -p -m 777 /home/%s/Desktop/operacoes/'%u):
            yield x
        for g in self.listgroups():
            print "%s\t%s"%(u, g)
            for x in command('ln -snf /mnt/cloud/operacoes/%s /home/%s/Desktop/operacoes/%s'%(g, u, g)):
                yield x
        with open('/home/%s/Desktop/SARD.rdp'%u, 'w') as f:
            f.write(mkrdp(u))
        try:
            for x in command("(cd /home; tar c */Desktop/SARD.rdp --mode='a+r' ) | tar x -C /mnt/cloud/operacoes/Administrators/rdps/"):
                yield x
        except:
            pass
        with zipfile.ZipFile('/mnt/cloud/operacoes/Administrators/rdps/%s/Desktop/%s.zip'%(u, u), 'w') as zipf:
            zipf.write('/mnt/cloud/operacoes/Administrators/rdps/%s/Desktop/SARD.rdp'%u, arcname='SARD.rdp')
        for x in self.permissoes():
            yield x
    def grupo(self, grupo=None):
        u = self.name
        if not u in listusers():
            if os.system('sss_cache -U -G'):
                #if can not reset cache, wait a minute to refresh
                for x in command('sleep 60'):
                    yield x
            if not u in listusers():
                raise Exception('user doesn\'t exist')
        if grupo is None:
            grupo = self.args['GRUPO']
        op = Operacao(grupo)
        if not op.exists():
            raise Exception('Group doesn\'t exist')
        if grupo in self.listgroups():
            raise Exception('User already in this group.')
        for x in command("smbldap-groupmod -m %s '%s'"%(u, grupo)):
            yield x
        if os.system('sss_cache -U -G'):
            #if can not reset cache, wait a minute to refresh
            for x in command('sleep 60'):
                yield x
        for x in self.preenchimento():
            yield x
    def permissoes(self):
        if not self.name in listusers():
            if os.system('sss_cache -U -G'):
                #if can not reset cache, wait a minute to refresh
                for x in command('sleep 60'):
                    yield x
            if not self.name in listusers():
                raise Exception('user doesn\'t exist')
        for x in command('chmod o-rwx /home/"%s" '%self.name):
            yield x
        for x in command('chown -h -R "%s":"%s" /home/"%s" '%((self.name,)*3)):
            yield x
    def zerar_senha(self):
        if not self.name in listusers():
            if os.system('sss_cache -U -G'):
                #if can not reset cache, wait a minute to refresh
                for x in command('sleep 60'):
                    yield x
            if not self.name in listusers():
                raise Exception('user doesn\'t exist')
        u = self.name
        print 'Sugestao de senha', random.randint(100000, 999999)
        for x in command('smbldap-passwd "%s"'%u):
            yield x
        for x in command('smbldap-usermod --shadowMax 3650 "%s"'%u):
            yield x