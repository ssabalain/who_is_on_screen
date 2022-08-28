# Proyecto 'Who is on Screen?' [🇪🇸]

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
* [Fase 2: Ejecucion de Spark Applications](#fase-2:-ejecucion-de-spark-applications).

El objetivo final de este trabajo es asentar la base tecnológica sobre la cual se desarrollará posteriormente el analisis de índole cientifico y de investigación. Se prioriza la familiarizacion con las herramientas (la mayoría desconocidas anteriormente) y la puesta a punto del sistema, relegando la obtención de resultados con significado para futuras iteraciones.

## Infraestructura

El presente repositorio permite la instalacion de un ambiente de desarrollo virtualizado basado en la solucion Docker. Las ventajas de utilizar estas herramientas radican principalmente en la posibilidad de desarrollar todo una única vez y luego implementar en el ambiente (productivo o no) que se desee.

Los contenedores que componen a nuestro ambiente serán inicializados mediante la ejecución de un [docker-compose](docker-compose.yml), y serán:
* **docs**: Imagen de *nginx* que crea el [menú inicial del repo](localhost).
* **MySQL**: Base de datos a utilizar a lo largo del proyecto.
* **phpmyadmin**: Web service que nos permitirá accede a un [DBMS de MySQL](http://localhost:8078/).
* **Postgres Airflow**: Base de datos que almacenará la metadata de Airflow.
* **Apache Airflow**: Plataforma de manejo de Worflows mediante la cual ejecutaremos los distintos procesos del trabajo. Se compone de 3 containers:
  * [El Web Server](http://localhost:8079/), al cual accederemos para controlar la ejecucion de los DAGs.
  * El scheduler, que funciona como back-end del primero.
  * El container de inicializacion, que se encarga del correcto montaje del servicio.
* **Apache Spark**: Plataforma de manejo de Spark, compuesta por:
  * [El nodo master](http://localhost:8080/), mediante el cual accederemos a una UI que nos permitirá monitorear las applicaciones a ejecutar.
  * Dos nodos workers.
* **Jupyter notebooks**: Nos permitirá acceder a un [web service](http://localhost:8888/) donde podremos ejecutar Jupyter notebooks, inclusive conectandonos al modulo de Spark.

## Fase 1: Puesta en marcha del ambiente y carga de datos en MySQL

Esta primera parte del trabajo comienza con la instalación y puesta a punto del ambiente, y culmina con la carga de datos de IMDB a MySQL.

### Instalacion del ambiente

A continuacion se encuentran los pasos necesarios para la correcta instalación del ambiente:

1. Instalacion de docker:
    - a. Para Windows se recomienda el uso de [WSL2](https://docs.docker.com/desktop/windows/wsl/).
    - b. En caso de contar con OSX, se puede seguir [esta guía](https://stackoverflow.com/questions/40523307/brew-install-docker-does-not-include-docker-engine/43365425#43365425)
    - c. Para Linux, la instalacion será via [manejador de paquetes](https://docs.docker.com/engine/install/ubuntu/)

2. Clonado del repo: Una vez instalado Docker, se debera clonar el repositorio a traves del siguiente comando:

    ```shell
    git clone https://github.com/ssabalain/who_is_on_screen.git
    cd who_is_on_screen
    ```

### Inicializando el ambiente

Ya con todo instalado, procederemos a la inicializacion del ambiente. En caso de tratarse de la primera vez, ejecutaremos el siguiente comando:

    ./control-env.sh initial_setup

Para posteriores inicializaciones, bastará con correr:

    ./control-env.sh start

Cuando se desee finalizar todos los contenedores:

    ./control-env.sh stop

El archivo ShellScript "[contron-env.sh](control-env.sh)" nos permitirá operar nuestro ambiente de manera sencilla, desde su inicializacion a su posterior apagado. Se recomienda consultar las distintas opciones con las que cuenta este comando a modo de comprender mejor su alcance.

### Ejecutando DAGs en Airflow

Una vez se encuentre levantado el ambiente, nos dirigiremos al [Web server de Airflow](http://localhost:8079/).

Allí encontraremos distintos DAGs que se dividirán en dos grandes grupos:
  - Aquellos con prefijo "1_", que refieren a la ejecución de scripts de Python para realizar operaciones sobre la base de datos MySQL
  - Aquellos con prefijo "2_", que refieren a la ejecución de aplicaciones en el cluster de Spark montado (ver [Fase 2](#fase-2:-ejecucion-de-spark-applications))

Para inicializar cualquiera de estos DAGs hace falta tan solo "encenderlos", clickeando el boton ON/OFF disponible.

Dentro del primer grupo de DAGs, encontraremos uno llamado "[1_0_initial_database_setup](airflow/dags/initial_database_setup_dag.py)". El mismo se compone de un Bash Operator que actualiza el servicio PIP del container de Airflow, y luego un Python Operator que ejecuta el script "[initial_database_setup.py](src/python_scripts/initial_database_setup.py)".

Este DAG realiza el proceso completo de ingesta de datos a nuestra base de datos, que consiste en:

1. Descarga de los [datasets publicos de IMDB](https://datasets.imdbws.com/) en el filesystem del repositorio (en caso de que no existan). Este paso puede ser ejecutado de manera aislada utilizando el DAG "[1_1_download_imdb_datasets](airflow/dags/download_imdb_files_dag.py)".
2. Creacion de las tablas SQL para almacenar los datasets. Este paso puede ser ejecutado de manera aislada utilizando el DAG "[1_2_create_mysql_tables](airflow/dags/create_mysql_tables_dag.py)".
3. Carga de los datos en SQL via proceso Batch (a modo de no sobrecargar la memoria del contenedor). Este paso puede ser ejecutado de manera aislada utilizando el DAG "[1_3_load_mysql_tables](airflow/dags/load_mysql_tables_dag.py)".

En caso de necesitar borrar las tablas creadas, se puede ejecutar el DAG "[1_4_drop_mysql_tables](airflow/dags/drop_mysql_tables_dag.py)".

### Accediendo a los datos via phpMyAdmin

Ya con las tablas creadas, será posible acceder a las mismas y realizar consultas de distinto tipo a través de la plataforma [phpMyAdmin](http://localhost:8078/).

## Fase 2: Ejecucion de Spark Applications

En esta fase se buscará corroborar que es posible acceder al cluster de Spark levantado en el ambiente a traves de otros servicios alojados en contenedores diferentes al de Spark. Lograr esto presupone vencer una barrera tecnica relativamente compleja y completa la puesta a punto del ecosistema de desarrollo.

A modo de comprobar la correcta ejecucion

### Ejecutando Spark Applications desde Airflow

Para ejecutar una Spark Application desde Airflow es necesario, en primer lugar, configurar una conexion de tipo "spark" en la plataforma de orquestación, que apunte al Sparl cluster a utilizar.

En segundo lugar, las ejecuciones per se de una Spark App desde Airflow se realiza utilizando el "SparkSubmitOperator", un operador del paquete de "airflow_providers". El DAG "[2___reading_imdb_datasets](airflow/dags/reading_datasets_dag.py)" sirve como ejemplo tanto de la configuracion de la conexion como del uso del operador. Este DAG simplemente cuenta la cantidad de registros en uno de los archivos .tsv descargados anteriormente.

### Ejecutando Spark Applications mediante Jupyter Notebooks

Para ejecutar una Spark Application desde un Jupyter Notebook es necesario importar la funcion "SparkSession" de la libreria pyspark.sql, la cual nos permitirá configurar los parametros que posibilitarán la conexion con el Cluster de Spark.

El notebook [0_connecting_to_spark.ipynb](src/jupyter_notebooks/0_connecting_to_spark.ipynb) muestra de manera detallada como establecer una conexion y ejecutar un simple comando de Spark.