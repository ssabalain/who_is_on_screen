#!/usr/bin/env bash

function stop {
  echo "Stopping and removing containers"
  docker-compose --project-name wios down
}

function cleanup {
  echo "Removing everything"
  docker-compose --project-name wios down --volumes --rmi all
}

function initial_setup {
  cd ./docker-airflow
  echo "Building docker-airflow-spark image from Dockerfile. If this is running for the first time, it might take up to 10 min...."
  docker build --rm --force-rm -t docker-airflow-spark:1.10.7_3.1.2 .
  cd ..
  $(start)
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
  echo '
  Everything is ready, access your host to learn more (ie: http://localhost/)
  '
}

case $1 in
  start )
  start
  info
    ;;

  initial_setup )
  initial_setup
  info
    ;;

  stop )
  stop
    ;;

  cleanup )
  stop
  cleanup
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
