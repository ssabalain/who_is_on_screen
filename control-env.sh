#!/usr/bin/env bash

function stop {
  echo "Stopping and removing containers..."
  docker-compose --project-name wios down
}

function cleanup {
  echo "Removing volumes..."
  docker-compose --project-name wios down --volumes --rmi all
  echo "Deleting cache folders..."
  rm -rf ./airflow/dags/__pycache__
  rm -rf ./facial_database/jupyter_notebooks/.ipynb_checkpoints
  rm -rf ./facial_database/python_scripts/__pycache__
  echo "Deleting log folders..."
  rm -rf ./airflow/logs
}

function hard_cleanup {
  read -p "HOLD ON THERE, YOU CINEPHILE! You are about to delete the '/datasets' folder and clean some unused stuff from Docker-Desktop.\
  Are you sure you want to continue? [y/n] " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
      echo "Wise choice. Don't forget to check '/control-env.sh' file to know more about this stage."
      exit 1
  fi
  echo "Alright, here we go..."
  echo "Deleting datasets..."
  rm -rf ./facial_database/datasets
  echo "Cleaning Docker-Desktop..."
  docker rm $(docker ps -f status=exited -aq)
  docker rmi $(docker images -f "dangling=true" -q)
  docker volume rm $(docker volume ls -qf dangling=true)

}

function initial_setup {
  echo "Building images from Dockerfiles. If this is running for the first time, it might take up to 10 min...."
  ./docker/build.sh
}

function start {
  echo "Starting up..."
  docker-compose --project-name wios up -d
}

function update {
  echo "Updating docker images ..."
  docker-compose --project-name wios pull
  echo "You probably should restart"
}

function grant_mysql_access {
  echo "Granting root access to MySQL user..."
  bash ./docker/jupyterlab/grant_root_privileges.sh
}

case $1 in
  start )
  start
  grant_mysql_access
    ;;

  initial_setup )
  initial_setup
  start
  grant_mysql_access
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

  logs )
  docker-compose --project-name wios logs -f
    ;;

  * )
  printf "ERROR: Missing command\n  Usage: `basename $0` (start|initial_setup|stop|cleanup|hard_cleanup|logs|update)\n"
  exit 1
    ;;
esac