///! Модуль установщика Open vAIR
///!
///! Здесь находится основная логика установки утилиты
///!
///! See also [`OpenvairInstaller`]
use std::{path::Path, process::Command, rc::Rc, thread, time::Duration};

use anyhow::anyhow;
use bcrypt::DEFAULT_COST;
use log::info;
use serde_valid::Validate;

use crate::openvair_manager::{
    cmd_runner::CommandRunner,
    docker::{
        installer::DockerInstaller,
        provider::{DockerProvider, DockerRunConfig},
    },
    files::FilesProvider,
    node_exporter::installer::NodeExporterInstaller,
    openvair_installer::config::OpenvairInstallerConfig,
    os_services::ServiceProvider,
    pkg_management::distro::PackageProvider,
    project_config::OpenvairProjectConfig,
    prometheus::installer::PrometheusInstaller,
    python::provider::PythonProvider,
};

pub struct OpenvairInstaller<'a> {
    pub installer_config: OpenvairInstallerConfig,
    pub project_config: OpenvairProjectConfig,
    pkg: Rc<dyn PackageProvider>,
    runner: Rc<CommandRunner>,
    files: Rc<FilesProvider>,
    docker_installer: &'a dyn DockerInstaller,
    docker: &'a DockerProvider,
    prometheus_installer: Rc<dyn PrometheusInstaller>,
    node_exporter_installer: Rc<dyn NodeExporterInstaller>,
    python: &'a PythonProvider,
    services: Rc<dyn ServiceProvider>,
}

impl<'a> OpenvairInstaller<'a> {
    pub fn new(
        installer_config: OpenvairInstallerConfig,
        project_config: OpenvairProjectConfig,
        pkg: Rc<dyn PackageProvider>,
        runner: Rc<CommandRunner>,
        files: Rc<FilesProvider>,
        docker_installer: &'a dyn DockerInstaller,
        docker: &'a DockerProvider,
        prometheus_installer: Rc<dyn PrometheusInstaller>,
        node_exporter_installer: Rc<dyn NodeExporterInstaller>,
        python: &'a PythonProvider,
        services: Rc<dyn ServiceProvider>,
    ) -> Self {
        Self {
            installer_config,
            project_config,
            pkg,
            runner,
            docker_installer,
            docker,
            node_exporter_installer,
            python,
            services,
            files,
            prometheus_installer,
        }
    }

    pub fn install_openvair(&mut self) -> anyhow::Result<()> {
        info!("starting openvair installation");

        self.project_config.validate()?;
        self.create_jwt_secret()?;
        self.get_os_type()?;

        self.prepare_system_packages()?;
        self.make_and_configure_venv()?;
        self.prepare_python_packages()?;

        self.set_repo_owner()?;
        self.docker_installer.install_docker()?;
        self.setup_postgres_container()?;
        self.setup_rabbitmq_container()?;

        self.setup_snmp()?;
        self.make_migrations()?;
        self.generate_certificate()?;

        self.install_prometheus()?;
        self.install_node_exporter()?;

        self.setup_novnc()?;
        self.setup_restic()?;
        self.process_services()?;

        self.clear_home_dir()?;
        self.install_uv()?;
        self.install_documentation()?;
        self.restart_web_app_service()?;
        info!("installation finished");

        Ok(())
    }

    fn create_jwt_secret(&mut self) -> anyhow::Result<()> {
        info!("creating jwt secret");
        let secret = self
            .runner
            .run(Command::new("openssl").args(["rand", "-hex", "32"]))
            .output;
        self.project_config.jwt.secret = Some(secret.to_string());
        self.save_project_config()?;

        info!("jwt secret created successfully");
        Ok(())
    }

    fn get_os_type(&mut self) -> anyhow::Result<()> {
        info!("reading os type");
        let os_type = self
            .runner
            .pipe(
                Command::new("lsb_release").arg("-i"),
                Command::new("cut").args(["-f", "2-"]),
            )
            .output
            .to_lowercase();

        info!("got os type: {}", &os_type);
        self.project_config.os_data.os_type = os_type;
        self.save_project_config()?;
        Ok(())
    }

    fn prepare_system_packages(&self) -> anyhow::Result<()> {
        let pkgs = [
            // Python things
            "python3-venv",
            "python3-pip",
            "libpq-dev",
            "python3-websockify",
            // Libvirt requirements
            "qemu-kvm",
            "libvirt-daemon-system",
            "libvirt-clients",
            "bridge-utils",
            "libvirt-dev",
            "python3-dev",
            "build-essential",
            // Storage things
            "nfs-common",
            "xfsprogs",
            // ---
            "openvswitch-switch",
            "multipath-tools",
            "open-iscsi",
        ];

        for p in pkgs {
            self.pkg.try_install(p)?;
        }

        Ok(())
    }

