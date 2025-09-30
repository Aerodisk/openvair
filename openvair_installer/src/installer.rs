use base64::Engine;
use rand::RngCore;
use async_trait::async_trait;

use crate::config::OpenVairConfig;
use crate::constants::{USER, USER_PATH, PROJECT_PATH};
use crate::logging::{info_cyan, info_green};
use crate::system::*;

/// Context shared across all installation steps
pub struct InstallationContext {
    pub config: OpenVairConfig,
    pub project_path: String,
    pub user_path: String,
    pub user: String,
    // User credentials for TUI mode
    pub user_login: Option<String>,
    pub user_password: Option<String>,
}

impl InstallationContext {
    pub fn new(config: OpenVairConfig) -> Self {
        Self {
            config,
            project_path: PROJECT_PATH.to_string(),
            user_path: USER_PATH.to_string(),
            user: USER.to_string(),
            user_login: None,
            user_password: None,
        }
    }
    
}

/// Trait for modular installation steps
#[async_trait]
pub trait InstallerStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()>;
    fn name(&self) -> &'static str;
    fn description(&self) -> &'static str;
}

/// Registry for managing installation steps
pub struct StepRegistry {
    steps: Vec<Box<dyn InstallerStep + Send + Sync>>,
}

impl StepRegistry {
    pub fn new() -> Self {
        Self { steps: Vec::new() }
    }
    
    pub fn add_step<T: InstallerStep + Send + Sync + 'static>(mut self, step: T) -> Self {
        self.steps.push(Box::new(step));
        self
    }
    
    pub async fn execute_all(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        for step in &self.steps {
            info_cyan(&format!("[{}/{}] {}: {}", 
                self.get_current_step_number(step.as_ref()),
                self.steps.len(),
                step.name(), 
                step.description()));
            step.run(ctx).await?;
            info_green(&format!("✅ {} completed", step.name()));
        }
        Ok(())
    }
    
    fn get_current_step_number(&self, current_step: &dyn InstallerStep) -> usize {
        self.steps.iter().position(|step| {
            std::ptr::eq(step.as_ref() as *const dyn InstallerStep, 
                        current_step as *const dyn InstallerStep)
        }).unwrap_or(0) + 1
    }
}

/// Implementation of existing steps as the new trait

// Step implementations

#[derive(Default)]
pub struct TmuxInstallStep;

#[async_trait]
impl InstallerStep for TmuxInstallStep {
    async fn run(&self, _ctx: &mut InstallationContext) -> anyhow::Result<()> {
        if !command_exists("tmux").await {
            update_package_lists().await?;
            install_package("tmux").await?;
        } else {
            info_green("tmux is already installed");
        }

        if std::env::var("TMUX").is_ok() {
            info_green("Already running in tmux session");
            return Ok(());
        }

        info_green("tmux is available for use");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "TmuxInstall" }
    fn description(&self) -> &'static str { "Install and configure tmux session manager" }
}

#[derive(Default)]
pub struct UserDataVerificationStep;

#[async_trait]
impl InstallerStep for UserDataVerificationStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        const MIN_LOGIN_LENGTH: usize = 4;
        const MIN_PASSWORD_LENGTH: usize = 4;
        const MAX_LOGIN_LENGTH: usize = 30;

        // Use TUI-provided credentials if available, otherwise fall back to config
        let login = ctx.user_login.as_ref().unwrap_or(&ctx.config.default_user.login);
        let password = ctx.user_password.as_ref().unwrap_or(&ctx.config.default_user.password);

        if login.len() >= MIN_LOGIN_LENGTH && login.len() <= MAX_LOGIN_LENGTH {
            info_green("User login is valid");
        } else if login.len() < MIN_LOGIN_LENGTH {
            return Err(anyhow::anyhow!(
                "User login is too short. Minimum length is {} characters. Current length: {}",
                MIN_LOGIN_LENGTH, login.len()
            ));
        } else {
            return Err(anyhow::anyhow!(
                "User login is not valid or not specified. Installation script stopped"
            ));
        }

        if password.len() >= MIN_PASSWORD_LENGTH {
            info_green("User password is valid");
        } else if password.len() < MIN_PASSWORD_LENGTH {
            return Err(anyhow::anyhow!(
                "User password is too short. Minimum length is {} characters. Current length: {}",
                MIN_PASSWORD_LENGTH, password.len()
            ));
        } else {
            return Err(anyhow::anyhow!(
                "User password is not valid or not specified. Installation script stopped"
            ));
        }

        // Update config with the actual credentials used
        ctx.config.default_user.login = login.clone();
        ctx.config.default_user.password = password.clone();
        ctx.config.save()?;

        Ok(())
    }
    
    fn name(&self) -> &'static str { "UserDataVerification" }
    fn description(&self) -> &'static str { "Verify user credentials from configuration" }
}

