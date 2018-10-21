from subprocess import call
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
print '.qcow2 generado.'

n = input('Cuantas VM se van a crear? ')

# Instalamos (independientemente de que ya este instalado) virsh
print 'Instalando virsh...'
call('sudo apt install -y libvirt-bin', shell=True)

if n:
    # Iniciamos la vm
    call(['mykvm init', 'cdps-vm-base-p1.qcow2'], shell=True)
    call('mykvm up', shell=True)

    # Obtenemos el ID de la vm
    vmId = subprocess.check_output(["sudo virsh list", "--all", "|",
                                    "grep", "'cdps'", "|",
                                    "awk", "'{ print $1 }'"])

    # Dumpeamos el XML de la vm
    call('sudo virsh dumpxml %s > cdps-vm-base-p1.xml' % vmId, shell=True)

    # Borramos todas las instancias kvm (necesario para crear vms a partir de la base)
    call('mykvm destroy', shell=True)

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
    out = open('%s', xml)

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