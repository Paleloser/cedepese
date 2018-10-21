from subprocess import call
import yaml
import subprocess
import kvm
import os

# Descargamos la imagen preparada:
call('wget http://vnx.dit.upm.es/download/cdps/p1/cdps-vm-base-p1.img.bz2', shell=True)

# La descomprimimos
print 'Descomprimiendo la imagen...'
call('bunzip2 cdps-vm-base-p1.img.bz2', shell=True)
print 'Imagen descomprimida.'

# Generamos la base .qcow2, que servira de raiz a las vms
print 'Generando imagen .qcow2...'
call('qemu-img convert -O qcow2 cdps-vm-base-p1.img cdps-vm-base-p1.qcow2', shell=True)
call('cp cdps-vm-base-p1.qcow2 ~/.mykvm/base/precise64.qcow2', shell=True)
print '.qcow2 generado.'

n = input('Cuantas VM se van a crear? ')

# Instalamos (independientemente de que ya este instalado) virsh
print 'Instalando virsh...'
call('apt install -y libvirt-bin', shell=True)
print 'virsh instalado.'

if n:
    # yml de configuracion de mykvm
    print 'Configurando mykvm.yaml...'
    yml = [{'networks': [{'name': 'eno1',
                          'external': True,
                          'autostart': True,
                          'ip': '10.10.10.1'},
                         {'name': 'local',
                          'external': True,
                          'autostart': True,
                          'ip': '192.168.10.1'}]},
           {'vms': [{'name': 'cdps',
                     'vcpus': 2,
                     'ram': 2048,
                     'template': 'cdps-vm-base-p1.qcow2',
                     'netdevs': [{'network': 'eno1', 'ip': '10.10.10.10'},
                                 {'network': 'local', 'ip': '192.168.10.10'}]
                     }]
            }]
    call('mkdir /usr/local/share/mykvm', shell=True)
    call('mkdir /usr/local/share/mykvm/conf', shell=True)
    mykvm = open('/usr/local/share/mykvm/conf/mykvm.yml', 'w+')
    mykvm.write(yaml.dump(yml, default_flow_style=False, allow_unicode=True))
    print 'YAML cargado.'

    # vmbuilder script
    print 'Configurando vmbuilder.sh...'
    call('wget https://raw.githubusercontent.com/scottchoi/mykvm/master/script/vmbuilder.sh', shell=True)
    vmbuilder = open('vmbuilder.sh', 'r')
    newVmbuilder = open('vmbuilder2.sh', 'w+')

    for line in vmbuilder:
        if '--suite' in line:
            newVmbuilder.write('sudo vmbuilder kvm ubuntu --suite xenial --arch amd64 --flavour generic \\\n')
        elif '--timezone' in line:
            newVmbuilder.write('--timezone Europe/Spain --ssh-user-key ~/.ssh/id_rsa.pub    \\\n')
        elif '--mirror' in line:
            newVmbuilder.write('--mirror http://ftp.daum.net/ubuntu --addpkg=vim          \\\n')
        elif '.qcow2' in line:
            continue
        elif 'mkdir' in line:
            continue
        else:
            newVmbuilder.write(line)

    vmbuilder.close()
    newVmbuilder.close()
    call('mkdir /usr/local/share/mykvm/script', shell=True)
    call('mv vmbuilder2.sh /usr/local/share/mykvm/script/vmbuilder.sh', shell=True)

    # Iniciamos la vm
    print 'Iniciando mykvm...'
    call('mykvm init', shell=True)
    call('mykvm up', shell=True)
    print 'mykvm iniciado y corriendo.'

    # Obtenemos el ID de la vm
    print 'Obteniendo ID de la vm para dumpear su XML...'
    vmId = subprocess.check_output(["virsh list", "--all", "|",
                                    "grep", "'cdps'", "|",
                                    "awk", "'{ print $1 }'"])

    # Dumpeamos el XML de la vm
    call('virsh dumpxml %s > cdps-vm-base-p1.xml' % vmId, shell=True)

    # Borramos todas las instancias kvm (necesario para crear vms a partir de la base)
    call('mykvm destroy', shell=True)
    print 'XML dumpeado. Maquina borrada.'

# Generamos los XML y COW de cada vm
for i in range(0, n):

    vmName = 'cdps-vm%i' % i

    # Generamos .qcow2 para cada vm
    print 'Generando base (COW) de la VM', i
    qcow = '%s.qcow2' % vmName
    s = 'qemu-img create -f qcow2 -b cdps-vm-base-p1.qcow2 %s' % qcow
    call(s, shell=True)

    # Generamos su source, UUID y MAC
    pwd = '%s/%s' % (os.getcwd(), qcow)
    uuid = kvm.gen_uuid()
    mac = kvm.gen_mac()
    print 'Datos de la VM %s' % vmName
    print 'SRC: %s' % pwd
    print 'UUID: %s' % uuid
    print 'MAC: %s' % mac

    # Generamos el XML
    xml = '%s.xml' % vmName
    f = open('cdps-vm-base-p1.xml')
    out = open('%s' % xml, 'w+')

    for line in f:
        if '<name' in line:
            out.write('<name>%s</name>' % vmName)
        elif '<uuid' in line:
            out.write('<uuid>%s</uuid>' % uuid)
        elif '<mac' in line:
            out.write("<mac address='%s'/>" % mac)
        elif '<source' in line:
            out.write("<source file='%s' />" % pwd)
        else:
            out.write(line)

    f.close()
    out.close()
