///! Модуль установщика node_exporter
///!
///! Данный модуль управляет логикой установки node_exporter на разных дистрибутивах
///!
///! See also [`NodeExporterInstaller`]
use std::{process::Command, rc::Rc};

use anyhow::anyhow;

use crate::openvair_manager::{
    cmd_runner::CommandRunner,
    files::FilesProvider,
    os_services::{ServiceProvider, SystemdServiceProvider},
    pkg_management::github::{GithubPkgInfo, GithubPkgInstaller, InstallManifest, ManifestRecord},
    python::requirements::PythonRequirements,
};

pub trait NodeExporterInstaller {
    fn install_node_exporter(&self) -> anyhow::Result<()>;
}

#[derive(Clone, Debug)]
pub struct UbuntuNodeExporterInstaller {
    runner: Rc<CommandRunner>,
    files: Rc<FilesProvider>,
    git_pkg: Rc<GithubPkgInstaller>,
    services: Rc<SystemdServiceProvider>,
    config: UbuntuNodeExporterInstallerConfig,
}

impl UbuntuNodeExporterInstaller {
    fn configure_prometheus(&self) -> anyhow::Result<()> {
        self.files.append(
            r#"
  - job_name: "node_exporter"
    static_configs:
      - targets: ["localhost:9100"]
                    "#
            .trim(),
            "/etc/prometheus/prometheus.yml",
        )?;
        self.runner.try_run(Command::new("promtool").args([
            "check",
            "config",
            "/etc/prometheus/prometheus.yml",
        ]))?;
        // Restart prometheus
        self.runner.try_run(Command::new("curl").args([
            "-X",
            "POST",
            "https://localhost:9090/-/reload",
            "--insecure",
        ]))?;
        Ok(())
    }

    fn setup_services(&self) -> anyhow::Result<()> {
        self.services.add_service_from_content(
            "
[Unit]
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
                    "
            .trim(),
            "node_exporter.service",
        )?;
        self.services.enable_service("node_exporter.service")?;
        self.services.start_service("node_exporter.service")?;
        Ok(())
    }

    fn install_node_exporter_bin(&self, version: &str) -> anyhow::Result<()> {
        let product = format!("node_exporter-{version}.linux-{}", &self.config.proc);
        let target_file = format!("{product}.tar.gz");
        let target_url = format!(
            "https://github.com/prometheus/node_exporter/releases/download/v${version}/{target_file}",
        );

        // Download node_exporter
        self.runner
            .try_run(Command::new("curl").args(["-LO", &target_url]))?;
        self.runner
            .try_run(Command::new("sudo").args(["tar", "-xf", &target_file]))?;
        self.files
            .mv(&format!("{product}/node_exporter"), "/usr/local/bin")?;

        // Cleanup
        self.files.remove_files(&[&target_file])?;
        self.files.remove_dirs(&[&product])?;
        Ok(())
    }
}

impl NodeExporterInstaller for UbuntuNodeExporterInstaller {
    fn install_node_exporter(&self) -> anyhow::Result<()> {
        let version = self
            .config
            .requirements
            .get_version("node_exporter")
            .ok_or(anyhow!("failed to get version for 'node_exporter'"))?;

        let pkg_info = GithubPkgInfo::builder()
            .name("node_exporter")
            .owner("prometheus")
            .version(&version)
            .manifest(InstallManifest(vec![ManifestRecord::new(
                "/usr/local/bin",
                ["node_exporter"],
            )]))
            .build();

        self.git_pkg.download_package(&pkg_info)?;

        self.install_node_exporter_bin(&version)?;
        self.setup_services()?;
        self.configure_prometheus()?;
        Ok(())
    }
}

#[derive(Clone, Debug, Default)]
pub struct UbuntuNodeExporterInstallerConfig {
    proc: String,
    requirements: Rc<PythonRequirements>,
}

impl UbuntuNodeExporterInstallerConfig {
    pub fn builder() -> UbuntuNodeExporterInstallerConfigBuilder {
        UbuntuNodeExporterInstallerConfigBuilder::default()
    }
}

#[derive(Clone, Debug, Default)]
pub struct UbuntuNodeExporterInstallerConfigBuilder {
    config: UbuntuNodeExporterInstallerConfig,
}

impl UbuntuNodeExporterInstallerConfigBuilder {
    pub fn proc(mut self, value: impl ToString) -> Self {
        self.config.proc = value.to_string();
        self
    }

    pub fn requirements(mut self, value: Rc<PythonRequirements>) -> Self {
        self.config.requirements = value;
        self
    }

    pub fn build(self) -> UbuntuNodeExporterInstallerConfig {
        self.config
    }
}

impl UbuntuNodeExporterInstaller {
    pub fn new(
        config: UbuntuNodeExporterInstallerConfig,
        runner: Rc<CommandRunner>,
        files: Rc<FilesProvider>,
        git_pkg: Rc<GithubPkgInstaller>,
        services: Rc<SystemdServiceProvider>,
    ) -> Self {
        Self {
            runner,
            config,
            files,
            services,
            git_pkg,
        }
    }
}
