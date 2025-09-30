use tokio::process::Command;
use std::process::Stdio;
use crate::logging::{log_operation_start, log_operation_success, log_operation_failure};

/// Execute a command with arguments and log the results
pub async fn run_command(program: &str, args: &[&str], description: &str) -> anyhow::Result<()> {
    log_operation_start(description);
    
    let output = Command::new(program)
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .await?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        
        if !stdout.trim().is_empty() {
            tracing::debug!("Command stdout: {}", stdout.trim());
        }
        if !stderr.trim().is_empty() {
            tracing::debug!("Command stderr: {}", stderr.trim());
        }
        
        log_operation_success(description);
        Ok(())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        let error = anyhow::anyhow!(
            "Command failed with exit code {}: {}", 
            output.status.code().unwrap_or(-1),
            stderr.trim()
        );
        log_operation_failure(description, &error);
        Err(error)
    }
}

/// Execute a shell command (using sh -c)
pub async fn run_shell(command: &str, description: &str) -> anyhow::Result<()> {
    run_command("sh", &["-c", command], description).await
}

/// Execute a shell command and return output
pub async fn run_shell_output(command: &str) -> anyhow::Result<String> {
    let output = Command::new("sh")
        .args(&["-c", command])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .await?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(anyhow::anyhow!(
            "Command failed with exit code {}: {}", 
            output.status.code().unwrap_or(-1),
            stderr.trim()
        ))
    }
}

/// Check if a command exists in PATH
pub async fn command_exists(command: &str) -> bool {
    Command::new("which")
        .arg(command)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .await
        .map(|status| status.success())
        .unwrap_or(false)
}

/// Install a package using apt-get
pub async fn install_package(package: &str) -> anyhow::Result<()> {
    let description = format!("Installing package: {}", package);
    
    // First check if the package is already installed
    let check_output = Command::new("dpkg")
        .args(&["-l"])
        .stdout(Stdio::piped())
        .output()
        .await?;

    let installed_packages = String::from_utf8_lossy(&check_output.stdout);
    if installed_packages.contains(&format!(" {} ", package)) {
        crate::logging::info_green(&format!("{} is already installed", package));
        return Ok(());
    }

    // Install the package
    run_command("sudo", &["apt-get", "install", "-y", package], &description).await
}

/// Update package lists
pub async fn update_package_lists() -> anyhow::Result<()> {
    run_command("sudo", &["apt-get", "update"], "Updating package lists").await
}

/// Create a directory with proper permissions
pub async fn create_directory(path: &str, owner: Option<&str>) -> anyhow::Result<()> {
    let description = format!("Creating directory: {}", path);
    run_command("sudo", &["mkdir", "-p", path], &description).await?;
    
    if let Some(owner) = owner {
        let chown_description = format!("Setting owner for directory: {}", path);
        run_command("sudo", &["chown", "-R", &format!("{}:{}", owner, owner), path], &chown_description).await?;
    }
    
    Ok(())
}

/// Check if a file exists
pub async fn file_exists(path: &str) -> bool {
    tokio::fs::metadata(path).await.is_ok()
}

/// Read a file's contents
pub async fn read_file(path: &str) -> anyhow::Result<String> {
    Ok(tokio::fs::read_to_string(path).await?)
}


/// Append content to a file
pub async fn append_to_file(path: &str, content: &str) -> anyhow::Result<()> {
    use tokio::fs::OpenOptions;
    use tokio::io::AsyncWriteExt;

    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
        .await?;
        
    file.write_all(content.as_bytes()).await?;
    Ok(())
}

/// Get OS information from /etc/os-release
pub async fn get_os_info() -> anyhow::Result<String> {
    let content = read_file("/etc/os-release").await?;
    
    for line in content.lines() {
        if line.starts_with("ID=") {
            let os_id = line.strip_prefix("ID=")
                .unwrap_or("")
                .trim_matches('"')
                .to_lowercase();
            return Ok(os_id);
        }
    }
    
    // Fallback: use lsb_release if available
    if command_exists("lsb_release").await {
        let output = Command::new("lsb_release")
            .args(&["-i", "--short"])
            .output()
            .await?;
        
        if output.status.success() {
            let os_type = String::from_utf8_lossy(&output.stdout)
                .trim()
                .to_lowercase();
            return Ok(os_type);
        }
    }
    
    Ok("unknown".to_string())
}

