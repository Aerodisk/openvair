///! Модуль конфигурации *установщика* Open vAIR
///!
///! Не путать с [`crate::openvair_manager::project_config`]
///!
///! See also [`OpenvairInstallerConfig`]
use std::{process::Command, rc::Rc};

use log::info;

use crate::{
    openvair_manager::cli::OpenvairManagerInstallArgs, openvair_manager::cmd_runner::CommandRunner,
};

#[derive(Default, Clone, Debug)]
pub struct OpenvairInstallerConfig {
    pub user: String,
    pub os: String,
    pub arch: String,
    pub project_name: String,
    pub docs_project_name: String,
    pub user_path: String,
    pub project_path: String,
    pub docs_project_path: String,
    pub project_config_file: String,
    pub dependencies_file: String,
    pub processor_type: String,
}

impl OpenvairInstallerConfig {
    pub fn builder() -> OpenvairInstallerConfigBuilder {
        OpenvairInstallerConfigBuilder::new()
    }
}

#[derive(Clone, Debug)]
pub struct OpenvairInstallerConfigBuilder {
    config: OpenvairInstallerConfig,
}

impl<'a> OpenvairInstallerConfigBuilder {
    pub fn new() -> Self {
        Self {
            config: Default::default(),
        }
    }

    pub fn build(
        mut self,
        runner: Rc<CommandRunner>,
        install_args: &'a OpenvairManagerInstallArgs,
    ) -> OpenvairInstallerConfig {
        self.config.user = install_args.user.clone();
        self.config.os = runner
            .pipe(
                Command::new("lsb_release").arg("-i"),
                Command::new("awk").arg("'{print tolower($3)}'"),
            )
            .output;
        self.config.arch = runner.run(Command::new("uname").arg("-m")).output;
        self.config.project_name = install_args.project_name.clone();
        self.config.docs_project_name = install_args.docs_project_name.clone();
        self.config.user_path = format!("/opt/{}", self.config.user);
        self.config.project_path =
            format!("{}/{}", self.config.user_path, self.config.project_name);
        self.config.docs_project_path = format!(
            "{}/{}",
            self.config.user_path, self.config.docs_project_name
        );
        self.config.project_config_file =
            format!("{}/project_config.toml", self.config.project_path);
        self.config.dependencies_file =
            format!("{}/third_party_requirements.txt", self.config.project_path);

        if self.config.arch == "aarch64" {
            self.config.processor_type = "arm64".to_string();
        } else {
            self.config.processor_type = "amd64".to_string();
        }

        info!("architecture set to {}", self.config.arch);
        self.config
    }
}
