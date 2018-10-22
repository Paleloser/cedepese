import os

# Creacion de los directorios de almacenamiento de las paginas web
os.system("sudo mkdir /var/www/dom1")
os.system("sudo mkdir /var/www/dom2")
os.system("sudo chmod 777 /var/www/dom1")
os.system("sudo chmod 777 /var/www/dom2")

# Creacion del primer archivo index.html para el primer servidor

f1 = open("/var/www/dom1/index.html", "w")
f1.write("//Fichero index.html en dom1\n<html>\n<h1>Primer Servidor</h1>\n</html>")
f1.close()

# Creacion del segundo archivo index.html para el segundo servidor basandonos en el primero
fileDom1 = open("/var/www/dom1/index.html", 'r') 
fileDom2 = open("/var/www/dom2/index.html", 'w')

for line in fileDom1:
    if "index.html en dom1" in line:
        fileDom2.write("//Fichero index.html en dom2 \n")
    elif "<h1>Primer Servidor</h1>" in line:
        fileDom2.write("<h1>Segundo Servidor</h1> \n")
    else:
        fileDom2.write(line)

fileDom1.close()
fileDom2.close()
