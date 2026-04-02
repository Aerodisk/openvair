///! Модуль управления установкой на различных дистрибутивах
///!
///! See also [`PackageProvider`]
use crate::openvair_manager::cmd_runner::CommandResult;

pub trait PackageProvider {
    fn try_check_installed(&self, package_name: &str) -> anyhow::Result<bool>;
    fn try_install(&self, package_name: &str) -> anyhow::Result<CommandResult>;
    fn check_installed(&self, package_name: &str) -> bool {
        self.try_check_installed(package_name)
            .expect(&format!("failed to check if {package_name} is installed"))
    }
    fn install(&self, package_name: &str) -> CommandResult {
        self.try_install(package_name)
            .expect(&format!("failed to install {package_name}"))
    }
}

pub mod ubuntu;
