///! Модуль работы с файлами
///!
///! Данный модуль предоставляет интерфейс для совершения
///! частых операций с файлами и директориями, такими как
///! перенос/переименование, копирование, удаление и запись
///!
///! See also [`FilesProvider`]
use std::{process::Command, rc::Rc};

use crate::openvair_manager::cmd_runner::CommandRunner;

#[derive(Clone, Debug)]
pub struct FilesProvider {
    runner: Rc<CommandRunner>,
}

impl FilesProvider {
    pub fn new(runner: Rc<CommandRunner>) -> Self {
        Self { runner }
    }

    pub fn remove_files(&self, paths: &[&str]) -> anyhow::Result<()> {
        let mut args = vec!["rm"];
        args.extend(paths);

        self.runner.try_run(Command::new("sudo").args(args))?;
        Ok(())
    }

    pub fn remove_dirs(&self, paths: &[&str]) -> anyhow::Result<()> {
        let mut args = vec!["rm", "-rf"];
        args.extend(paths);

        self.runner.try_run(Command::new("sudo").args(args))?;
        Ok(())
    }

    pub fn mv(&self, src_path: &str, target_path: &str) -> anyhow::Result<()> {
        self.runner
            .try_run(Command::new("sudo").args(["mv", src_path, target_path]))?;
        Ok(())
    }

    pub fn cp(&self, src_paths: &[&str], target_path: &str) -> anyhow::Result<()> {
        let mut args = vec!["cp"];
        args.extend(src_paths);
        args.push(target_path);

        self.runner.try_run(Command::new("sudo").args(args))?;
        Ok(())
    }

    pub fn chown(&self, owner: &str, files: &[&str]) -> anyhow::Result<()> {
        let mut args = vec!["chown", "-R"];
        args.push(owner);
        args.extend(files);

        self.runner.try_run(Command::new("sudo").args(args))?;
        Ok(())
    }

    pub fn write(&self, content: &str, path: &str) -> anyhow::Result<()> {
        self.runner.try_pipe(
            Command::new("echo").arg(content),
            Command::new("sudo").args(["tee", path]),
        )?;
        Ok(())
    }

    pub fn append(&self, content: &str, path: &str) -> anyhow::Result<()> {
        self.runner.try_pipe(
            Command::new("echo").arg(content),
            Command::new("sudo").args(["tee", "-a", path]),
        )?;
        Ok(())
    }
}
