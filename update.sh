#!/bin/bash

USER=aero
OS=$(cat /etc/issue)
ARCH=$(arch)

# Project settings
PROJECT_NAME=openvair
USER_PATH=/opt/$USER
PROJECT_PATH="${USER_PATH}/${PROJECT_NAME}"
DEPENDENCIES_FILE="${PROJECT_PATH}/third_party_requirements.txt"

# Color settings
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

#===================== GIT MANAGER =================
# Проверка наличия утилиты jq
if ! command -v jq &> /dev/null; then
    echo "Утилита jq не установлена. Установите ее для работы скрипта."
    exit 1
fi

# Установите переменные для репозитория и API GitHub
REPO_OWNER="OWNER_NAME"
REPO_NAME="REPO_NAME"
API_URL="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/branches"

# Получение списка веток с помощью API GitHub
branches=$(curl -s "$API_URL")
version_branches=()

# Функция для проверки соответствия имени ветки маске x.x.x
function is_version_branch {
    [[ $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
}

# Функция для обновления миграций alembic
update_migrations(){
  message="FAILURE IN UPDATING ALEMBIC MIGRATIONS"
  sudo alembic upgrade head || { show_allert_message "$message"; return; }
  printf ">>>>>> ${GREEN}SUCCESSFULLY UPDATED ALEMBIC MIGRATIONS${NC}\n"
}

while IFS= read -r branch; do
    if is_version_branch "$branch"; then
        version_branches+=("$branch")
    fi
done < <(echo "$branches" | jq -r '.[].name')

# Подтягиваем новые ветки, если есть
git pull

# Вывод списка подходящих имен веток
echo "Доступные версии для обновления:"

select branch in "${version_branches[@]}"; do
    if [ -n "$branch" ]; then
        echo "Вы выбрали ветку: $branch"
        git checkout "$branch"
        echo "Применение миграций Alembic для новой ветки: $branch"
        update_migrations
        break
    else
        echo "Неверный выбор. Пожалуйста, выберите номер ветки из списка."
    fi
done

show_allert_message() {
  local message=$1
  
  printf ">>>>>> ${RED}$message${NC}\n"
  error_messages+=("${RED}ERROR:${NC} $message")
}

# Go to home dir of new user
go_to_home_dir(){
  message="FAILURE IN GOING TO HOME DIR"
  cd $USER_PATH || { show_allert_message "$message"; return; }
  printf ">>>>>> ${GREEN}SUCCESSFULLY WENT TO HOME DIR${NC}\n"
}

# ========= FUNCTIONS FOR DAEMONS =========

add_service(){
  message="FAILURE IN ADDING SERVICE ${1} TO SYSTEMD/SYSTEM"
  sudo cp "$1" /etc/systemd/system/ || { show_allert_message "$message"; return; }
  printf ">>>>>> ${GREEN}SUCCESSFULLY ADDED SERVICE ${1} TO SYSTEMD/SYSTEM${NC}\n"
}

enable_service(){
  message="FAILURE IN ENABLING SERVICE ${1}"
  sudo systemctl enable "$1" || { show_allert_message "$message"; return; }
  printf ">>>>>> ${GREEN}SUCCESSFULLY ENABLED SERVICE ${1}${NC}\n"
}

start_service(){
  message="FAILURE IN STARTING SERVICE ${1}"
  sudo systemctl start "$1" || { show_allert_message "$message"; return; }
  printf ">>>>>> ${GREEN}SUCCESSFULLY STARTED SERVICE ${1}${NC}\n"
}

restart_service(){
  message="FAILURE IN RESTARTING SERVICE ${1}"
  sudo systemctl restart "$1" || { show_allert_message "$message"; return; }
  printf ">>>>>> ${GREEN}SUCCESSFULLY RESTARTED SERVICE ${1}${NC}\n"
}

# Main script
go_to_home_dir

for file in $(sudo find $PROJECT_PATH/ -name *.service)
do
  add_service "$file"
  enable_service `basename $file`
  restart_service `basename $file`
done
