from subprocess import call
import subprocess
import os

# REQUISITOS
# PGMS: wget, bunzip, libvirt-bin, qemu-utils, virtinst
# MODULOS: kvm

# Descargamos la imagen preparada:
call('wget http://vnx.dit.upm.es/download/cdps/p1/cdps-vm-base-p1.img.bz2', shell=True)

# La descomprimimos
print 'Descomprimiendo la imagen...'
call('bunzip2 cdps-vm-base-p1.img.bz2', shell=True)

# Generamos la base .qcow2, que servira de raiz a las vms
print 'Generando imagen .qcow2...'
call('qemu-img convert -O qcow2 cdps-vm-base-p1.img cdps-vm-base-p1.qcow2', shell=True)
call('chmod 666 cdps-vm-base-p1.qcow2', shell=True)

# DESCOMENTAR EL SIGUIENTE BLOQUE PARA USO CON KVM + MULTIPLES VMS

# import kvm
# import time
#
# # Creamos la vm
# print 'Instalando maquina virtual base...'
# call('virt-install --import --name base --memory 2048 --disk cdps-vm-base-p1.qcow2 --vcpus=2 --os-type linux \\'
#      '--network default --keymap es --connect qemu:///system --noautoconsole', shell=True)
#
# # Obtenemos el ID de la vm
# print 'Obteniendo ID de la vm para dumpear su XML...'
# vmId = subprocess.check_output("sudo virsh list --all | grep 'base' | awk  '{ print $1 }'", shell=True)
#
# # Dumpeamos el XML de la vm
# print 'Dumpeando XML base para poder crear n copias OW'
# xml = subprocess.check_output("sudo virsh dumpxml %s" % vmId, shell=True)
# newXml = open('cdps-vm-base-p1.xml', "w+")
# newXml.write(xml)
# newXml.close()
#
# # Apagamos la base
# time.sleep(10)
# call('virsh shutdown base', shell=True)
# time.sleep(2)

n = input('Numero de maquinas a crear: ')

# Generamos los XML y COW, generamos la vm y la configuramos
for i in range(0, n):

    vmName = 'cdps-vm%i' % i

    # Generamos .qcow2 para cada vm
    print 'Generando base (COW) de la VM', i
    qcow = '%s.qcow2' % vmName
    s = 'qemu-img create -f qcow2 -b cdps-vm-base-p1.qcow2 %s' % qcow
    call(s, shell=True)

    # Generamos su source, UUID y MAC
    pwd = '%s/%s' % (os.getcwd(), qcow)

    # DESCOMENTAR PARA USO CON KVM + MULTIPLES VMS
    # uuid = kvm.gen_uuid()
    # mac = kvm.gen_mac()

    # COMENTAR PARA USO SIN KVM + UNA VM
    uuid = '85d78af1-6fe6-2851-9f38-600c047d25a8'
    mac = '54:52:00:44:c3:0f'

    print 'Datos de la VM %s' % vmName
    print 'SRC: %s' % pwd
    print 'UUID: %s' % uuid
    print 'MAC: %s' % mac

    # Generamos el XML
    xml = '%s.xml' % vmName
    f = open('cdps-vm-base-p1.xml', 'r', 0)
    out = open('%s' % xml, 'w')

    for line in f:
        if '<name' in line:
            out.write('<name>%s</name>\n' % vmName)
        elif '<uuid' in line:
            out.write('<uuid>%s</uuid>\n' % uuid)
        elif '<mac' in line:
            out.write("<mac address='%s'/>\n" % mac)
        elif '<source file' in line:
            out.write("<source file='%s' />\n" % pwd)
        else:
            out.write(line)

    f.close()
    out.close()

    # Se crea la maquina virtual
    print 'Creando la vm...'
    call('sudo virsh create %s' % xml, shell=True)

    # Sacamos la IP
    ip = subprocess.check_output("sudo virsh domifaddr %s | grep ipv4 | awk '{print $4}' | cut -d '/' -f 1" % vmName,
                                 shell=True)

    print 'VM %s configurada @  %s' % (vmName, ip)
