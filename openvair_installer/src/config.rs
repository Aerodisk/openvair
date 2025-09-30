use dialoguer::{Input, Password};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

use crate::constants::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub user: String,
    pub password: String,
    pub host: String,
    pub port: u16,
    pub db_name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RabbitMQConfig {
    pub user: String,
    pub password: String,
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DockerConfig {
    pub db_container: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StorageConfig {
    pub data_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JwtConfig {
    pub algorithm: String,
    pub token_type: String,
    pub access_token_expiration_minutes: u32,
    pub refresh_token_expiration_days: u32,
    pub secret: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessagingConfig {
    #[serde(rename = "type")]
    pub messaging_type: String,
    pub transport: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WebAppConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrometheusConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DefaultUserConfig {
    pub login: String,
    pub password: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OsDataConfig {
    pub os_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkConfig {
    pub config_manager: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnmpConfig {
    pub agent_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SentryConfig {
    pub dsn: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmailConfig {
    pub smtp_server: String,
    pub smtp_port: u16,
    pub smtp_username: String,
    pub smtp_password: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NotificationsConfig {
    pub email: EmailConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResticConfig {
    pub repository: String,
    pub password: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackupConfig {
    pub backuper: String,
    pub restic: ResticConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OpenVairConfig {
    pub database: DatabaseConfig,
    pub rabbitmq: RabbitMQConfig,
    pub docker: DockerConfig,
    pub storage: StorageConfig,
    pub jwt: JwtConfig,
    pub messaging: MessagingConfig,
    pub web_app: WebAppConfig,
    pub prometheus: PrometheusConfig,
    pub default_user: DefaultUserConfig,
    pub os_data: OsDataConfig,
    pub network: NetworkConfig,
    pub snmp: SnmpConfig,
    pub sentry: SentryConfig,
    pub notifications: NotificationsConfig,
    pub backup: BackupConfig,
}

impl Default for OpenVairConfig {
    fn default() -> Self {
        Self {
            database: DatabaseConfig {
                user: USER.to_string(),
                password: USER.to_string(),
                host: "0.0.0.0".to_string(),
                port: DEFAULT_DB_PORT,
                db_name: DEFAULT_DB_NAME.to_string(),
            },
            rabbitmq: RabbitMQConfig {
                user: DEFAULT_RABBITMQ_USER.to_string(),
                password: DEFAULT_RABBITMQ_PASSWORD.to_string(),
                host: DEFAULT_RABBITMQ_HOST.to_string(),
                port: DEFAULT_RABBITMQ_PORT,
            },
            docker: DockerConfig {
                db_container: "postgres".to_string(),
            },
            storage: StorageConfig {
                data_path: format!("{}/data", PROJECT_PATH),
            },
            jwt: JwtConfig {
                algorithm: "HS256".to_string(),
                token_type: "bearer".to_string(),
                access_token_expiration_minutes: 30,
                refresh_token_expiration_days: 30,
                secret: None,
            },
            messaging: MessagingConfig {
                messaging_type: "rpc".to_string(),
                transport: "rabbitmq".to_string(),
            },
            web_app: WebAppConfig {
                host: DEFAULT_WEB_HOST.to_string(),
                port: DEFAULT_WEB_PORT,
            },
            prometheus: PrometheusConfig {
                host: DEFAULT_PROMETHEUS_HOST.to_string(),
                port: DEFAULT_PROMETHEUS_PORT,
            },
            default_user: DefaultUserConfig {
                login: String::new(),
                password: String::new(),
            },
            os_data: OsDataConfig {
                os_type: String::new(),
            },
            network: NetworkConfig {
                config_manager: "ovs".to_string(),
            },
            snmp: SnmpConfig {
                agent_type: "agentx".to_string(),
            },
            sentry: SentryConfig {
                dsn: String::new(),
            },
            notifications: NotificationsConfig {
                email: EmailConfig {
                    smtp_server: "smtp.yandex.ru".to_string(),
                    smtp_port: 465,
                    smtp_username: "your_email@example.com".to_string(),
                    smtp_password: "your_password".to_string(),
                },
            },
            backup: BackupConfig {
                backuper: "restic".to_string(),
                restic: ResticConfig {
                    repository: String::new(),
                    password: String::new(),
                },
            },
        }
    }
}

impl OpenVairConfig {
    /// Load configuration from file, with interactive fallback for missing fields
    pub fn load_or_create_interactive() -> anyhow::Result<Self> {
        // Try to load existing config
        let mut config = if Path::new(CONFIG_FILE).exists() {
            let content = fs::read_to_string(CONFIG_FILE)?;
            toml::from_str(&content)?
        } else {
            // Create default config
            Self::default()
        };

        // Interactive prompts for critical missing fields
        if config.default_user.login.trim().is_empty() {
            config.default_user.login = Input::<String>::new()
                .with_prompt("Enter default user login (minimum 4 characters)")
                .validate_with(|input: &String| -> Result<(), &str> {
                    if input.len() >= 4 && input.len() <= 30 {
                        Ok(())
                    } else {
                        Err("Login must be between 4 and 30 characters")
                    }
                })
                .interact()?;
        }

        if config.default_user.password.trim().is_empty() {
            config.default_user.password = Password::new()
                .with_prompt("Enter default user password (minimum 4 characters)")
                .with_confirmation("Confirm password", "Passwords don't match")
                .validate_with(|input: &String| -> Result<(), &str> {
                    if input.len() >= 4 {
                        Ok(())
                    } else {
                        Err("Password must be at least 4 characters")
                    }
                })
                .interact()?;
        }

        // Ensure web app host is set
        if config.web_app.host.trim().is_empty() || config.web_app.host == "localhost" {
            config.web_app.host = Input::<String>::new()
                .with_prompt("Enter web application host")
                .default("localhost".to_string())
                .interact()?;
        }

        // Save updated configuration
        config.save()?;

        Ok(config)
    }

    /// Save configuration to file
    pub fn save(&self) -> anyhow::Result<()> {
        ensure_path_exists(CONFIG_FILE)?;
        let content = toml::to_string_pretty(self)?;
        fs::write(CONFIG_FILE, content)?;
        Ok(())
    }

    /// Update JWT secret in the configuration
    pub fn update_jwt_secret(&mut self, secret: String) -> anyhow::Result<()> {
        self.jwt.secret = Some(secret);
        self.save()?;
        Ok(())
    }

    /// Update OS type in the configuration
    pub fn update_os_type(&mut self, os_type: String) -> anyhow::Result<()> {
        self.os_data.os_type = os_type;
        self.save()?;
        Ok(())
    }

    /// Validate critical configuration fields
    pub fn validate(&self) -> anyhow::Result<()> {
        if self.default_user.login.len() < 4 || self.default_user.login.len() > 30 {
            return Err(anyhow::anyhow!("User login must be between 4 and 30 characters"));
        }

        if self.default_user.password.len() < 4 {
            return Err(anyhow::anyhow!("User password must be at least 4 characters"));
        }

        if self.web_app.host.trim().is_empty() {
            return Err(anyhow::anyhow!("Web application host cannot be empty"));
        }

        Ok(())
    }
}