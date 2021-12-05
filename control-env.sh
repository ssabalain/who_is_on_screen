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
  echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
  docker-compose --project-name wios up airflow-init
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

  logs )
  docker-compose --project-name wios logs -f
    ;;

  * )
  printf "ERROR: Missing command\n  Usage: `basename $0` (start|initial_setup|stop|cleanup|logs|update)\n"
  exit 1
    ;;
esac
