///! Модуль работы с Docker
///!
///! Данный модуль предоставляет провайдер для работы с Docker,
///! в основном через shell.
///!
///! See also [`DockerProvider`]
use std::{process::Command, rc::Rc};

use crate::openvair_manager::cmd_runner::{CommandResult, CommandRunner};

pub struct DockerProvider {
    pub runner: Rc<CommandRunner>,
}

impl DockerProvider {
    pub fn new(runner: Rc<CommandRunner>) -> DockerProvider {
        Self { runner }
    }
}

#[derive(Clone, Debug, Default)]
pub struct DockerRunConfig {
    pub name: Option<String>,
    pub restart: Option<String>,
    pub env: Option<Vec<String>>,
    pub ports: Option<String>,
    pub hostname: Option<String>,
    pub detach: bool,
    pub command: String,
}

impl DockerRunConfig {
    pub fn new(command: &str) -> Self {
        Self {
            command: command.to_string(),
            ..Default::default()
        }
    }

    pub fn builder(self) -> DockerRunConfigBuilder {
        DockerRunConfigBuilder { config: self }
    }
}

#[derive(Clone, Debug, Default)]
pub struct DockerRunConfigBuilder {
    config: DockerRunConfig,
}

impl DockerRunConfigBuilder {
    pub fn name(mut self, value: &str) -> Self {
        self.config.name = Some(value.to_string());
        self
    }
    pub fn restart(mut self, value: &str) -> Self {
        self.config.name = Some(value.to_string());
        self
    }
    pub fn ports(mut self, value: &str) -> Self {
        self.config.name = Some(value.to_string());
        self
    }
    pub fn hostname(mut self, value: &str) -> Self {
        self.config.name = Some(value.to_string());
        self
    }

    pub fn env(mut self, value: &[&str]) -> Self {
        self.config.name = Some(
            Vec::from_iter(value)
                .iter()
                .map(ToString::to_string)
                .collect(),
        );
        self
    }

    pub fn detach(mut self, value: bool) -> Self {
        self.config.detach = value;
        self
    }

    pub fn build(self) -> DockerRunConfig {
        self.config
    }
}

impl DockerProvider {
    pub fn try_run(&self, run_config: &DockerRunConfig) -> anyhow::Result<CommandResult> {
        let mut cmd_base = Command::new("sudo");
        let mut args: Vec<&str> = vec!["docker", "run"];

        if let Some(name) = &run_config.name {
            args.extend(["--name", name]);
        }

        if let Some(restart) = &run_config.restart {
            args.extend(["--restart", restart]);
        }

        if let Some(hostname) = &run_config.hostname {
            args.extend(["--hostname", hostname]);
        }

        if let Some(ports) = &run_config.ports {
            args.extend(["-p", ports])
        }

        if let Some(env) = &run_config.env {
            let env_arg = env
                .iter()
                .map(|e| ["-e", e.as_str()])
                .flatten()
                .collect::<Vec<&str>>();
            args.extend(env_arg.as_slice());
        }

        if run_config.detach {
            args.extend(["-d"]);
        }

        args.push(&run_config.command);
        Ok(self.runner.try_run(cmd_base.args(args))?)
    }

    pub fn try_exec(&self, container_name: &str, command: &str) -> anyhow::Result<CommandResult> {
        let mut cmd = Command::new("sudo");
        Ok(self
            .runner
            .try_run(cmd.args(["docker", "exec", "-it", container_name, command]))?)
    }
}