#[derive(Default)]
pub struct JwtSecretStep;

#[async_trait]
impl InstallerStep for JwtSecretStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let secret = generate_random_secret();
        ctx.config.update_jwt_secret(secret)?;
        info_green("JWT secret created successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "JwtSecret" }
    fn description(&self) -> &'static str { "Generate and configure JWT secret" }
}

#[derive(Default)]
pub struct OsTypeDetectionStep;

#[async_trait]
impl InstallerStep for OsTypeDetectionStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let os_type = get_os_info().await?;
        ctx.config.update_os_type(os_type.clone())?;
        info_green(&format!("Received OS type: {}", os_type));
        Ok(())
    }
    
    fn name(&self) -> &'static str { "OsTypeDetection" }
    fn description(&self) -> &'static str { "Detect operating system type" }
}

#[derive(Default)]
pub struct HomeDirSetupStep;

#[async_trait]
impl InstallerStep for HomeDirSetupStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        create_directory(&ctx.user_path, Some(&ctx.user)).await?;
        create_directory(&ctx.project_path, Some(&ctx.user)).await?;
        info_green(&format!("Home directory created and configured: {}", ctx.user_path));
        Ok(())
    }
    
    fn name(&self) -> &'static str { "HomeDirSetup" }
    fn description(&self) -> &'static str { "Create and configure home directories" }
}

#[derive(Default)]
pub struct PythonToolsStep;

#[async_trait]
impl InstallerStep for PythonToolsStep {
    async fn run(&self, _ctx: &mut InstallationContext) -> anyhow::Result<()> {
        install_package("python3-venv").await?;
        install_package("python3-pip").await?;
        Ok(())
    }
    
    fn name(&self) -> &'static str { "PythonTools" }
    fn description(&self) -> &'static str { "Install Python virtual environment and pip" }
}

#[derive(Default)]
pub struct VenvCreationStep;

#[async_trait]
impl InstallerStep for VenvCreationStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let venv_path = format!("{}/venv", ctx.project_path);
        
        if file_exists(&venv_path).await {
            info_green("Python virtual environment already exists");
            return Ok(());
        }
        
        let command = format!("cd {} && python3 -m venv venv", ctx.project_path);
        run_shell(&command, "Making python virtual environment").await?;
        Ok(())
    }
    
    fn name(&self) -> &'static str { "VenvCreation" }
    fn description(&self) -> &'static str { "Create Python virtual environment" }
}

#[derive(Default)]
pub struct PythonPathStep;

#[async_trait]
impl InstallerStep for PythonPathStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let activate_path = format!("{}/venv/bin/activate", ctx.project_path);
        
        if !file_exists(&activate_path).await {
            return Err(anyhow::anyhow!("Virtual environment activate script not found: {}", activate_path));
        }

        let pythonpath_line = format!("export PYTHONPATH=\"{}:$PYTHONPATH\"\n", ctx.project_path);
        
        let content = read_file(&activate_path).await?;
        if content.contains(&format!("PYTHONPATH=\"{}:", ctx.project_path)) {
            info_green("PYTHONPATH is already configured in activate script");
            return Ok(());
        }
        
        append_to_file(&activate_path, &pythonpath_line).await?;
        info_green("PYTHONPATH added to virtual environment activate script");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "PythonPath" }
    fn description(&self) -> &'static str { "Configure PYTHONPATH in virtual environment" }
}

#[derive(Default)]
pub struct LibpqDevStep;

#[async_trait]
impl InstallerStep for LibpqDevStep {
    async fn run(&self, _ctx: &mut InstallationContext) -> anyhow::Result<()> {
        install_package("libpq-dev").await
    }
    
