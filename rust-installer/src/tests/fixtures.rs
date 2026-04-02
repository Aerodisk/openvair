///! Фикстуры для тестов
use std::rc::Rc;

use rstest::fixture;

use crate::openvair_manager::{
    cmd_runner::CommandRunner, pkg_management::distro::ubuntu::UbuntuPackageProvider,
    python::provider::PythonProvider,
};

#[fixture]
pub fn command_runner() -> CommandRunner {
    CommandRunner
}

#[fixture]
pub fn python_provider(command_runner: CommandRunner) -> PythonProvider {
    PythonProvider::new(Rc::new(command_runner))
}

#[fixture]
pub fn ubuntu_package_provider(command_runner: CommandRunner) -> UbuntuPackageProvider {
    UbuntuPackageProvider::new(Rc::new(command_runner))
}
