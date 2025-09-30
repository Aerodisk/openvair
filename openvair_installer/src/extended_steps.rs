use async_trait::async_trait;

use crate::installer::{InstallerStep, InstallationContext};
use crate::logging::{info_cyan, info_green};
use crate::system::*;

/// 11. Libvirt virtualization support (install_requirements_for_libvirt)
#[derive(Default)]
pub struct LibvirtStep;

#[async_trait]
impl InstallerStep for LibvirtStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        // Install required packages
        let packages = vec![
            "qemu-kvm", 
            "libvirt-daemon-system", 
            "libvirt-clients", 
            "bridge-utils", 
            "libvirt-dev", 
            "python3-dev", 
            "build-essential"
        ];
        
        for package in packages {
            install_package(package).await?;
        }

        // Enable and start libvirt service
        run_shell("sudo systemctl enable --now libvirtd", "Enable libvirt daemon").await?;

        // Add user to libvirt and kvm groups
        let user = &ctx.user;
        run_shell(&format!("sudo usermod -aG libvirt {}", user), "Add user to libvirt group").await?;
        run_shell(&format!("sudo usermod -aG kvm {}", user), "Add user to kvm group").await?;

        info_green("Libvirt virtualization support installed successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "Libvirt" }
    fn description(&self) -> &'static str { "Install libvirt virtualization support" }
}

/// 12. Install libvirt-python (install_libvirt_python)
#[derive(Default)]
pub struct LibvirtPythonStep;

#[async_trait]
impl InstallerStep for LibvirtPythonStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let pip_cmd = format!("{}/venv/bin/pip install libvirt-python", ctx.project_path);
        run_shell(&pip_cmd, "Install libvirt-python").await?;
        info_green("libvirt-python installed successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "LibvirtPython" }
    fn description(&self) -> &'static str { "Install libvirt Python bindings" }
}

/// 13. Storage requirements (install_requirements_for_storages)
#[derive(Default)]
pub struct StorageRequirementsStep;

#[async_trait]
impl InstallerStep for StorageRequirementsStep {
    async fn run(&self, _ctx: &mut InstallationContext) -> anyhow::Result<()> {
        // Install storage packages
        let packages = vec!["nfs-common", "xfsprogs"];
        for package in packages {
            install_package(package).await?;
        }

        info_green("Storage requirements installed successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "StorageRequirements" }
    fn description(&self) -> &'static str { "Install storage and NFS support packages" }
}

/// 14. Install wheel (install_wheel)
#[derive(Default)]
pub struct WheelStep;

#[async_trait]
impl InstallerStep for WheelStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let pip_cmd = format!("{}/venv/bin/pip install wheel", ctx.project_path);
        run_shell(&pip_cmd, "Install wheel in venv").await?;
        info_green("Wheel installed successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "Wheel" }
    fn description(&self) -> &'static str { "Install Python wheel package" }
}

/// 15. Install Python requirements (install_python_requirements)
#[derive(Default)]
pub struct PythonRequirementsStep;

#[async_trait]
impl InstallerStep for PythonRequirementsStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let requirements_path = format!("{}/requirements.txt", ctx.project_path);
        if file_exists(&requirements_path).await {
            let pip_cmd = format!("{}/venv/bin/pip install -r {}", ctx.project_path, requirements_path);
            run_shell(&pip_cmd, "Install Python requirements").await?;
            info_green("Python requirements installed successfully");
        } else {
            info_cyan("No requirements.txt found, skipping Python requirements installation");
        }
        Ok(())
    }
    
    fn name(&self) -> &'static str { "PythonRequirements" }
    fn description(&self) -> &'static str { "Install Python project requirements" }
}

/// 16. Install pre-commit (install_pre-commit)
#[derive(Default)]
pub struct PreCommitStep;

#[async_trait]
impl InstallerStep for PreCommitStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let precommit_bin = format!("{}/venv/bin/pre-commit", ctx.project_path);
        
        // Install pre-commit hooks
        run_shell(&format!("cd {} && {} install", ctx.project_path, precommit_bin), 
                 "Install pre-commit hooks").await?;

        info_green("Pre-commit hooks installed successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "PreCommit" }
    fn description(&self) -> &'static str { "Install and configure pre-commit hooks" }
}

/// 17. Install psycopg2 (install_psycopg2)
#[derive(Default)]
pub struct PostgresqlSupportStep;

#[async_trait]
impl InstallerStep for PostgresqlSupportStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        // Install psycopg2 in venv
        let venv_pip = format!("{}/venv/bin/pip", ctx.project_path);
        run_shell(&format!("{} install psycopg2", venv_pip), "Install psycopg2").await?;

        info_green("PostgreSQL support installed successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "PostgresqlSupport" }
    fn description(&self) -> &'static str { "Install PostgreSQL database support" }
}

/// 18. Install Open vSwitch (install_openvswitch)
#[derive(Default)]
pub struct OpenVSwitchStep;

#[async_trait]
impl InstallerStep for OpenVSwitchStep {
    async fn run(&self, _ctx: &mut InstallationContext) -> anyhow::Result<()> {
        // Install Open vSwitch
        install_package("openvswitch-switch").await?;

        // Enable and start the service
        run_shell("sudo systemctl enable --now openvswitch-switch", "Enable Open vSwitch").await?;

        // Validate installation
        run_shell("sudo ovs-vsctl show", "Validate Open vSwitch installation").await?;

        info_green("Open vSwitch installed successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "OpenVSwitch" }
    fn description(&self) -> &'static str { "Install and configure Open vSwitch networking" }
}

/// 19. Install multipath tools (install_multipath)
#[derive(Default)]
pub struct MultipathStep;

#[async_trait]
impl InstallerStep for MultipathStep {
    async fn run(&self, _ctx: &mut InstallationContext) -> anyhow::Result<()> {
        // Install multipath tools
        install_package("multipath-tools").await?;

        // Enable and start the service
        run_shell("sudo systemctl enable --now multipathd", "Enable multipath daemon").await?;

        info_green("Multipath tools installed successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "Multipath" }
    fn description(&self) -> &'static str { "Install multipath I/O tools" }
}

/// 20. Change owner (change_owner)
#[derive(Default)]
pub struct ChangeOwnerStep;

#[async_trait]
impl InstallerStep for ChangeOwnerStep {
    async fn run(&self, ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let change_cmd = format!("sudo chown -R {}:{} {}", ctx.user, ctx.user, ctx.project_path);
        run_shell(&change_cmd, "Change project ownership to user").await?;
        info_green("Project ownership changed successfully");
        Ok(())
    }
    
    fn name(&self) -> &'static str { "ChangeOwner" }
    fn description(&self) -> &'static str { "Change project ownership to the specified user" }
}

/// 21. Set architecture (set_arch)
#[derive(Default)]
pub struct ArchDetectionStep;

#[async_trait]
impl InstallerStep for ArchDetectionStep {
    async fn run(&self, _ctx: &mut InstallationContext) -> anyhow::Result<()> {
        let arch = get_system_arch().await?;
        info_green(&format!("System architecture detected: {}", arch));
        Ok(())
    }
    
    fn name(&self) -> &'static str { "ArchDetection" }
    fn description(&self) -> &'static str { "Detect system architecture for binary downloads" }
}

/// Utility function to get system architecture
async fn get_system_arch() -> anyhow::Result<String> {
    let output = run_shell_output("uname -m").await?;
    let arch = output.trim();
    
    Ok(match arch {
        "aarch64" => "arm64".to_string(),
        _ => "amd64".to_string(),
    })
}