    fn make_and_configure_venv(&self) -> anyhow::Result<()> {
        info!("making venv");
        self.runner.try_run(
            Command::new("python3")
                .args([
                    "-m",
                    "venv",
                    &format!("{}/venv", self.installer_config.project_path),
                ])
                .current_dir(&self.installer_config.project_path),
        )?;

        info!("exporting pythonpath");
        self.files.append(
            &format!(
                "'export PYTHONPATH={}:",
                &self.installer_config.project_path
            ),
            &format!("{}/venv/bin/activate", &self.installer_config.project_path),
        )?;
        Ok(())
    }

    fn prepare_python_packages(&self) -> anyhow::Result<()> {
        info!("installing misc python packages");
        let python_pkgs = ["libvirt-python", "wheel"];
        for p in python_pkgs {
            self.python.try_install(p)?;
        }

        info!("installing requirements");
        self.python.try_install_requirements(&format!(
            "{}/requirements.txt",
            self.installer_config.project_path
        ))?;
        info!("install precommit");
        self.runner.try_run(
            Command::new(format!(
                "{}/venv/bin/pre-commit",
                self.installer_config.project_path
            ))
            .arg("install"),
        )?;
        Ok(())
    }

    fn set_repo_owner(&self) -> anyhow::Result<()> {
        info!("changing owner of the repo");
        self.files.chown(
            &format!(
                "{}:{}",
                self.installer_config.user, self.installer_config.user
            ),
            &[&self.installer_config.project_path],
        )?;
        Ok(())
    }

    fn setup_postgres_container(&self) -> anyhow::Result<()> {
        info!("creating postgresql docker container");
        const PG_CONTAINER_NAME: &str = "postgres";
        const PG_DB_NAME: &str = "openvair";

        let pg_run = DockerRunConfig::new("postgres -c 'listen_addresses=*'")
            .builder()
            .name(PG_CONTAINER_NAME)
            .restart("unless-stopped")
            .env(&[
                format!("POSTGRES_USER={}", self.installer_config.user).as_str(),
                format!("POSTGRES_PASSWORD={}", self.installer_config.user).as_str(),
            ])
            .ports(&format!(
                "{}:{}",
                self.project_config.database.port, self.project_config.database.port
            ))
            .detach(true)
            .build();

        self.docker.try_run(&pg_run)?;
        thread::sleep(Duration::from_secs(5));

        // Create DB
        self.docker.try_exec(
            PG_CONTAINER_NAME,
            &format!(
                "psql -U {} -c 'CREATE DATABASE {};'",
                self.installer_config.user, PG_DB_NAME
            ),
        )?;

        // Setup Permissions
        self.docker.try_exec(
            PG_CONTAINER_NAME,
            &format!(
                "psql -U {} -c 'GRANT ALL PRIVILEGES ON DATABASE {} TO {};'",
                self.installer_config.user, PG_DB_NAME, self.installer_config.user,
            ),
        )?;

        // Setup default user
        let hashed_password =
            bcrypt::hash(&self.project_config.default_user.password, DEFAULT_COST)?;
        self.docker.try_exec(PG_CONTAINER_NAME,
            &format!(
                "psql -U {} -d {} -c \"INSERT INTO USERS (id, username, password) VALUES ('0b677738-34ff-4f9e-b1f6-5962065c0207', '{}', NULL, 't', '{}')\"",
                &self.installer_config.user, PG_DB_NAME, &self.project_config.default_user.login, hashed_password
            )
        )?;

        Ok(())
    }

    fn setup_rabbitmq_container(&self) -> anyhow::Result<()> {
        let rabbitmq_user = self.project_config.rabbitmq.user.as_str();
        let rabbitmq_password = self.project_config.rabbitmq.password.as_str();
        let rabbitmq_host = match self.project_config.rabbitmq.host.as_str() {
            "localhost" => "127.0.0.1",
            addr => addr,
        };
        let rabbitmq_port = self.project_config.rabbitmq.port;

        // TODO this should prooooobably be moved to be a configurable version
        //
        // But for now "it just needs to be"
        let hostname = self.runner.try_run(&mut Command::new("hostname"))?.output;
        let run_cfg = DockerRunConfig::new("rabbitmq:3.11")
            .builder()
            .detach(true)
            .hostname(&hostname)
            .name("rabbit")
            .env(&[
                &format!("RABBITMQ_DEFAULT_USER={rabbitmq_user}"),
                &format!("RABBITMQ_DEFAULT_PASS={rabbitmq_password}"),
            ])
            .ports(&format!("{rabbitmq_host}:{rabbitmq_port}:{rabbitmq_port}"))
            .restart("unless-stopped")
            .build();

        self.docker.try_run(&run_cfg)?;

        Ok(())
    }

