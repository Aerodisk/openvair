///! Модуль работы с сервисами ОС
///!
///! See also [`ServiceProvider`]
use std::{process::Command, rc::Rc};

use crate::{openvair_manager::cmd_runner::CommandRunner, openvair_manager::files::FilesProvider};

pub trait ServiceProvider {
    fn restart_service(&self, name: &str) -> anyhow::Result<()>;
    fn add_service_from_file(&self, file: &str) -> anyhow::Result<()>;
    fn add_service_from_content(&self, content: &str, service_name: &str) -> anyhow::Result<()>;
    fn enable_service(&self, name: &str) -> anyhow::Result<()>;
    fn start_service(&self, name: &str) -> anyhow::Result<()>;
}

#[derive(Clone, Debug)]
pub struct SystemdServiceProvider {
    files: Rc<FilesProvider>,
    runner: Rc<CommandRunner>,
}

impl SystemdServiceProvider {
    pub fn new(runner: Rc<CommandRunner>, files: Rc<FilesProvider>) -> Self {
        Self { runner, files }
    }
}

impl ServiceProvider for SystemdServiceProvider {
    fn restart_service(&self, name: &str) -> anyhow::Result<()> {
        self.runner
            .try_run(Command::new("sudo").args(["systemctl", "restart", name.as_ref()]))?;
        Ok(())
    }

    fn add_service_from_file(&self, file: &str) -> anyhow::Result<()> {
        self.files.cp(&[file.as_ref()], "/etc/systemd/system")?;
        Ok(())
    }

    fn enable_service(&self, name: &str) -> anyhow::Result<()> {
        self.runner
            .try_run(Command::new("sudo").args(["systemctl", "enable", name.as_ref()]))?;
        Ok(())
    }

    fn start_service(&self, name: &str) -> anyhow::Result<()> {
        self.runner
            .try_run(Command::new("sudo").args(["systemctl", "start", name.as_ref()]))?;
        Ok(())
    }

    fn add_service_from_content(&self, content: &str, service_name: &str) -> anyhow::Result<()> {
        self.files
            .write(content, &format!("/etc/systemd/system/{}", service_name))?;
        Ok(())
    }
}
