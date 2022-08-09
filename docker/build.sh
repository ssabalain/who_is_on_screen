#!/bin/bash
#
# -- Build Apache Spark Standalone Cluster Docker Images

function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

eval $(parse_yaml ./docker/build.yml)

# ----------------------------------------------------------------------------------------------------------------------
# -- Variables ---------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

BUILD_DATE="$(date -u +'%Y-%m-%d')"

SHOULD_BUILD_BASE=${build_base}
SHOULD_BUILD_AIRFLOW=${build_airflow}
SHOULD_BUILD_SPARK=${build_spark}
SHOULD_BUILD_JUPYTERLAB=${build_jupyterlab}

AIRFLOW_VERSION=${version_airflow}
PYTHON_VERSION=${version_python}
PYTHON_VERSION_SHORT="${PYTHON_VERSION:0:3}"
SPARK_VERSION=${version_spark}
JUPYTERLAB_VERSION=${version_jupyterlab}

SPARK_VERSION_MAJOR=${SPARK_VERSION:0:1}

if [[ "${SPARK_VERSION_MAJOR}" == "2" ]]
then
  HADOOP_VERSION="2.7"
  SCALA_VERSION="2.11.12"
  SCALA_KERNEL_VERSION="0.6.0"
elif [[ "${SPARK_VERSION_MAJOR}"  == "3" ]]
then
  HADOOP_VERSION="3.2"
  SCALA_VERSION="2.12.10"
  SCALA_KERNEL_VERSION="0.10.9"
else
  exit 1
fi

# ----------------------------------------------------------------------------------------------------------------------
# -- Functions----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

function cleanContainers() {

    container="$(docker ps -a | grep 'jupyterlab' | awk '{print $1}')"
    docker stop "${container}"
    docker rm "${container}"

    container="$(docker ps -a | grep 'spark-worker' -m 1 | awk '{print $1}')"
    while [ -n "${container}" ];
    do
      docker stop "${container}"
      docker rm "${container}"
      container="$(docker ps -a | grep 'spark-worker' -m 1 | awk '{print $1}')"
    done

    container="$(docker ps -a | grep 'spark-master' | awk '{print $1}')"
    docker stop "${container}"
    docker rm "${container}"

    container="$(docker ps -a | grep 'spark-base' | awk '{print $1}')"
    docker stop "${container}"
    docker rm "${container}"

    container="$(docker ps -a | grep 'base' | awk '{print $1}')"
    docker stop "${container}"
    docker rm "${container}"

    container="$(docker ps -a | grep 'airflow-spark' | awk '{print $1}')"
    docker stop "${container}"
    docker rm "${container}"

}

function cleanImages() {

    if [[ "${SHOULD_BUILD_AIRFLOW}" == "true" ]]
    then
      docker rmi -f "$(docker images | grep -m 1 'airflow-spark' | awk '{print $3}')"
    fi

    if [[ "${SHOULD_BUILD_JUPYTERLAB}" == "true" ]]
    then
      docker rmi -f "$(docker images | grep -m 1 'jupyterlab' | awk '{print $3}')"
    fi

    if [[ "${SHOULD_BUILD_SPARK}" == "true" ]]
    then
      docker rmi -f "$(docker images | grep -m 1 'spark-worker' | awk '{print $3}')"
      docker rmi -f "$(docker images | grep -m 1 'spark-master' | awk '{print $3}')"
      docker rmi -f "$(docker images | grep -m 1 'spark-base' | awk '{print $3}')"
    fi

    if [[ "${SHOULD_BUILD_BASE}" == "true" ]]
    then
      docker rmi -f "$(docker images | grep -m 1 'base' | awk '{print $3}')"
    fi

}

function cleanVolume() {
  docker volume rm "hadoop-distributed-file-system"
}

function buildImages() {

  if [[ "${SHOULD_BUILD_BASE}" == "true" ]]
  then
    docker build \
      --build-arg build_date="${BUILD_DATE}" \
      --build-arg PYTHON_VERSION="${PYTHON_VERSION}" \
      --build-arg PYTHON_VERSION_SHORT="${PYTHON_VERSION_SHORT}" \
      --build-arg scala_version="${SCALA_VERSION}" \
      -f ./docker/base/Dockerfile \
      -t base:latest .
  fi

  if [[ "${SHOULD_BUILD_AIRFLOW}" == "true" ]]
  then
    docker build \
      --build-arg build_date="${BUILD_DATE}" \
      --build-arg AIRFLOW_VERSION="${AIRFLOW_VERSION}" \
      --build-arg PYTHON_VERSION="${PYTHON_VERSION}" \
      --build-arg SCALA_VERSION="${SCALA_VERSION::4}" \
      --build-arg HADOOP_VERSION="${HADOOP_VERSION}" \
      --build-arg SPARK_VERSION="${SPARK_VERSION}" \
      -f ./docker/airflow/Dockerfile \
      -t airflow-spark:airflow-${AIRFLOW_VERSION}-spark-${SPARK_VERSION} .
  fi

  if [[ "${SHOULD_BUILD_SPARK}" == "true" ]]
  then

    docker build \
      --build-arg build_date="${BUILD_DATE}" \
      --build-arg spark_version="${SPARK_VERSION}" \
      --build-arg hadoop_version="${HADOOP_VERSION}" \
      -f ./docker/spark-base/Dockerfile \
      -t spark-base:${SPARK_VERSION} .

    docker build \
      --build-arg build_date="${BUILD_DATE}" \
      --build-arg spark_version="${SPARK_VERSION}" \
      -f ./docker/spark-master/Dockerfile \
      -t spark-master:${SPARK_VERSION} .

    docker build \
      --build-arg build_date="${BUILD_DATE}" \
      --build-arg spark_version="${SPARK_VERSION}" \
      -f ./docker/spark-worker/Dockerfile \
      -t spark-worker:${SPARK_VERSION} .

  fi

  if [[ "${SHOULD_BUILD_JUPYTERLAB}" == "true" ]]
  then
    docker build \
      --build-arg build_date="${BUILD_DATE}" \
      --build-arg scala_version="${SCALA_VERSION}" \
      --build-arg spark_version="${SPARK_VERSION}" \
      --build-arg jupyterlab_version="${JUPYTERLAB_VERSION}" \
      --build-arg scala_kernel_version="${SCALA_KERNEL_VERSION}" \
      -f ./docker/jupyterlab/Dockerfile \
      -t jupyterlab:${JUPYTERLAB_VERSION}-spark-${SPARK_VERSION} .
  fi

}

# ----------------------------------------------------------------------------------------------------------------------
# -- Main --------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

cleanContainers;
cleanImages;
cleanVolume;
buildImages;