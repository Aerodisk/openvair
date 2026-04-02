///! Модуль управления конфигурацией *openvair*
///!
///! Не путать с [`crate::openvair_manager::openvair_installer::config`]
///!
///! See also [`OpenvairPorjectConfig`]
use std::{
    fs::File,
    io::{Read, Write},
};

use serde::{Deserialize, Serialize};
use serde_valid::Validate;
use toml;

#[derive(Clone, Debug, Deserialize, Serialize, Validate)]
pub struct OpenvairProjectConfig {
    pub database: DatabaseConfig,
    pub rabbitmq: RabbitMqConfig,
    pub docker: DockerConfig,
    pub storage: StorageConfig,
    pub jwt: JwtConfig,
    pub messaging: MessagingConfig,
    pub web_app: WebAppConfig,
    pub prometheus: PrometheusConfig,
    #[validate]
    pub default_user: DefaultUserConfig,
    pub os_data: OsDataConfig,
    pub network: NetworkConfig,
    pub snmp: SnmpConfig,
    pub sentry: SentryConfig,
    pub notifications: NotificationsConfig,
    pub backup: BackupConfig,
}

impl OpenvairProjectConfig {
    pub fn try_from_file(path: &str) -> anyhow::Result<Self> {
        let mut contents: String = String::new();
        File::open(path)?.read_to_string(&mut contents)?;
        Self::try_from_contents(&contents)
    }

    pub fn try_from_contents(contents: &str) -> anyhow::Result<Self> {
        Ok(toml::from_str::<Self>(&contents)?)
    }

    pub fn try_save_file(&self, path: &str) -> anyhow::Result<()> {
        File::open(path)?.write_all(toml::to_string(self)?.as_bytes())?;
        Ok(())
    }
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DatabaseConfig {
    pub user: String,
    pub password: String,
    pub host: String,
    pub port: u32,
    pub db_name: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct RabbitMqConfig {
    pub user: String,
    pub password: String,
    pub host: String,
    pub port: u32,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DockerConfig {
    pub db_container: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct StorageConfig {
    pub data_path: String,
}

#[derive(Default, Clone, Debug, Deserialize, Serialize)]
pub struct JwtConfig {
    pub algorithm: String,
    pub token_type: String,
    pub access_token_expiration_minutes: u32,
    pub refresh_token_expiration_days: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub secret: Option<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct MessagingConfig {
    #[serde(alias = "type")]
    pub type_: String,
    pub transport: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct WebAppConfig {
    pub host: String,
    pub port: u32,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct PrometheusConfig {
    pub host: String,
    pub port: u32,
}

#[derive(Clone, Debug, Deserialize, Serialize, Validate)]
pub struct DefaultUserConfig {
    #[validate(max_length = 30)]
    #[validate(min_length = 5)]
    pub login: String,
    #[validate(min_length = 5)]
    pub password: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct OsDataConfig {
    pub os_type: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct NetworkConfig {
    pub config_manager: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SnmpConfig {
    pub agent_type: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SentryConfig {
    pub dsn: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct NotificationsConfig {
    pub email: NotificationsEmailConfig,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct NotificationsEmailConfig {
    pub smtp_server: String,
    pub smtp_port: u32,
    pub smtp_username: String,
    pub smtp_password: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct BackupConfig {
    pub backuper: String,
    pub restic: BackupResticConfig,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct BackupResticConfig {
    pub repository: String,
    pub password: String,
}

#[cfg(test)]
mod tests {
    use serde_valid::Validate;

    use crate::openvair_manager::project_config::OpenvairProjectConfig;

    #[test]
    fn test_config_read() {
        let contents = r#"
[database]
user = 'aero'
password = 'aero'
host = '0.0.0.0'
port = 5432
db_name = 'openvair'

[rabbitmq]
user = 'guest'
password = 'guest'
host = 'localhost'
port = 5672

[docker]
db_container = 'postgres'

[storage]
data_path = '/opt/aero/openvair/data'

[jwt]
algorithm = 'HS256'
token_type = "bearer"
access_token_expiration_minutes = 30
refresh_token_expiration_days = 30

[messaging]
type = 'rpc'
transport = 'rabbitmq'

[web_app]
host = 'localhost'
port = 8000

[prometheus]
host = 'localhost'
port = 9090

[default_user]
login = 'aaaaa'
password = 'aaaaaaa'

[os_data]
os_type = ''

[network]
config_manager = 'ovs'

[snmp]
agent_type = 'agentx'

[sentry]
dsn = ''


[notifications]
    [notifications.email]
    smtp_server = 'smtp.yandex.ru'
    smtp_port = 465
    smtp_username = 'your_email@example.com'
    smtp_password = 'your_password'

[backup]
    backuper = 'restic'
    [backup.restic]
    repository = ''
    password = ''  
            "#;

        let conf = OpenvairProjectConfig::try_from_contents(contents)
            .expect("failed to parse project config");
        assert_eq!(conf.database.user, "aero");
        assert!(conf.validate().is_ok());
    }
}
