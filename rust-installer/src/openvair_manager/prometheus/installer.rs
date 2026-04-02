///! Модуль установки Prometheus на различных дистрибутивах
///!
///! See also [`PrometheusInstaller`]
use std::{process::Command, rc::Rc};

use anyhow::anyhow;

use crate::openvair_manager::{
    cmd_runner::CommandRunner,
    files::FilesProvider,
    os_services::{ServiceProvider, SystemdServiceProvider},
    pkg_management::github::{GithubPkgInfo, GithubPkgInstaller, InstallManifest, ManifestRecord},
    python::requirements::PythonRequirements,
};

pub trait PrometheusInstaller {
    fn install_prometheus(&self) -> anyhow::Result<()>;
}

pub struct UbuntuPrometheusInstaller {
    runner: Rc<CommandRunner>,
    files: Rc<FilesProvider>,
    services: Rc<SystemdServiceProvider>,
    git_pkg: Rc<GithubPkgInstaller>,
    config: UbuntuPrometheusInstallerConfig,
}

impl PrometheusInstaller for UbuntuPrometheusInstaller {
    fn install_prometheus(&self) -> anyhow::Result<()> {
        self.setup_prometheus_dirs()?;
        self.install_prometheus_bins()?;

        let paths = self
            .config
            .cert_paths
            .iter()
            .map(String::as_str)
            .collect::<Vec<_>>();

        self.files.cp(&paths, "/etc/prometheus")?;

        self.files.write(
            r#"
tls_server_config:
  cert_file: "/etc/prometheus/cert.pem"
  key_file: "/etc/prometheus/key.pem"
"#
            .trim(),
            "/etc/prometheus/web-config.yml",
        )?;

        self.setup_prometheus_services()?;
        Ok(())
    }
}

impl UbuntuPrometheusInstaller {
    fn setup_prometheus_dirs(&self) -> anyhow::Result<()> {
        self.runner.try_run(Command::new("sudo").args([
            "mkdir",
            "-p",
            "/var/db/prometheus",
            "/etc/prometheus",
        ]))?;

        self.files.chown(
            &format!("{}:{}", self.config.user, self.config.user),
            &["/etc/prometheus/", "/var/db/prometheus"],
        )?;

        Ok(())
    }

    fn install_prometheus_bins(&self) -> anyhow::Result<()> {
        let version = self
            .config
            .requirements
            .get_version("prometheus")
            .ok_or(anyhow!("failed to get version for 'prometheus"))?;

        let pkg_info = GithubPkgInfo::builder()
            .name("prometheus")
            .owner("prometheus")
            .version(version)
            .manifest(InstallManifest(vec![
                ManifestRecord::new("/usr/local/bin", ["prometheus", "promtool"]),
                ManifestRecord::new(
                    "/etc/prometheus",
                    ["consoles", "console_libraries", "prometheus.yml"],
                ),
            ]))
            .build();

        self.git_pkg.download_package(&pkg_info)?;
        Ok(())
    }

    fn setup_prometheus_services(&self) -> Result<(), anyhow::Error> {
        self.services.add_service_from_content(
            r#"
[Unit]
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
"#
            .trim(),
            "prometheus.service",
        )?;
        self.services.enable_service("prometheus.service")?;
        self.services.start_service("prometheus.service")?;
        Ok(())
    }
}

impl UbuntuPrometheusInstaller {
    pub fn new(
        runner: Rc<CommandRunner>,
        files: Rc<FilesProvider>,
        services: Rc<SystemdServiceProvider>,
        git_pkg: Rc<GithubPkgInstaller>,
        config: UbuntuPrometheusInstallerConfig,
    ) -> Self {
        Self {
            runner,
            files,
            git_pkg,
            config,
            services,
        }
    }
}

pub struct UbuntuPrometheusInstallerConfig {
    requirements: Rc<PythonRequirements>,
    cert_paths: Vec<String>,
    user: String,
}

impl UbuntuPrometheusInstallerConfig {
    pub fn new(
        user: String,
        requirements: Rc<PythonRequirements>,
        cert_paths: Vec<String>,
    ) -> Self {
        Self {
            requirements,
            cert_paths,
            user,
        }
    }
}
