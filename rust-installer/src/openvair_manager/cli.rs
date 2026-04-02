///! Модуль определения CLI интерфейса
///!
///! Данный модуль задаёт консольный интерфейс, с которым работает пользователь
///!
///! See also [`OpenvairManagerCli`]
use clap::{Args, Parser, Subcommand};

#[derive(Clone, Debug, Parser)]
#[command(
    about = "A CLI manager program for Open vAIR",
    long_about = "A CLI manager program for Open vAIR\n\n\
                  This tool can be used to manage your Open vAIR installation\n\
                  Such as install openvair, update it, uninstall it. More features pending.",
    after_help = "Written by pine-free (Freya Pines)"
)]
pub struct OpenvairManagerCli {
    #[command(subcommand)]
    pub command: ManagerCommands,
}

#[derive(Clone, Debug, Args, PartialEq, Eq)]
pub struct OpenvairManagerInstallArgs {
    #[arg(short, long, default_value_t = String::from("aero"))]
    pub user: String,
    #[arg(short, long, default_value_t = String::from("openvair"))]
    pub project_name: String,
    #[arg(short, long, default_value_t = String::from("openvair-docs"))]
    pub docs_project_name: String,
}

#[derive(Clone, Subcommand, Debug, PartialEq, Eq)]
pub enum ManagerCommands {
    Install(OpenvairManagerInstallArgs),
}

#[cfg(test)]
mod tests {

    use clap::Parser;

    use super::*;

    #[test]
    fn test_command_parse() {
        let res = OpenvairManagerCli::parse_from(["openvair-manager", "install", "-u", "test"]);
        assert_eq!(
            res.command,
            ManagerCommands::Install(OpenvairManagerInstallArgs {
                user: String::from("test"),
                project_name: String::from("openvair"),
                docs_project_name: String::from("openvair-docs")
            })
        )
    }
}
