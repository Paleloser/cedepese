import os

# Configuracion de la interfaz de red
os.system('chmod 777 /etc/network/interfaces')
interfaces = open('/etc/network/interfaces', 'r')
interfacesdos = open('/etc/network/interfaces2', 'w')

for line in interfaces:
    if 'source /etc/network/interfaces.d/*.cfg' in line:
        interfacesdos.write('auto eth0\n'
                            'iface eth0 inet static\n'
                            'address 192.168.122.241\n'
                            'nermask 255.255.255.0\n'
                            'gateway 192.168.122.1\n '
                            'dns-nameservers 192.168.122.1')
    else:
        interfacesdos.write(line)

interfaces.close()
interfacesdos.close()

os.system('sudo mv /etc/network/interfaces2 /etc/network/interfaces | chmod 777 /etc/network/interfaces')

# Instalacion de apache con todos sus extras para el correcto funcionamiento
os.system("sudo apt-get install -y apache2")
os.system("sudo apt-get install -y lynx")
os.system("sudo apt-get install -y wget")
os.system("sudo apt-get install -y curl")
os.system("sudo cp /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/dominio1.conf")
os.system("sudo chmod 777 /etc/apache2/sites-available/dominio1.conf")

# Anadir ServerName dominio1.cdps y ServerAlias www.dominio1.cdps
f1 = open("/etc/apache2/sites-available/dominio1.conf", "r")
f2 = open("/etc/apache2/sites-available/dominio1.conf.b", "w+")

for line in f1:
    if "DocumentRoot /var/www/html" in line:
        f2.write('DocumentRoot /var/www/dom1\n')
        f2.write("ServerName dominio1.cdps\nServerAlias www.dominio1.cdps\n")
    else:
        f2.write(line)

f1.close()
f2.close()

os.system('sudo mv /etc/apache2/sites-available/dominio1.conf.b /etc/apache2/sites-available/dominio1.conf')

# Recarga de apache con los cambios realizados
os.system("sudo a2ensite dominio1.conf")
os.system("sudo service apache2 reload")

# Mismo proceso para la segunda pagina web
fileDom1 = open("/etc/apache2/sites-available/dominio1.conf", 'r') 
fileDom2 = open("/etc/apache2/sites-available/dominio2.conf", 'w')

for line in fileDom1:
    if "DocumentRoot /var/www/dom1" in line:
        fileDom2.write('DocumentRoot /var/www/dom2\n')
    elif "ServerName dominio1.cdps" in line :
        fileDom2.write("ServerName dominio2.cdps \n")
    elif "ServerAlias www.dominio1.cdps" in line :
        fileDom2.write("ServerAlias www.dominio2.cdps \n")
    else:
        fileDom2.write(line)

fileDom1.close()
fileDom2.close()

# Recarga de apache con los cambios realizados
os.system("sudo a2ensite dominio2.conf")
os.system("sudo service apache2 reload")
