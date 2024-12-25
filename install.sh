#!/usr/bin/bash

# User settings
USER=aero
OS=$(lsb_release -i | awk '{print tolower($3)}')
ARCH=$(uname -m)
PROJECT_NAME=openvair
USER_PATH=/opt/$USER
PROJECT_PATH="${USER_PATH}/${PROJECT_NAME}"
PROJECT_CONFIG_FILE="$PROJECT_PATH/project_config.toml"
DEPENDENCIES_FILE="${PROJECT_PATH}/third_party_requirements.txt"

# Color settings
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

LOG_FILE="${PROJECT_PATH}/install.log"

log() {
    local log_color="$1"
    local log_message="$2"
    local timestamp="[$(date +'%Y-%m-%d %H:%M:%S')]"

    # show message
    echo -e "${timestamp} ${log_color}${log_message}${NC}"
    # wright into log file
    echo "${timestamp} ${log_message}" >> "$LOG_FILE"
}

stop_script() {
    local error_message="$1"
    if [ -n "$error_message" ]; then
        log $RED "$error_message"
    fi
    echo
    echo "Press any key to exit tmux session"
    read -n 1 -s -r
    exit 1
}

# Function to execute a command
execute() {
    local command="$1"
    local message="$2"

    log $CYAN "Start to execute: $message"
    if eval "$command"; then
        log $GREEN "Successfully executed: $message"
    else
        stop_script "Failure while executing: $message"
    fi
}

check_or_install() {
    local package=$1
    log $CYAN "Installing $package..."
    if ! dpkg -l | grep -q $package; then
        sudo apt-get install -y $package || stop_script "Failed to install $package"
        log $GREEN "$package installed successfully"
    else
        log $GREEN "$package is already installed"
    fi
}

generate_random_secret() {
    openssl rand -hex 32
}

update_config_file() {
    local jwt_secret="$1"

    if ! grep -q "\[jwt\]" "$PROJECT_CONFIG_FILE"; then
        echo "[jwt]" >> "$PROJECT_CONFIG_FILE"
    fi

    if grep -q "secret" "$PROJECT_CONFIG_FILE"; then
        sed -i -E "s|secret\s*=\s*\"[^\"]*\"|secret=\"$jwt_secret\"|" "$PROJECT_CONFIG_FILE"
    else
        sed -i -E "/\[jwt\]/a\secret=\"$jwt_secret\"" "$PROJECT_CONFIG_FILE"
    fi
}

create_jwt_secret() {
    log $CYAN "Starting jwt secret creation"
    local secret
    secret=$(generate_random_secret)
    update_config_file "$secret"
    log $GREEN "JWT secret created successfully"
}

install_tmux_and_start_session() {
    log $CYAN "Checking for tmux installation"
    if ! command -v tmux &> /dev/null; then
        check_or_install "tmux"
    fi

    if [[ -z "$TMUX" ]]; then
        log $CYAN "Starting script in tmux session"
        tmux new-session -d -s install_session "bash $0 tmux"
        tmux attach -t install_session
        exit 0
    fi
}

