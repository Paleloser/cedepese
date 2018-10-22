import os
import sys

#Instalacion de apache con todos sus extras para el correcto funcionamiento
os.system("sudo apt-get install apache2")
os.system("sudo apt-get install lynx")
os.system("sudo apt-get install wget")
os.system("sudo apt-get install curl")
os.system("sudo cp /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/dominio1.conf")
os.system("sudo chmod 777 /etc/apache2/sites-available/dominio1.conf")

#Anadir ServerName dominio1.cdps y ServerAlias www.dominio1.cdps
f1 = open("/etc/apache2/sites-available/dominio1.conf", "w")
for line in f1:
        if "DocumentRoot /var/www/dom1" in line:
        		f1.write(line)
                f1.write("ServerName dominio1.cdps\nServerAlias www.dominio1.cdps\n")
        else:
                f1.write(line)
f1.close()

#Recarga de apache con los cambios realizados
os.system("sudo a2ensite dominio1.conf")
os.system("sudo apache2 reload")

#Mismo proceso para la segunda pagina web
fileDom1 = open("/etc/apache2/sites-available/dominio1.conf", 'r') 
fileDom2 = open("/etc/apache2/sites-available/dominio2.conf", 'w') 
for line in fileDom1:
   if "ServerName dominio1.cdps" in line :
       fileDom2.write("ServerName dominio2.cdps \n")
   elif "ServerAlias www.dominio1.cdps" in line :
       fileDom2.write("ServerAlias www.dominio2.cdps \n")
   else:
      fileDom2.write(line)
fileDom1.close()
fileDom2.close()

#Recarga de apache con los cambios realizados
os.system("sudo a2ensite dominio2.conf")
os.system("sudo service apache2 reload")