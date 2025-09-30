use owo_colors::OwoColorize;
use std::fs::OpenOptions;
use tracing::{info, warn, error};
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

use crate::constants::LOG_FILE;

/// Initialize logging system with both console and file output
pub fn init_logging() -> anyhow::Result<()> {
    init_logging_with_file(Some(LOG_FILE))
}

/// Initialize logging system, optionally with file output
pub fn init_logging_with_file(log_file_path: Option<&str>) -> anyhow::Result<()> {
    let console_layer = fmt::layer()
        .with_writer(std::io::stderr)
        .with_ansi(true)
        .with_target(false)
        .with_thread_ids(false)
        .with_level(true)
        .with_file(false)
        .with_line_number(false);

    let registry = tracing_subscriber::registry()
        .with(EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")))
        .with(console_layer);

    if let Some(log_path) = log_file_path {
        // Try to create log file, but don't fail if we can't
        if let Ok(()) = crate::constants::ensure_path_exists(log_path) {
            if let Ok(log_file) = OpenOptions::new()
                .create(true)
                .append(true)
                .open(log_path) {
                
                let file_layer = fmt::layer()
                    .with_writer(log_file)
                    .with_ansi(false)
                    .with_target(false)
                    .with_thread_ids(false)
                    .with_level(true)
                    .with_file(true)
                    .with_line_number(true);
                
                registry.with(file_layer).init();
                return Ok(());
            }
        }
        // If we can't create the log file, just use console logging
        eprintln!("Warning: Could not create log file at {}, using console-only logging", log_path);
    }
    
    registry.init();
    Ok(())
}

/// Initialize console-only logging
pub fn init_console_logging() -> anyhow::Result<()> {
    init_logging_with_file(None)
}

/// Log an info message with cyan color
pub fn info_cyan(message: &str) {
    let timestamp = chrono::Local::now().format("[%Y-%m-%d %H:%M:%S]");
    eprintln!("{} {}", timestamp.cyan(), message.cyan());
    info!("{}", message);
}

/// Log a success message with green color
pub fn info_green(message: &str) {
    let timestamp = chrono::Local::now().format("[%Y-%m-%d %H:%M:%S]");
    eprintln!("{} {}", timestamp.green(), message.green());
    info!("{}", message);
}

/// Log a warning message with yellow color
pub fn warn_yellow(message: &str) {
    let timestamp = chrono::Local::now().format("[%Y-%m-%d %H:%M:%S]");
    eprintln!("{} {}", timestamp.yellow(), message.yellow());
    warn!("{}", message);
}

/// Log an error message with red color
pub fn error_red(message: &str) {
    let timestamp = chrono::Local::now().format("[%Y-%m-%d %H:%M:%S]");
    eprintln!("{} {}", timestamp.red(), message.red());
    error!("{}", message);
}

/// Log the start of an operation
pub fn log_operation_start(operation: &str) {
    info_cyan(&format!("Start to execute: {}", operation));
}

/// Log the successful completion of an operation
pub fn log_operation_success(operation: &str) {
    info_green(&format!("Successfully executed: {}", operation));
}

/// Log a failure of an operation
pub fn log_operation_failure(operation: &str, error: &anyhow::Error) {
    error_red(&format!("Failure while executing: {} - {}", operation, error));
}

/// Colored print macros for convenience
#[macro_export]
macro_rules! info_c {
    ($($arg:tt)*) => {
        $crate::logging::info_cyan(&format!($($arg)*))
    };
}

#[macro_export]
macro_rules! success_c {
    ($($arg:tt)*) => {
        $crate::logging::info_green(&format!($($arg)*))
    };
}

#[macro_export]
macro_rules! warn_c {
    ($($arg:tt)*) => {
        $crate::logging::warn_yellow(&format!($($arg)*))
    };
}

#[macro_export]
macro_rules! error_c {
    ($($arg:tt)*) => {
        $crate::logging::error_red(&format!($($arg)*))
    };
}