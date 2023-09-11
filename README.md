# metasearcher

Instalación y uso del proyecto:
-------------------------------
  * Previamente a los pasos descritos a continuación, es necesario tener Doker instalado y en funcionamiento. Es posible que, para su correcta ejecución en dispositivos con Windows, sea necesario ejecutar el comando "bcdedit /set hypervisorlaunchtype auto" y reiniciar. Este comando es revertible de la siguiente forma: "bcdedit /set hypervisorlaunchtype off" y reiniciar también. La instalación de Docker la podeis seguir desde su página web (https://docs.docker.com/).
  * También será necesario tener instalado visual studio. Métodos de instalación disponibles en su página web (https://code.visualstudio.com/download).

Para realizar la instalación del proyecto es necesario descargar 2 extensiones en visual studio: Dev Containters y Docker.
![image](https://user-images.githubusercontent.com/73128028/204043484-3928e8d6-9474-4ba5-933a-203b8fed114c.png)

![image](https://user-images.githubusercontent.com/73128028/204043588-878b765b-5928-45db-8ab3-a720896c3328.png)

Una vez tengamos dichas extensiones, abrimos el código fuente. Si tenemos las extensiones correctamente instaladas y funcionando, se generará una alerta abajo a la derecha que nos sugiere abrir el código en un contenedor:
![image](https://user-images.githubusercontent.com/73128028/204043823-5607f9aa-5f93-4745-8a63-12322d29bac3.png)

Si no fuese así, debería repasarse la instalación. De todas formas, puede intentarse lanzar el proyecto en un contenedor siguiendo los siguientes pasos.
  * Pulsa Ctrl + Shift + P.
  * Selecciona la opción "Reopen and Rebuild in a Container"
  * Se debería generar un container con una base de datos y una maquina virtual con python y las librerías necesarias para ejecutar el código.
  * Escribe en el terminal de la maquina virtual, desde el directorio src el siguiente código
```
python manage.py runserver 0.0.0.0:8080
```
Especial enfasis en que el puerto sea 8080. De otra forma no funcionará.
