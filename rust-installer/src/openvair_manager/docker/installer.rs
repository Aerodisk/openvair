///! Модуль установщика Docker
///!
///! Данный модуль задаёт основную логику установки Docker для разных дистрибутивов.
///!
///! See also [`DockerInstaller`]
use std::{process::Command, rc::Rc};

use crate::openvair_manager::{
    cmd_runner::CommandRunner,
    files::FilesProvider,
    pkg_management::distro::{PackageProvider, ubuntu::UbuntuPackageProvider},
};

pub trait DockerInstaller {
    fn install_docker(&self) -> anyhow::Result<()>;
}

pub struct UbuntuDockerInstaller {
    pkg: Rc<UbuntuPackageProvider>,
    runner: Rc<CommandRunner>,
    files: Rc<FilesProvider>,
    os_type: String,
    proc: String,
}

impl UbuntuDockerInstaller {
    pub fn new(
        runner: Rc<CommandRunner>,
        files: Rc<FilesProvider>,
        pkg: Rc<UbuntuPackageProvider>,
    ) -> Self {
        Self {
            runner,
            pkg,
            os_type: String::new(),
            proc: String::new(),
            files,
        }
    }

    pub fn set_os_type(&mut self, value: &str) {
        self.os_type = value.to_string();
    }

    pub fn set_proc(&mut self, value: &str) {
        self.proc = value.to_string();
    }
}

impl<'a> DockerInstaller for UbuntuDockerInstaller {
    fn install_docker(&self) -> anyhow::Result<()> {
        let pkgs = [
            "apt-transport-https",
            "ca-certificates",
            "curl",
            "gnupg-agent",
            "software-properties-common",
        ];
        for p in pkgs {
            self.pkg.try_install(p)?;
        }

        self.runner.pipe(
            Command::new("curl").args([
                "-fsSL",
                &format!("https://download.docker.com/linux/{}/gpg", self.os_type),
            ]),
            Command::new("sudo").args(["apt-key", "add", "-"]),
        );

        let lsb_res = self.runner.run(Command::new("lsb_release").arg("-cs"));
        let lsb_release = lsb_res.output.trim();

        self.files.write(
            &format!(
                "'deb [arch={}] https://download.docker.com/linux/{} {lsb_release} stable'",
                self.proc, self.os_type
            ),
            "/etc/apt/sources.list.d/docker.list",
        )?;

        self.runner
            .run(Command::new("sudo").args(["apt-get", "update"]));
        let docker_pkgs = ["docker-ce", "docker-ce-cli", "containerd.io"];

        for p in docker_pkgs {
            self.pkg.install(p);
        }

        Ok(())
    }
}
