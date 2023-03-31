# 'Who is on Screen' project [🇬🇧]

'Who is on screen' is a project conceived under the scope of a final specialization degree project, which main goal is
to familiarize the student with the development of a complete data science pipeline, from data collection up to the
deployment of ML models. This repository is not intended to work as a productive solution, but rather a concept proof of
how different technologies could be applied to solve a specific kind of problem. You can access the final paper with all
the details around the problematic and the decisions made [here 🇪🇸](/docs/pdfs/Sabalain_TFI.pdf).

## General Introduction

In general terms, the goal is to develop a solution that, through the use of facial recognition, maps the actors that
appear on the screen for each minute of a specific film material during that interval. The aim is to build a solution
that is easy to scale, given that facial recognition through machine learning often requires a high amount of resources.

The ultimate goal of this work is to lay the technological foundation on which the scientific and research analysis will
be developed. Prioritizing familiarity with the tools (most of which were previously unknown) and fine-tuning the system.

## Infrastructure

This repository allows for the installation of a virtualized development environment based on the Docker solution. The
advantages of using these tools mainly lie in the possibility of developing everything once and then implementing it in
the desired environment (productive or not).

The containers that make up our environment will be initialized by running a [docker-compose](docker-compose.yml), and
will be:

* **docs**: *nginx* image that creates the initial [repository menu](localhost).
* **MySQL**: Database to be used throughout the project.
* **phpmyadmin**: Web service that will allow us to access a [MySQL DBMS](http://localhost:8078/).
* **Postgres Airflow**: Database that will store Airflow metadata.
* **Apache Airflow**: Workflow management platform through which we will run the different processes of the work. It
  consists of 3 containers:
  * [The Web Server](http://localhost:8079/), which we will access to control the execution of the DAGs.
  * The scheduler, which works as the backend of the first.
  * The initialization container, which is responsible for the correct mounting of the service.
* **Apache Spark**: Spark management platform, composed of:
  * [The master node](http://localhost:8080/), through which we will access a UI that will allow us to monitor the
    applications to be run.
  * Two worker nodes.
* **Jupyter notebooks**: It will allow us to access a [web service](http://localhost:8888/) where we can run Jupyter
  notebooks, even connecting to the Spark module.
* **Selenium**: Needed in order to perform repetetive web-scrapping tasks. It has a [UI](http://localhost:5900/) that
  can be accessed to monitor on-going tasks.

## Setting up the environment

This first part of the work begins with the installation and setup of the environment.

### Environment installation

The necessary steps for the correct installation of the environment are:

1. Docker installation:
    - a. For Windows, the use of [WSL2](https://docs.docker.com/desktop/windows/wsl/) is recommended.
    - b. In case of having OSX, you can follow [this guide](https://stackoverflow.com/questions/40523307/brew-install-docker-does-not-include-docker-engine/43365425#43365425)
    - c. For Linux, the installation will be via [package manager](https://docs.docker.com/engine/install/ubuntu/)

2. Clone the repo: Once Docker is installed, you must clone the repository through the following command:

    ```shell
    git clone https://github.com/ssabalain/who_is_on_screen.git
    cd who_is_on_screen
    ```

### Initializing the environment

Now that everything is installed, we will proceed to initialize the environment. If it is the first time, we will
execute the following command:

    ./control-env.sh initial_setup

For subsequent initializations, just run:

    ./control-env.sh start

When we want to stop all the containers:

    ./control-env.sh stop

The ShellScript file "[contron-env.sh](control-env.sh)" will allow us to operate our environment easily, from
initialization to shutdown.
It is recommended to consult the different options available with this command to better understand its scope.

### Running DAGs on Airflow

Once the environment is up, we will go to the [Airflow Web server](http://localhost:8079/) .

There we will find different DAGs that will be divided into two main groups:

  - Those with prefix "1_", which refer to the execution of Python scripts to perform operations on the MySQL database
  - Those with prefix "2_", which refer to the execution of applications on the mounted Spark cluster.

To initialize any of these DAGs, just turn them on by clicking the available ON/OFF button.

### Accessing data via phpMyAdmin

With the tables created, it will be possible to access them and perform different types of queries through the
[phpMyAdmin platform](http://localhost:8078/).

### Executing Spark Applications

In this phase, we will verify that it is possible to access the Spark cluster set up in the environment through other
services hosted in containers different from the Spark one. Achieving this presupposes overcoming a relatively complex
technical barrier and completing the development ecosystem setup.

#### Running Spark Applications from Airflow

To run a Spark Application from Airflow, it is first necessary to configure a "spark" type connection in the
orchestration platform, pointing to the Spark cluster to be used.

Secondly, the actual executions of a Spark App from Airflow are performed using the "SparkSubmitOperator", an operator
from the "airflow_providers" package. The DAG "2___reading_imdb_datasets" serves as an example of both the connection
configuration and the use of the operator. This DAG simply counts the number of records in a specific .tsv file.

#### Running Spark Applications from Jupyter Notebooks

To run a Spark application from a Jupyter Notebook, it is necessary to import the "SparkSession" function from the
pyspark.sql library, which will allow us to configure the parameters that will enable the connection with the Spark
Cluster.

The notebook [0_connecting_to_spark.ipynb](src/jupyter_notebooks/0_connecting_to_spark.ipynb) shows in detail how to
establish a connection and execute a simple Spark command.