    fn name(&self) -> &'static str { "LibpqDev" }
    fn description(&self) -> &'static str { "Install PostgreSQL development libraries" }
}

#[derive(Default)]
pub struct WebsockifyStep;

#[async_trait]
impl InstallerStep for WebsockifyStep {
    async fn run(&self, _ctx: &mut InstallationContext) -> anyhow::Result<()> {
        install_package("python3-websockify").await
    }
    
    fn name(&self) -> &'static str { "Websockify" }
    fn description(&self) -> &'static str { "Install Python websockify for VNC proxy" }
}

// Utility functions

/// Generate a random 32-byte secret encoded as base64
fn generate_random_secret() -> String {
    let mut secret_bytes = [0u8; 32];
    rand::thread_rng().fill_bytes(&mut secret_bytes);
    base64::engine::general_purpose::STANDARD.encode(&secret_bytes)
}

/// Orchestrator function to run all 10 steps
pub async fn run_first_ten_steps() -> anyhow::Result<()> {
    info_cyan("Starting OpenVAir installation - First 10 steps");
    
    // Load configuration interactively
    let config = OpenVairConfig::load_or_create_interactive()?;
    let mut ctx = InstallationContext::new(config);

    // Build registry with the first 10 steps
    let registry = StepRegistry::new()
        .add_step(TmuxInstallStep::default())
        .add_step(UserDataVerificationStep::default())
        .add_step(JwtSecretStep::default())
        .add_step(OsTypeDetectionStep::default())
        .add_step(HomeDirSetupStep::default())
        .add_step(PythonToolsStep::default())
        .add_step(VenvCreationStep::default())
        .add_step(PythonPathStep::default())
        .add_step(LibpqDevStep::default())
        .add_step(WebsockifyStep::default());

    registry.execute_all(&mut ctx).await?;

    info_green("First 10 installation steps completed successfully!");
    Ok(())
}

/// Extended OpenVAir installation - first 21 steps
pub async fn run_extended_installation() -> anyhow::Result<()> {
    use crate::extended_steps::*;
    
    info_cyan("Starting OpenVAir EXTENDED installation (21 steps)");
    
    // Load configuration interactively
    let config = OpenVairConfig::load_or_create_interactive()?;
    let mut ctx = InstallationContext::new(config);

    // Build registry with first 21 installation steps
    let registry = StepRegistry::new()
        // First 10 steps (basic setup)
        .add_step(TmuxInstallStep::default())
        .add_step(UserDataVerificationStep::default())
        .add_step(JwtSecretStep::default())
        .add_step(OsTypeDetectionStep::default())
        .add_step(HomeDirSetupStep::default())
        .add_step(PythonToolsStep::default())
        .add_step(VenvCreationStep::default())
        .add_step(PythonPathStep::default())
        .add_step(LibpqDevStep::default())
        .add_step(WebsockifyStep::default())
        
        // Extended steps (11-21)
        .add_step(LibvirtStep::default())
        .add_step(LibvirtPythonStep::default())
        .add_step(StorageRequirementsStep::default())
        .add_step(WheelStep::default())
        .add_step(PythonRequirementsStep::default())
        .add_step(PreCommitStep::default())
        .add_step(PostgresqlSupportStep::default())
        .add_step(OpenVSwitchStep::default())
        .add_step(MultipathStep::default())
        .add_step(ChangeOwnerStep::default())
        .add_step(ArchDetectionStep::default());

    registry.execute_all(&mut ctx).await?;

    info_green("✅ Extended OpenVAir installation (21 steps) completed successfully!");
    info_cyan("🚀 Ready for Docker and services installation!");
    
    Ok(())
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_random_secret() {
        let secret1 = generate_random_secret();
        let secret2 = generate_random_secret();
        
        // Secrets should be different
        assert_ne!(secret1, secret2);
        
        // Should be valid base64
        assert!(base64::engine::general_purpose::STANDARD.decode(&secret1).is_ok());
        assert!(base64::engine::general_purpose::STANDARD.decode(&secret2).is_ok());
        
        // Decoded should be 32 bytes
        let decoded = base64::engine::general_purpose::STANDARD.decode(&secret1).unwrap();
        assert_eq!(decoded.len(), 32);
    }
}