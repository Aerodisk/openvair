use std::path::Path;

/// Default user for OpenVAir installation
pub const USER: &str = "aero";

/// Base path for user installation
pub const USER_PATH: &str = "/opt/aero";

/// Main project directory
pub const PROJECT_PATH: &str = "/opt/aero/openvair";

/// Project configuration file path
pub const CONFIG_FILE: &str = "/opt/aero/openvair/project_config.toml";

/// Installation log file path
pub const LOG_FILE: &str = "/opt/aero/openvair/install.log";

/// Default database settings
pub const DEFAULT_DB_PORT: u16 = 5432;
pub const DEFAULT_DB_NAME: &str = "openvair";

/// Default web app settings
pub const DEFAULT_WEB_HOST: &str = "localhost";
pub const DEFAULT_WEB_PORT: u16 = 8000;

/// Default RabbitMQ settings
pub const DEFAULT_RABBITMQ_HOST: &str = "localhost";
pub const DEFAULT_RABBITMQ_PORT: u16 = 5672;
pub const DEFAULT_RABBITMQ_USER: &str = "guest";
pub const DEFAULT_RABBITMQ_PASSWORD: &str = "guest";

/// Default Prometheus settings
pub const DEFAULT_PROMETHEUS_HOST: &str = "localhost";
pub const DEFAULT_PROMETHEUS_PORT: u16 = 9090;

/// Helper function to ensure a path exists
pub fn ensure_path_exists(path: &str) -> anyhow::Result<()> {
    let path_obj = Path::new(path);
    if let Some(parent) = path_obj.parent() {
        std::fs::create_dir_all(parent)?;
    }
    Ok(())
}