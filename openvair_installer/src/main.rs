mod constants;
mod logging;
mod config;
mod system;
mod installer;
mod extended_steps;
mod tui;

use clap::{Parser, Subcommand};
use std::path::PathBuf;

/// OpenVAir installer - Rust CLI replacement for install.sh
#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    /// Configuration file path
    #[arg(short, long, value_name = "FILE")]
    config: Option<PathBuf>,

    /// Run in non-interactive mode (use existing config or defaults)
    #[arg(long)]
    non_interactive: bool,

    /// Skip tmux session setup
    #[arg(long)]
    skip_tmux: bool,

    /// Enable TUI mode with progress visualization
    #[arg(long)]
    tui: bool,

    /// Verbose logging
    #[arg(short, long)]
    verbose: bool,

    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    /// Install OpenVAir with the first 10 steps
    Install {
        /// Steps to run (comma-separated list, e.g., "1,2,3" or "all")
        #[arg(short, long, default_value = "all")]
        steps: String,
    },
    /// Extended installation with 21 steps (includes libvirt, docker prep)
    ExtendedInstall,
    /// Validate configuration file
    ValidateConfig,
    /// Generate a sample configuration file
    GenerateConfig {
        /// Output path for the configuration file
        #[arg(short, long)]
        output: Option<PathBuf>,
    },
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    // Initialize logging - use console-only for non-installation commands
    match &cli.command {
        Some(Commands::GenerateConfig { .. }) | Some(Commands::ValidateConfig) => {
            logging::init_console_logging()?;
        }
        _ => {
            logging::init_logging()?;
        }
    }

    // Set log level based on verbosity
    if cli.verbose {
        unsafe { std::env::set_var("RUST_LOG", "debug"); }
    } else {
        unsafe { std::env::set_var("RUST_LOG", "info"); }
    }

    match &cli.command {
        Some(Commands::Install { steps }) => {
            if cli.tui {
                // Run with TUI
                tui::run_tui_with_installation().await?
            } else {
                // Run in console mode
                run_installation(&cli, steps).await?
            }
        }
        Some(Commands::ExtendedInstall) => {
            if cli.tui {
                // Run extended installation with TUI
                tui::run_tui_with_extended_installation().await?
            } else {
                // Run extended installation in console mode
                run_extended_installation(&cli).await?
            }
        }
        Some(Commands::ValidateConfig) => {
            validate_config(&cli).await?
        }
        Some(Commands::GenerateConfig { output }) => {
            generate_config(&cli, output.as_deref()).await?
        }
        None => {
            // Default: run basic installation
            if cli.tui {
                tui::run_tui_with_installation().await?
            } else {
                run_installation(&cli, &"all".to_string()).await?
            }
        }
    }

    Ok(())
}

async fn run_installation(cli: &Cli, steps: &str) -> anyhow::Result<()> {
    use crate::logging::{info_cyan, info_green};

    info_cyan("🚀 Starting OpenVAir Installation");
    info_cyan(&format!("Running steps: {}", steps));

    if cli.non_interactive {
        info_cyan("Running in non-interactive mode");
    }

    // For now, we'll just run all first 10 steps
    installer::run_first_ten_steps().await?;

    info_green("✅ Installation completed successfully!");
    Ok(())
}

async fn run_extended_installation(cli: &Cli) -> anyhow::Result<()> {
    use crate::logging::{info_cyan, info_green};

    info_cyan("🚀 Starting OpenVAir EXTENDED Installation (21 steps)");
    info_cyan("This includes libvirt, storage, Python deps, and system preparation");

    if cli.non_interactive {
        info_cyan("Running in non-interactive mode");
    }

    // Run extended installation with 21 steps
    installer::run_extended_installation().await?;

    info_green("✅ Extended installation completed successfully!");
    info_cyan("🚀 System is ready for Docker and services!");
    Ok(())
}

async fn validate_config(cli: &Cli) -> anyhow::Result<()> {
    use crate::config::OpenVairConfig;
    use crate::constants::CONFIG_FILE;
    use crate::logging::{info_cyan, info_green, error_red};

    let config_path = cli.config.as_ref()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|| CONFIG_FILE.to_string());

    info_cyan(&format!("Validating configuration file: {}", config_path));

    if !std::path::Path::new(&config_path).exists() {
        error_red(&format!("Configuration file not found: {}", config_path));
        return Err(anyhow::anyhow!("Configuration file not found: {}", config_path));
    }

    let content = tokio::fs::read_to_string(&config_path).await?;
    let config: OpenVairConfig = toml::from_str(&content)?;
    
    config.validate()?;
    info_green("✅ Configuration file is valid!");
    
    Ok(())
}

async fn generate_config(_cli: &Cli, output: Option<&std::path::Path>) -> anyhow::Result<()> {
    use crate::config::OpenVairConfig;
    use crate::logging::{info_cyan, info_green};

    let default_config = OpenVairConfig::default();
    let config_content = toml::to_string_pretty(&default_config)?;
    
    let output_path = output
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|| "project_config.toml".to_string());
    
    info_cyan(&format!("Generating sample configuration file: {}", output_path));
    
    tokio::fs::write(&output_path, config_content).await?;
    
    info_green(&format!("✅ Sample configuration generated: {}", output_path));
    println!("\n📝 Please edit the configuration file to set your preferred values.");
    println!("   Pay special attention to:");
    println!("   - default_user.login and default_user.password");
    println!("   - web_app.host and web_app.port");
    println!("   - database connection settings");
    
    Ok(())
}

