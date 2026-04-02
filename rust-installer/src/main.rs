///! # Описание
///!
///! Данная программа позволяет управлять openvair
///!  
///! ## Архитектура
///!
///! Программа состоит из модулей, каждый из которых несёт ответственность
///! за отдельную логическую часть функционала. Например модуль [`crate::openvair_manager::cmd_runner`]
///! отвечает за запуск команд в шелле, модуль [`crate::openvair_manager::git_pkg`] позволяет устанавливать
///! пакеты с github и т.п.
///!
///! Если в коде часто встречается один и тот же функционал (например установка пакетов,
///! управление файлами, запуск комманд) -- рекомендуется вынести этот функционал в отдельный модуль.
///!
///! Для каждого набора функционала создаётся свой `struct`, как правило называемый "Provider",
///! или другим словом, если у него есть более чёткое предназначение. Провайдеры
///! рекомендуется сочитать друг с другом для достижения их функционала.
///!
///! Например, в рамках установки пакетов с github требуется запускать комманды в шелле,
///! так что в конструктор провайдера комманд входит указатель [`std::rc::Rc`] на провайдер комманд
use std::{process::Command, rc::Rc};

use clap::Parser;

use crate::openvair_manager::{
    cli::OpenvairManagerCli,
    cmd_runner::CommandRunner,
    docker::{installer::UbuntuDockerInstaller, provider::DockerProvider},
    files::FilesProvider,
    node_exporter::installer::{UbuntuNodeExporterInstaller, UbuntuNodeExporterInstallerConfig},
    openvair_installer::{config::OpenvairInstallerConfig, service::OpenvairInstaller},
    os_services::SystemdServiceProvider,
    pkg_management::{
        distro::ubuntu::UbuntuPackageProvider,
        github::{GithubPkgInstaller, GithubPkgInstallerConfig},
    },
    project_config::OpenvairProjectConfig,
    prometheus::installer::{UbuntuPrometheusInstaller, UbuntuPrometheusInstallerConfig},
    python::{provider::PythonProvider, requirements::PythonRequirements},
};

mod tests;

pub mod openvair_manager;

// TODO нужно будет добавить механизм определения дистрибутива и настраивать по нему все провайдеры ниже
fn main() -> anyhow::Result<()> {
    let runner = Rc::new(CommandRunner::new());
    let files = Rc::new(FilesProvider::new(runner.clone()));
    let pkg = Rc::new(UbuntuPackageProvider::new(runner.clone()));
    let mut docker_installer =
        UbuntuDockerInstaller::new(runner.clone(), files.clone(), pkg.clone());
    let docker = DockerProvider::new(runner.clone());
    let mut python = PythonProvider::new(runner.clone());
    let services = Rc::new(SystemdServiceProvider::new(runner.clone(), files.clone()));

    let cli = OpenvairManagerCli::parse();
    match cli.command {
        openvair_manager::cli::ManagerCommands::Install(openvair_manager_install_args) => {
            let installer_cfg = OpenvairInstallerConfig::builder()
                .build(runner.clone(), &openvair_manager_install_args);
            let project_cfg =
                OpenvairProjectConfig::try_from_file(&installer_cfg.project_config_file)?;
            let third_party_requirements = Rc::new(PythonRequirements::from_file(
                &installer_cfg.dependencies_file,
            )?);

            let os_type = runner
                .pipe(
                    Command::new("lsb_release").arg("-i"),
                    Command::new("cut").args(["-f", "2-"]),
                )
                .output
                .to_lowercase();
            docker_installer.set_os_type(&os_type);
            docker_installer.set_proc(&installer_cfg.processor_type);
            python.set_python_path(&format!("{}/venv/bin/python3", installer_cfg.project_path));
            let git_pkg = Rc::new(GithubPkgInstaller::new(
                GithubPkgInstallerConfig::new(installer_cfg.processor_type.clone()),
                runner.clone(),
                files.clone(),
            ));
            let prometheus_installer = Rc::new(UbuntuPrometheusInstaller::new(
                runner.clone(),
                files.clone(),
                services.clone(),
                git_pkg.clone(),
                UbuntuPrometheusInstallerConfig::new(
                    installer_cfg.user.clone(),
                    third_party_requirements.clone(),
                    vec![
                        format!("{}/cert.pem", installer_cfg.project_path),
                        format!("{}/key.pem", installer_cfg.project_path),
                    ],
                ),
            ));
            let node_exporter_installer = Rc::new(UbuntuNodeExporterInstaller::new(
                UbuntuNodeExporterInstallerConfig::builder()
                    .proc(&installer_cfg.processor_type)
                    .requirements(third_party_requirements)
                    .build(),
                runner.clone(),
                files.clone(),
                git_pkg.clone(),
                services.clone(),
            ));

            let mut installer = OpenvairInstaller::new(
                installer_cfg,
                project_cfg,
                pkg,
                runner,
                files,
                &docker_installer,
                &docker,
                prometheus_installer,
                node_exporter_installer,
                &python,
                services,
            );

            installer.install_openvair()?;
        }
    }

    Ok(())
}
