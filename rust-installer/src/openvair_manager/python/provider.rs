///! Модуль работы с Python
///!
///! See also [`PythonProvider`]
use std::{process::Command, rc::Rc};

use crate::openvair_manager::cmd_runner::CommandRunner;

#[derive(Clone, Debug)]
pub struct PythonProvider {
    runner: Rc<CommandRunner>,
    python_path: String,
}

impl PythonProvider {
    pub fn new(runner: Rc<CommandRunner>) -> Self {
        Self {
            runner,
            python_path: String::new(),
        }
    }

    pub fn set_python_path(&mut self, path: &str) {
        self.python_path = path.to_string();
    }

    fn python_cmd(&self) -> Command {
        Command::new(&self.python_path)
    }

    fn install_args() -> Vec<String> {
        vec![
            String::from("-m"),
            String::from("pip"),
            String::from("install"),
        ]
    }

    pub fn try_install(&self, package_name: &str) -> anyhow::Result<()> {
        let mut args = Self::install_args();
        args.push(package_name.to_string());
        self.runner.try_run(self.python_cmd().args(args))?;

        Ok(())
    }

    pub fn try_install_requirements(&self, requirements_path: &str) -> anyhow::Result<()> {
        let mut args = Self::install_args();
        args.extend([String::from("-r"), requirements_path.to_string()]);
        self.runner.try_run(self.python_cmd().args(args))?;

        Ok(())
    }
}
