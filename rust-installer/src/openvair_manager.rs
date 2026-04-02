///! Модуль openvair_manager
///!
///! Данный модуль предназначен для инкапсуляции вспомогательных модулей,
///! использующихся в программе
pub mod cli;
pub mod cmd_runner;
pub mod docker;
pub mod files;
pub mod node_exporter;
pub mod openvair_installer;
pub mod os_services;
pub mod pkg_management;
pub mod project_config;
pub mod prometheus;
pub mod python;