verify_user_data() {
    # Check user credentials
    log $CYAN "User data verification"

    # Set minimum length constants
    local MIN_LOGIN_LENGTH=4
    local MIN_PASSWORD_LENGTH=4

    # Retrieve user credentials from project_config.toml
    SECTION_LINE=$(grep -n default_user "$PROJECT_CONFIG_FILE" | cut -d ':' -f 1)
    LOGIN_LINE=$(($SECTION_LINE + $(grep -A 2 default_user "$PROJECT_CONFIG_FILE" | grep -n login | cut -d ':' -f 1) - 1))
    PASSWORD_LINE=$(($SECTION_LINE + $(grep -A 2 default_user "$PROJECT_CONFIG_FILE" | grep -n password | cut -d ':' -f 1) - 1))

    LOGIN=$(sed -n "${LOGIN_LINE}p" "$PROJECT_CONFIG_FILE" | awk -F "'" '{print $2}')
    PASSWORD=$(sed -n "${PASSWORD_LINE}p" "$PROJECT_CONFIG_FILE" | awk -F "'" '{print $2}')

    # Validate user login
    if [[ ${#LOGIN} -ge 5 && ${#LOGIN} -le 30 ]]; then
        log $GREEN "User login is valid"
    else
        if [[ ${#LOGIN} -lt $MIN_LOGIN_LENGTH ]]; then
            stop_script "User login is too short. Minimum length is $MIN_LOGIN_LENGTH characters. Current length: ${#LOGIN}"
        else
            stop_script "User login is not valid or not specified. Installation script stopped"
        fi
    fi

    # Validate user password
    if [[ ${#PASSWORD} -ge 5 ]]; then
        log $GREEN "User password is valid"
    else
        if [[ ${#PASSWORD} -lt $MIN_PASSWORD_LENGTH ]]; then
            stop_script "User password is too short. Minimum length is $MIN_PASSWORD_LENGTH characters. Current length: ${#PASSWORD}"
        else
            stop_script "User password is not valid or not specified. Installation script stoped"
        fi
    fi
}

# Generate SSL self-signed certificate
generate_certificate() {
    # Параметры
    local days=36500
    local key_file="$PROJECT_PATH/key.pem"
    local cert_file="$PROJECT_PATH/cert.pem"
    local config_file="$PROJECT_PATH/openssl.cnf"

    # Проверка наличия конфигурационного файла
    if [ ! -f "$config_file" ]; then
        stop_script "Configuration file $config_file not found!"
    fi

    log $GREEN "Configuration file $config_file found"
    
    local command="openssl req -x509 -newkey rsa:4096 -keyout $key_file -out $cert_file -days $days -nodes -config $config_file"
    local message="Generating SSL certificate with key: $key_file and cert: $cert_file"
    
    execute "$command" "$message"
}

# Get OS type
get_os_type() {
    local command="lsb_release -i | cut -f 2- | tr '[:upper:]' '[:lower:]'"
    local message="Getting OS type"
    execute "$command" "$message"
    OS_TYPE=$(eval "$command")
    sed -i "s/os_type = '.*'/os_type = '$OS_TYPE'/" "$PROJECT_CONFIG_FILE"
    log $GREEN "Received OS type: $OS_TYPE"
}

# Go to home dir of new user
go_to_home_dir() {
    local command="cd \"$USER_PATH\""
    local message="Going to home dir: $USER_PATH"
    execute "$command" "$message"
}

# Install necessary packages
install_venv_and_pip() {
    check_or_install "python3-venv"
    check_or_install "python3-pip"
}

# Making venv in repo
make_venv() {
    local command="cd $PROJECT_PATH && python3 -m venv $PROJECT_PATH/venv"
    local message="Making venv"
    execute "$command" "$message"
}

# Change owner of the repo
change_owner() {
    local command="sudo chown -R $USER:$USER $PROJECT_PATH"
    local message="Changing owner of the repo"
    execute "$command" "$message"
}

# Add python path
add_pythonpath_to_activate() {
    local command="echo \"export PYTHONPATH=${PROJECT_PATH}:\" | sudo tee -a $PROJECT_PATH/venv/bin/activate"
    local message="Exporting python path"
    execute "$command" "$message"
}

# Installing libpq-dev
install_libpq_dev(){
    check_or_install "libpq-dev"
}

# Installing python3-websockify
install_python3_websockify(){
    check_or_install "python3-websockify"
}

install_requirements_for_libvirt(){
    check_or_install "qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils libvirt-dev python3-dev build-essential"
}

# Installing storage requirements
install_requirements_for_storages(){
    check_or_install "nfs-common xfsprogs"
}

# Unified function for installing python package
install_python_package() {
    local package_name="$1"
    local message="$2"

    local command="$PROJECT_PATH/venv/bin/python3 -m pip install $package_name"
    execute "$command" "Installing $message"
}

# Install libvirt python
install_libvirt_python() {
    log $CYAN "Installing libvirt-python..."
    local command="$PROJECT_PATH/venv/bin/pip install libvirt-python"
    execute "$command" "Installing libvirt-python"
}

# Installing wheel
install_wheel() {
  install_python_package "wheel" "wheel"
}

# Installing requirements python
install_python_requirements() {
  install_python_package "-r $PROJECT_PATH/requirements.txt" "python requirements"
}

# Installing psycopg
install_psycopg2(){
    install_python_package "psycopg2" "psycopg2"
}

# Installing openvswitch
install_openvswitch(){
  check_or_install "openvswitch-switch"
}

# Installing multipath
install_multipath(){
    check_or_install "multipath-tools"
}

# Функция для определения переменной ARCH
set_arch() {
    log $CYAN "Setting architecture"
    if [ "$ARCH" = "aarch64" ]; then
        PROC="arm64"
        log $GREEN "Architecture set to aarch64"
    else
        PROC="amd64"
        log $GREEN "Architecture set to amd64"
    fi
}

install_docker() {
    local message="Installing Docker"

    # Check if Docker is installed
    if command -v docker &> /dev/null; then
        log $GREEN "Docker already installed"
        return
    fi

    # Устанавливаем необходимые зависимости
    execute "sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common -y" "Installing necessary dependencies for Docker"
    # Добавляем ключ GPG для репозитория Docker
    execute "curl -fsSL https://download.docker.com/linux/$OS_TYPE/gpg | sudo apt-key add -" "Adding GPG key for Docker repository"
    # Добавляем репозиторий Docker
    execute "echo 'deb [arch=$PROC] https://download.docker.com/linux/$OS_TYPE $(lsb_release -cs) stable' | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null" "Adding Docker repository"
    # Обновляем информацию о пакетах и устанавливаем Docker
    execute "sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io -y" "Installing Docker"
}

# PostgreSQL installation
# Set the database name
DATABASE_NAME="openvair"

# Set Docker container name and port number
DOCKER_CONTAINER_NAME="postgres"
DATABASE_PORT=$(awk -F " = " '/\[database\]/{flag=1; next} flag && /port/ {print $2; exit}' "$PROJECT_CONFIG_FILE")

# Run PostgreSQL container in Docker
run_postgres_container() {
    local message="Creating PostgreSQL Docker container"
    local command="sudo docker run \
        --name $DOCKER_CONTAINER_NAME \
        --restart unless-stopped \
        -e POSTGRES_USER=$USER \
        -e POSTGRES_PASSWORD=$USER \
        -p $DATABASE_PORT:$DATABASE_PORT \
        -d postgres \
        -c 'listen_addresses=*'"
    execute "$command" "$message"
    sleep 5
}

# Create database function
create_database() {
    local command="sudo docker exec -it $DOCKER_CONTAINER_NAME psql -U $USER -c 'CREATE DATABASE $DATABASE_NAME;'"
    local message="Creating database $DATABASE_NAME"
    execute "$command" "$message"
}

# Grant privileges function
grant_privileges() {
    local command="sudo docker exec -it $DOCKER_CONTAINER_NAME psql -U $USER -c 'GRANT ALL PRIVILEGES ON DATABASE $DATABASE_NAME TO $USER;'"
    local message="Granting privileges on database $DATABASE_NAME to user $USER"
    execute "$command" "$message"
}

# Function to create RabbitMQ Docker container
create_rabbitmq_container() {
    log $CYAN "Start to create RabbitMQ Docker container..."
    log $CYAN "Fetch RabbitMQ configuration from project_config.toml"
    local section_line=$(awk '/\[rabbitmq\]/{print NR}' "$PROJECT_CONFIG_FILE")
    local rabbitmq_user=$(awk -F "'" -v section_line=$((section_line + 1)) 'NR==section_line {print $2}' "$PROJECT_CONFIG_FILE")
    local rabbitmq_password=$(awk -F "'" -v section_line=$((section_line + 2)) 'NR==section_line {print $2}' "$PROJECT_CONFIG_FILE")
    local rabbitmq_host=$(awk -F "'" -v section_line=$((section_line + 3)) 'NR==section_line {print $2}' "$PROJECT_CONFIG_FILE")
    local rabbitmq_port=$(awk -F " = " -v section_line=$((section_line + 4)) 'NR==section_line {print $2}' "$PROJECT_CONFIG_FILE")
    log $GREEN "RabbitMQ configuration data fetched successfully"

    # Check and adjust RabbitMQ_HOST if it's set to "localhost"
    if [ "$rabbitmq_host" == "localhost" ]; then
        rabbitmq_host="127.0.0.1"
    fi

    # Prepare the docker run command
    local command="sudo docker run -d \
        --hostname $(hostname) \
        --name rabbit \
        -e RABBITMQ_DEFAULT_USER=$rabbitmq_user \
        -e RABBITMQ_DEFAULT_PASS=$rabbitmq_password \
        -p $rabbitmq_host:$rabbitmq_port:$rabbitmq_port \
        --restart unless-stopped rabbitmq:3.11"

    # Execute the command
    execute "$command" "Creating RabbitMQ Docker container"
}

# Install SNMP packages
install_snmp_packages() {
    check_or_install "snmp snmpd"
}

# Configure snmpd.conf file
configure_snmp_conf() {
    log $CYAN "Starting SNMP configuration file setup"
    local SNMPD_CONF="/etc/snmp/snmpd.conf"
    local CONFIG_LINE1="view systemonly  included    .1.3.6.1.4.1.54641"
    local CONFIG_LINE2="rocommunity public default -V systemonly"

    if [ -f "$SNMPD_CONF" ]; then
        echo "$CONFIG_LINE1" | sudo tee -a "$SNMPD_CONF" > /dev/null
        echo "$CONFIG_LINE2" | sudo tee -a "$SNMPD_CONF" > /dev/null
        log $GREEN "LINES SUCCESSFULLY ADDED TO $SNMPD_CONF"
    else
        log $RED "$SNMPD_CONF file does not exist"
        return 1
    fi
}

# Function to make migrations
make_migrations() {
    log $CYAN "Starting alembic migrations..."

    # Navigate to the project path
    if cd "$PROJECT_PATH"; then
        log $GREEN "Successfully changed directory to $PROJECT_PATH"
    else
        log $RED "Failure in changing directory to $PROJECT_PATH for migrations"
        return 1
    fi

    # Run migrations using Alembic
    local migration_command="sudo $PROJECT_PATH/venv/bin/python3 -m alembic -c $PROJECT_PATH/alembic.ini upgrade head"
    execute "$migration_command" "Running Alembic migrations"
}

# ========= FUNCTIONS FOR INSTALLATION BINARIES =========
# Function to download a package
download_package(){
  local url="$1"
  local message="Downloading package from $url"
  execute "curl -LO \"$url\"" "$message"
}

# Function to unzip an archive
unzip_arch(){
  local archive="$1"
  local message="Unzipping archive: $archive"
  execute "sudo tar -xf \"$archive\"" "$message"
}

# Function to navigate to a directory
go_to_dir(){
  local dir="$1"
  local message="Navigating to directory: $dir"
  execute "cd \"$dir\"" "$message"
}

# Function to replace binary files to /usr/local/bin
replace_binary_files_to_local_bin(){
  for arg in "$@"; do
    local message="Replacing $arg to /usr/local/bin"
    execute "sudo mv \"$arg\" /usr/local/bin" "$message"
  done
}

# Function to remove downloaded folder
remove_downloaded_folder(){
  local folder="$1"
  local message="Removing downloaded folder: $folder"
  execute "sudo rm -rf \"$folder\"" "$message"
}

# Function to remove downloaded archive
remove_downloaded_arch(){
  local archive="$1"
  local message="Removing downloaded archive: $archive"
  execute "sudo rm \"$archive\"" "$message"
}

# ========= FUNCTIONS FOR DAEMONS =========
# Function to add a service to systemd/system
add_service(){
  local service_file="$1"
  local message="Adding service $service_file to systemd/system"
  execute "sudo cp \"$service_file\" /etc/systemd/system/" "$message"
  printf ">>>>>> ${GREEN}Successfully added service $service_file to systemd/system${NC}\n"
}

# Function to enable a systemd service
enable_service(){
  local service="$1"
  local message="Enabling service $service"
  execute "sudo systemctl enable \"$service\"" "$message"
  printf ">>>>>> ${GREEN}Successfully enabled service $service${NC}\n"
}

# Function to start a systemd service
start_service(){
  local service="$1"
  local message="Starting service $service"
  execute "sudo systemctl start \"$service\"" "$message"
  printf ">>>>>> ${GREEN}Successfully started service $service${NC}\n"
}

# Function to restart a systemd service
restart_service(){
  local service="$1"
  local message="Restarting service $service"
  execute "sudo systemctl restart \"$service\"" "$message"
  printf ">>>>>> ${GREEN}Successfully restarted service $service${NC}\n"
}

# ========= PROMETHEUS =========
# Function to create Prometheus folders
create_prometheus_folders() {
  local message="Creating Prometheus folders"
  execute "sudo mkdir -p /var/db/prometheus /etc/prometheus" "$message"
}

# Function to replace Prometheus files to /etc/prometheus
replace_prometheus_files_to_etc_prometheus() {
  local message="Replacing Prometheus files to /etc/prometheus"
  execute "sudo mv consoles console_libraries prometheus.yml /etc/prometheus/" "$message"
}

# Function to create Prometheus web-config.yml
create_prometheus_web_config() {
  local message="Creating Prometheus web-config.yml"
  echo 'tls_server_config:
  cert_file: "/etc/prometheus/cert.pem"
  key_file: "/etc/prometheus/key.pem"
' | sudo tee /etc/prometheus/web-config.yml || stop_script "Failure while creating Prometheus web-config.yml"
  printf ">>>>>> ${GREEN}Successfully created web-config.yml${NC}\n"
}

# Copy SSL files to /etc/prometheus/ folder
copy_ssl_files_to_etc_prometheus() {
  local message="Copying SSL files to /etc/prometheus"
  execute "sudo cp $PROJECT_PATH/cert.pem $PROJECT_PATH/key.pem /etc/prometheus/" "${message}"
}

# Function to change owner of Prometheus directories
change_owner_of_the_prometheus_dirs() {
  local message="Changing owner of Prometheus directories"
  sudo chown -R $USER:$USER /etc/prometheus/ /var/db/prometheus || { printf ">>>>>> ${RED}Failure in changing owner of the Prometheus dirs${NC}\n"; return; }
  printf ">>>>>> ${GREEN}Successfully changed owner of the Prometheus dirs${NC}\n"
}

# Function to create Prometheus systemd service
create_prometheus_service() {
  local message="Creating Prometheus systemd service"
  echo '[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
User=aero
Group=aero
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/db/prometheus \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --web.config.file=/etc/prometheus/web-config.yml \
  --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
' | sudo tee /etc/systemd/system/prometheus.service || stop_script "Failure while adding prometheus service to systemd/system"
  printf ">>>>>> ${GREEN}Successfully added service to systemd/system${NC}\n"
}

# Installng prometheus
install_prometheus() {
  local DEPENDENCY="prometheus"
  local VERSION=$(grep "^${DEPENDENCY}==" "${DEPENDENCIES_FILE}" | sed "s/^${DEPENDENCY}==//")
  local PRODUCT="${DEPENDENCY}-${VERSION}.linux-${PROC}"
  local URL="https://github.com/prometheus/prometheus/releases/download/v${VERSION}/${PRODUCT}.tar.gz"
  local downloaded_file="${PRODUCT}.tar.gz"

  go_to_home_dir
  download_package "$URL"
  unzip_arch "$downloaded_file" 
  go_to_dir "$PRODUCT"
  replace_binary_files_to_local_bin "prometheus" "promtool"
  create_prometheus_folders
  replace_prometheus_files_to_etc_prometheus 
  copy_ssl_files_to_etc_prometheus
  create_prometheus_web_config
  change_owner_of_the_prometheus_dirs
  go_to_home_dir
  remove_downloaded_arch "${PRODUCT}.tar.gz"
  remove_downloaded_folder "$PRODUCT"
  create_prometheus_service
  enable_service "prometheus.service"
  start_service "prometheus.service"
}

# ========= NODE_EXPORTER =========
# Function to create Node Exporter systemd service
create_node_exporter_service() {
  local message="Creating Node Exporter systemd service"
  echo '[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
User=aero
Group=aero
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/usr/local/bin/node_exporter \
  --collector.logind

[Install]
WantedBy=multi-user.target
' | sudo tee /etc/systemd/system/node_exporter.service || stop_script "Failure while adding node_exporter service to systemd/systemc"
  printf ">>>>>> ${GREEN}Successfully added service to systemd/system${NC}\n"
}

# Function to add Node Exporter job to Prometheus
add_node_exporter_job_to_prometheus(){
  echo '
  - job_name: "node_exporter"
    static_configs:
      - targets: ["localhost:9100"]
' | sudo tee -a /etc/prometheus/prometheus.yml || stop_script "Failure while adding node_exporter job to prometheus"
  printf ">>>>>> ${GREEN}SUCCESSFULLY ADDED NODE_EXPORTER JOB TO PROMETHEUS${NC}\n"
}

# Function to check Prometheus configuration using promtool
promtool_check() {
  local message="Checking Prometheus configuration"
  execute "promtool check config /etc/prometheus/prometheus.yml" "$message"
}

# Function to restart Prometheus web interface
restart_prometheus_web() {
  local message="Restarting Prometheus web"
  execute "curl -X POST https://localhost:9090/-/reload --insecure" "$message"
}

install_node_exporter() {
  local DEPENDENCY="node_exporter"
  local VERSION=$(grep "^${DEPENDENCY}==" "${DEPENDENCIES_FILE}" | sed "s/^${DEPENDENCY}==//")

  if [ "$ARCH" = "aarch64" ]; then
    local PROC="arm64"
  else
    local PROC="amd64"
  fi

  local PRODUCT="${DEPENDENCY}-${VERSION}.linux-${PROC}"
  local URL="https://github.com/prometheus/node_exporter/releases/download/v${VERSION}/${PRODUCT}.tar.gz"
  local downloaded_file="${PRODUCT}.tar.gz"

  download_package "$URL"
  unzip_arch "$downloaded_file"
  go_to_dir "$PRODUCT"
  replace_binary_files_to_local_bin "node_exporter"

  # Delete downloaded folders
  go_to_home_dir
  remove_downloaded_arch "$downloaded_file"
  remove_downloaded_folder "$PRODUCT"

  create_node_exporter_service
  enable_service "node_exporter.service"
  start_service "node_exporter.service"

  add_node_exporter_job_to_prometheus
  promtool_check
  restart_prometheus_web
}

# Install open-iscsi
install_open_iscsi() {
    local command="yes | sudo apt install open-iscsi"
    local message="Installing open-iscsi"
    execute "$command" "$message" 
}

# Cloning noVNC
clone_novnc() {
    local command="git clone https://github.com/novnc/noVNC.git $PROJECT_PATH/$PROJECT_NAME/libs/noVNC"
    local message="Cloning noVNC"
    execute "$command" "$message"
}

# Install jq
install_jq(){
    local message="Installing jq"
    execute "sudo apt-get install jq -y" "$message"
}

install_restic(){
  local apt_get_command="sudo apt-get install restic"
  local self_update_command="sudo restic self-update" 
  local install_message="Installing restic"
  local update_message="Updating restic"
  execute "$apt_get_command" "$install_message"
  execute "$self_update_command" "$update_message"
}

# ========= Daemons =========
process_services() {
  go_to_home_dir

  # Поиск всех файлов с расширением .service в заданной директории и выполнение команд для каждого из них
  for file in $(sudo find $PROJECT_PATH/ -name *.service); do
    add_service "$file"
    enable_service `basename $file`
    start_service `basename $file`
  done
}

# Clear home directory
clear_home_dir() {
  local message="Clear home directory"
  execute "rm -rf .nvm .npm .cache .config" "$message"
}

# Create hashed password
make_hashed_password() {
  HASHED_PASSWORD=$($PROJECT_PATH/venv/bin/python3 -c """
from passlib import hash
hash = hash.bcrypt.hash('$PASSWORD')
print(hash)
""")
}

# Create default user
create_default_user() {
    local message="Createing default user"
    local command="sudo docker exec -it $DOCKER_CONTAINER_NAME \
        psql -U $USER -d $DATABASE_NAME -c \"INSERT INTO users \
        (id, username, password) \
        VALUES ('6777383c-56c3-44b3-8243-2fd5b819d3c9', '$LOGIN', \
        NULL, 't', '$HASHED_PASSWORD')\""
    execute "$command" "$message"
    sleep 5
}

# ============ Printing the final message =================
# Функция для централизованного вывода текста
print_at_center() {
    local text=$1
    local color=${2:-"GREEN"}
    local padding=$(( (terminal_width - ${#text}) / 2 ))

    case "$color" in
        "RED")
            printf "${RED}%*s%s${NC}\n" "$padding" "" "$text"
            ;;
        *)
            printf "${GREEN}%*s%s${NC}\n" "$padding" "" "$text"
            ;;
    esac
}

# Функция для вывода текста с отступом
print_with_padding() {
    local text=$1
    local padding=$2

    printf "%*s%s\n" "$padding" "" "$text"
}

# Функция для извлечения значения из конфигурационного файла
extract_value_from_config() {
    local key=$1
    grep -A 2 "web_app" "$PROJECT_PATH/project_config.toml" | grep "$key" | cut -d "=" -f2 | tr -d " '"
}

# Основная функция для вывода итогового сообщения
print_final_message() {
    local IP=$(extract_value_from_config "host")
    local PORT=$(extract_value_from_config "port")
    terminal_width=$(tput cols)
    line=$(printf "%*s" "$terminal_width" | tr ' ' '-')

    printf "%s\n" "$line"
    printf "\n"

    print_at_center "SUCCESS: Installation completed without errors!"
    printf "\n%s\n" "$line"
    printf "\n"

    print_at_center "CONGRATULATIONS!"
    printf "\n"
    print_at_center "openvair HAS BEEN INSTALLED"
    printf "\n"

    local api_docs_url="https://${IP}:${PORT}/swagger/"
    local padding_for_main_msg=$(( (terminal_width - ${#api_docs_url}) / 2 ))

    print_with_padding "ADDRESS  https://${IP}:${PORT}" $padding_for_main_msg
    print_with_padding "API-DOCS $api_docs_url" $padding_for_main_msg
    print_with_padding "LOGIN    $LOGIN" $padding_for_main_msg
    print_with_padding "PASSWORD $PASSWORD" $padding_for_main_msg

    printf "\n"
    print_at_center "GOOD LUCK!"
    printf "\n"
    printf "%s\n" "$line"
}

create_default_user() {
    log $CYAN "Creating default user"
    sudo docker exec -it $DOCKER_CONTAINER_NAME psql -U $USER -d $DATABASE_NAME -c "INSERT INTO users VALUES ('0b677738-34ff-4f9e-b1f6-5962065c0207', '$LOGIN', NULL, 't', '$HASHED_PASSWORD')" || stop_script "Failure while adding deafault user"
    log $GREEN "Default user was added successfully"
}

# Run the main installation steps
main() {
    install_tmux_and_start_session
    verify_user_data
    create_jwt_secret
    get_os_type
    go_to_home_dir
    install_venv_and_pip
    make_venv
    add_pythonpath_to_activate
    install_libpq_dev
    install_python3_websockify
    install_requirements_for_libvirt
    install_libvirt_python
    install_requirements_for_storages
    install_wheel
    install_python_requirements
    install_openvswitch
    install_multipath
    change_owner
    set_arch
    install_docker
    run_postgres_container
    create_database
    grant_privileges
    create_rabbitmq_container
    install_snmp_packages
    configure_snmp_conf
    make_migrations
    generate_certificate
    install_prometheus
    install_node_exporter
    install_open_iscsi
    clone_novnc
    install_restic
    process_services
    clear_home_dir
    make_hashed_password
    create_default_user
    restart_service 'web-app.service'
    print_final_message
}

main

# Check if script is running inside the tmux session
if [[ "$1" == "tmux" ]]; then
    # Press any key to exit tmux session
    read -n 1 -s -r -p "Press any key to exit tmux session"
    exit 0
fi
