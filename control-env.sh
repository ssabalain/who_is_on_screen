#!/usr/bin/env bash

function stop {
  echo "Stopping and removing containers"
  docker-compose --project-name wios down
}

function cleanup {
  echo "Removing volumes"
  docker-compose --project-name wios down --volumes --rmi all
  echo "Deleting cache folders"
  rm -rf ./airflow/dags/__pycache__
  rm -rf ./facial_database/jupyter_notebooks/.ipynb_checkpoints
  rm -rf ./facial_database/python_scripts/__pycache__
  echo "Deleting log folders"
  rm -rf ./airflow/logs
}

function hard_cleanup {
  echo "Deleting datasets"
  rm -rf ./facial_database/datasets
}

function initial_setup {
  cd ./docker-airflow
  echo "Building airflow-spark image from Dockerfile. If this is running for the first time, it might take up to 10 min...."
  docker build --rm --force-rm --no-cache -t airflow-spark .
  cd ..
}

function start {
  echo "Starting up"
  docker-compose --project-name wios up -d
}

function update {
  echo "Updating docker images ..."
  docker-compose --project-name wios pull
  echo "You probably should restart"
}

function token {
  echo 'Your TOKEN for Jupyter Notebook is:'
  SERVER=$(docker exec -it jupyter jupyter notebook list)
  echo "${SERVER}" | grep 'token' | sed -E 's/^.*=([a-z0-9]+).*$/\1/'
}

function info {
  echo 'Everything is ready, access your host to learn more (ie: http://localhost/)'
}

case $1 in
  start )
  start
  info
    ;;

  initial_setup )
  initial_setup
  start
  info
    ;;

  stop )
  stop
    ;;

  cleanup )
  stop
  cleanup
    ;;

  hard_cleanup )
  stop
  cleanup
  hard_cleanup
    ;;

  update )
  update
    ;;

  token )
  token
    ;;

  logs )
  docker-compose --project-name wios logs -f
    ;;

  * )
  printf "ERROR: Missing command\n  Usage: `basename $0` (start|initial_setup|stop|cleanup|token|logs|update)\n"
  exit 1
    ;;
esac