    fn setup_snmp(&self) -> anyhow::Result<()> {
        let pkgs = ["snmp", "snmpd"];

        for p in pkgs {
            self.pkg.try_install(p)?;
        }

        info!("appending snmp config");
        const SNMPD_CONF: &str = "/etc/snmp/snmpd.conf";
        if !std::fs::exists(SNMPD_CONF)? {
            anyhow::bail!("{} file does not exist", SNMPD_CONF);
        }

        self.files.append(
            "
view systemonly  included    .1.3.6.1.4.1.54641
rocommunity public default -V systemonly
"
            .trim(),
            SNMPD_CONF,
        )?;
        info!("successfully added lines to {}", SNMPD_CONF);

        Ok(())
    }

    fn make_migrations(&self) -> anyhow::Result<()> {
        info!("running alembic migrations");
        self.runner.try_run(
            Command::new("sudo")
                .args([
                    &format!("{}/venv/bin/python3", self.installer_config.project_path),
                    "-m",
                    "alembic",
                    "-c",
                    &format!("{}/alembic.ini", self.installer_config.project_path),
                    "upgrade",
                    "head",
                ])
                .current_dir(&self.installer_config.project_path),
        )?;

        Ok(())
    }

    fn generate_certificate(&self) -> anyhow::Result<()> {
        const CERT_DURATION_DAYS: u32 = 36500;
        let key_file: &str = &format!("{}/key.pem", self.installer_config.project_path);
        let cert_file: &str = &format!("{}/cert.pem", self.installer_config.project_path);
        let config_file: &str = &format!("{}/openssl.cnf", self.installer_config.project_path);

        if !std::fs::exists(config_file)? {
            anyhow::bail!("configuration file {} not found", config_file);
        }

        info!("configuration file {} found", config_file);

        self.runner.try_run(Command::new("openssl").args([
            "req",
            "-x509",
            "-newkey",
            "rsa:4096",
            "-keyout",
            key_file,
            "-out",
            cert_file,
            "-days",
            &CERT_DURATION_DAYS.to_string(),
            "-nodes",
            "-config",
            config_file,
        ]))?;
        Ok(())
    }

    fn install_prometheus(&self) -> anyhow::Result<()> {
        self.prometheus_installer.install_prometheus()?;
        Ok(())
    }

    fn install_node_exporter(&self) -> anyhow::Result<()> {
        self.node_exporter_installer.install_node_exporter()?;
        Ok(())
    }

    fn setup_novnc(&self) -> anyhow::Result<()> {
        self.runner.try_run(Command::new("git").args([
            "clone",
            "https://github.com/novnc/noVNC.git",
            &format!(
                "{}/{}/libs/noVNC",
                self.installer_config.project_path, self.installer_config.project_name
            ),
        ]))?;

        Ok(())
    }

    fn setup_restic(&self) -> anyhow::Result<()> {
        self.pkg.install("restic");
        self.runner
            .try_run(Command::new("sudo").args(["restic", "self-update"]))?;

        Ok(())
    }

    fn process_services(&self) -> anyhow::Result<()> {
        let files_res = self.runner.try_run(Command::new("sudo").args([
            "find",
            &self.installer_config.project_path,
            "-name",
            "*.service",
        ]))?;
        let files = files_res.output.split_whitespace().collect::<Vec<_>>();

        for file in files {
            let fpath = Path::new(file);
            let fbasename = fpath
                .file_name()
                .ok_or(anyhow!("failed to get basename from path '{}'", file))?
                .to_str()
                .expect("should always convert back to str because came from str");

            self.services.add_service_from_file(file)?;
            self.services.enable_service(fbasename)?;
            self.services.start_service(fbasename)?;
        }

        Ok(())
    }

    fn clear_home_dir(&self) -> anyhow::Result<()> {
        info!("clearing home directory");
        self.files
            .remove_dirs(&[".nvm", ".npm", ".cache", ".config"])?;
        Ok(())
    }

    fn install_uv(&self) -> anyhow::Result<()> {
        info!("installing uv");
        self.runner.try_pipe(
            Command::new("curl").args(["-LsSf", "https://astral.sh/uv/install.sh"]),
            &mut Command::new("sh"),
        )?;
        Ok(())
    }

    fn install_documentation(&self) -> anyhow::Result<()> {
        const DOC_REPO: &str = "https://github.com/Aerodisk/openvair-docs.git";

        info!("installing documentation");

        if std::fs::exists(&self.installer_config.docs_project_path)? {
            info!("dcoumentation repository already exists");
        } else {
            self.runner.try_run(Command::new("git").args([
                "clone",
                DOC_REPO,
                &self.installer_config.docs_project_path,
            ]))?;
        }

        self.runner.try_run(Command::new("bash").arg(format!(
            "{}/install.sh",
            &self.installer_config.docs_project_path
        )))?;

        Ok(())
    }

    fn restart_web_app_service(&self) -> anyhow::Result<()> {
        self.services.restart_service("web-app.service")?;
        Ok(())
    }

    fn save_project_config(&self) -> anyhow::Result<()> {
        self.project_config
            .try_save_file(&self.installer_config.project_config_file)?;
        Ok(())
    }
}
