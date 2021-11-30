# Proyecto 'Who is on Screen?' [🇪s]

## Informacion de la entrega
* Autor: Santiago Sabalain
* Materia: Seminario Intensivo de Topicos avanzados en Datos Complejos
* Comision: C2020
* Universidad: Instituto Tecnologico de Buenos Aires (ITBA)

## Acerca del trabajo

He decido utilizar al trabajo del seminario como puntapié inicial de la parte "tecnica" de mi trabajo final de la especializacion. Lo que refiere a la descripcion del problema y la hipotesis planteada pueden ser visualizadas en el [trabajo realizado en el taller de la especializacion](docs/pdfs/Sabalain_Taller_TFI.pdf).

En lineas generales, se busca desarrollar una solucion que permita, mediante el uso de reconocimiento facial, mapear para cada minuto de un determinado material filmografico los actores que aparecen en pantalla en dicho intervalo. Se busca construir una solucion que sea facil de escalar, dado que el reconocimiento facial via aprendizaje automatico suele demandar una alta cantidad de recursos.

En lo que respecta al scope de este trabajo de seminario, el mismo se dividirá en dos fases:
* [Fase 1: Puesta en marcha del ambiente y carga de datos en MySQL](#fase-1:-puesta-en-marcha-del-ambiente-y-carga-de-datos-en-mysql).
* [Fase 2: Lectura de MySQL via Spark](#fase-2:-lectura-de-mysql-via-spark).

El objetivo final de este trabajo es asentar la base tecnológica sobre la cual se desarrollará posteriormente el analisis de índole cientifico y de investigación. Se prioriza la familiarizacion con las herramientas (la mayoría desconocidas anteriormente) y la puesta a punto del sistema, relegando la obtención de resultados con significado para futuras iteraciones.

## Infraestructura

El presente repositorio permite la instalacion de un ambiente de desarrollo virtualizado mediante el conjunto de herramientas Docker. Las ventajas de utilizar estas herramientas radican principalmente en la posibilidad de desarrollar todo una única vez y luego deployear en el ambiente (productivo o no) que se desee.

Los contenedores que componen a nuestro ambiente serán inicializados mediante la ejecución de un [docker-compose](docker-compose.yml), y serán:
* **docs**: Imagen de *nginx* que crea el [menú inicial del repo](localhost).
* **MySQL**: Base de datos a utilizar a lo largo del proyecto.
* **phpmyadmin**: Web service que nos permitirá accede a un [DBMS de MySQL](http://localhost:8080/).
* **Postgres Airflow**: Base de datos sobre la cual se apoyará airflow.
* **Apache Airflow**: [Plataforma de maneja de Worflows](http://localhost:9090/) mediante la cual ejecutaremos los distintos procesos del trabajo.

## Desarrollo

### Fase 1: Puesta en marcha del ambiente y carga de datos en MySQL

Esta primera parte del trabajo comienza con la instalación y puesta a punto del ambiente, y culmina con la carga de datos de IMDB a MySQL.

#### Instalacion del ambiente

A continuacion se encuentran los pasos necesarios para la correcta instalación del ambiente:

1. Instalacion de docker:
    a. Para Windows se recomienda el uso de [WSL2](https://docs.docker.com/desktop/windows/wsl/).
    b. En caso de contar con OSX, se puede seguir [esta guía](https://stackoverflow.com/questions/40523307/brew-install-docker-does-not-include-docker-engine/43365425#43365425)
    c. Para Linux, la instalacion será via [manejador de paquetes](https://docs.docker.com/engine/install/ubuntu/)

2. Clonado del repo: Una vez instalado Docker, se debera clonar el repositorio a traves del siguiente comando:

    ```shell
    git clone https://github.com/ssabalain/who_is_on_screen.git
    cd who_is_on_screen
    ```

#### Inicializando el ambiente

Ya con todo instalado, inicializamos el ambiente utilizando el siguiente comando:

    ./control-env.sh start

El archivo ShellScript "[contron-env.sh](control-env.sh)" nos permitirá operar nuestro ambiente de manera sencilla, desde su inicializacion a su posterior apagado.

#### Ejecutando el DAG "initial-database-setup"

Una vez se encuentre levantado el ambiente, nos dirigiremos al [Web server de Airflow](http://localhost:9090/). 

Allí encontraremos un DAG llamado "[initial_database_setup_DAG](airflow/dags/initial_database_setup_dag.py)". El mismo se compone de un Bash Operator que actualiza el servicio PIP del container de Airflow, y luego un Python Operator que ejecuta el script "[initial_database_setup.py](facial_database/python_scripts/initial_database_setup.py)".

Este ultimo script será el encargdo de realizar los siguientes pasos:

1. Descarga de los [datasets publicos de IMDB](https://datasets.imdbws.com/) en el filesystem del repositorio (en caso de que no existan).
2. Creacion de las tablas SQL para almacenar los datasets.
3. Carga de los datos en SQL via proceso Batch (a modo de no sobrecargar la memoria del contenedor).

Para inicializar este DAG hace falta tan solo "encenderlo", clickeando el boton ON/OFF disponible.

El proceso de carga puede demorar ya que se trata de datasets pesados.

#### Accediendo a los datos via phpMyAdmin

Ya con las tablas creadas, será posible acceder a las mismas y realizar consultas de distinto tipo a través de la plataforma [phpMyAdmin](http://localhost:8080/).

### Fase 2: Lectura de MySQL via Spark

(WIP)
En esta fase se buscará acceder a los datos almacenados en la base MySQL mediante el motor Spark. Se analizarán dichos datos y se creará la estrucura de tablas necesarias para obtener una "base de datos facial", asi como tambien se llenaran dichas tablas con los actores abarcados en el scope del trabajo (peliculas de Christopher Nolan).
