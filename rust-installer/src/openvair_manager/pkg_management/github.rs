///! Модуль установки пакетов с Github
///!
///! Данный модуль предоставляет интерфейс для установки пакетов с github
///! по версии, имени, владельцу и целевой архитектуре
///!
///! See also [`GithubPkgInstaller`]
use std::{ops::Deref, process::Command, rc::Rc};

use crate::{openvair_manager::cmd_runner::CommandRunner, openvair_manager::files::FilesProvider};

#[derive(Clone, Debug)]
pub struct GithubPkgInstaller {
    config: GithubPkgInstallerConfig,
    runner: Rc<CommandRunner>,
    files: Rc<FilesProvider>,
}

impl GithubPkgInstaller {
    pub fn new(
        config: GithubPkgInstallerConfig,
        runner: Rc<CommandRunner>,
        files: Rc<FilesProvider>,
    ) -> Self {
        Self {
            config,
            runner,
            files,
        }
    }

    fn download_url(&self, url: &str) -> anyhow::Result<()> {
        self.runner
            .try_run(Command::new("curl").args(["-LO", url]))?;
        Ok(())
    }

    fn unzip_arch(&self, path: &str) -> anyhow::Result<()> {
        self.runner
            .try_run(Command::new("sudo").args(["tar", "-xf", path]))?;
        Ok(())
    }

    pub fn download_package(&self, info: &GithubPkgInfo) -> anyhow::Result<()> {
        let product = info.get_product_repr("linux", &self.config.proc);

        let url = format!(
            "https://github.com/{}/{}/releases/download/v{}/{}.tar.gz",
            info.owner, info.name, info.version, product
        );

        self.download_url(&url)?;
        self.unzip_arch(&format!("{}.tar.gz", info.name))?;

        for record in info.manifest.iter() {
            let ManifestRecord {
                target_folder,
                files,
            } = record;

            for file in files {
                self.files
                    .mv(&format!("{}/{}", product, file), &target_folder)?;
            }
        }

        self.files.remove_files(&[&format!("{product}.tar.gz")])?;
        self.files.remove_dirs(&[&product])?;

        Ok(())
    }
}

#[derive(Clone, Debug, Default)]
pub struct GithubPkgInfo {
    pub name: String,
    pub owner: String,
    pub version: String,
    pub manifest: InstallManifest,
}

impl GithubPkgInfo {
    pub fn builder() -> GithubPkgInfoBuilder {
        GithubPkgInfoBuilder::default()
    }
    pub fn get_product_repr(&self, target_os: &str, proc_type: &str) -> String {
        format!("{}-{}.{target_os}-{proc_type}", self.name, self.version)
    }
}

#[derive(Clone, Debug, Default)]
pub struct GithubPkgInfoBuilder {
    info: GithubPkgInfo,
}
impl GithubPkgInfoBuilder {
    pub fn build(self) -> GithubPkgInfo {
        self.info
    }

    pub fn name(mut self, value: &str) -> Self {
        self.info.name = value.to_string();
        self
    }

    pub fn owner(mut self, value: &str) -> Self {
        self.info.owner = value.to_string();
        self
    }

    pub fn version(mut self, value: &str) -> Self {
        self.info.version = value.to_string();
        self
    }

    pub fn manifest(mut self, value: InstallManifest) -> Self {
        self.info.manifest = value;
        self
    }
}

#[derive(Clone, Debug, Default)]
pub struct InstallManifest(pub Vec<ManifestRecord>);

impl Deref for InstallManifest {
    type Target = Vec<ManifestRecord>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

#[derive(Clone, Debug)]
pub struct ManifestRecord {
    target_folder: String,
    files: Vec<String>,
}

impl ManifestRecord {
    pub fn new(
        target_folder: impl ToString,
        files: impl IntoIterator<Item = impl ToString>,
    ) -> Self {
        let target_folder = target_folder.to_string();
        let files = files.into_iter().map(|v| v.to_string()).collect::<Vec<_>>();

        Self {
            target_folder,
            files,
        }
    }
}

#[derive(Clone, Debug)]
pub struct GithubPkgInstallerConfig {
    proc: String,
}

impl GithubPkgInstallerConfig {
    pub fn new(proc: String) -> Self {
        Self { proc }
    }
}
