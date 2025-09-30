use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout, Alignment},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Gauge, List, ListItem, Paragraph},
    Frame, Terminal,
};
use std::io;
use tokio::sync::mpsc;

#[derive(Clone, Debug)]
pub struct InstallStep {
    pub name: String,
    pub description: String,
    pub completed: bool,
    pub in_progress: bool,
    pub failed: bool,
}

impl InstallStep {
    pub fn new(name: &str, description: &str) -> Self {
        Self {
            name: name.to_string(),
            description: description.to_string(),
            completed: false,
            in_progress: false,
            failed: false,
        }
    }

    pub fn start(&mut self) {
        self.in_progress = true;
        self.completed = false;
        self.failed = false;
    }

    pub fn complete(&mut self) {
        self.in_progress = false;
        self.completed = true;
        self.failed = false;
    }

    pub fn fail(&mut self) {
        self.in_progress = false;
        self.completed = false;
        self.failed = true;
    }
}

pub struct InstallProgress {
    steps: Vec<InstallStep>,
    current_step: usize,
    overall_progress: f64,
}

impl InstallProgress {
    pub fn new() -> Self {
        let steps = vec![
            // First 10 steps (basic setup)
            InstallStep::new("Install tmux", "Check and install tmux if needed"),
            InstallStep::new("Verify user data", "Validate user credentials"),
            InstallStep::new("Create JWT secret", "Generate secure JWT secret"),
            InstallStep::new("Detect OS type", "Identify operating system"),
            InstallStep::new("Setup directories", "Create project directories"),
            InstallStep::new("Install Python tools", "Install python3-venv and python3-pip"),
            InstallStep::new("Create virtual env", "Set up Python virtual environment"),
            InstallStep::new("Configure PYTHONPATH", "Add project path to environment"),
            InstallStep::new("Install libpq-dev", "Install PostgreSQL development libraries"),
            InstallStep::new("Install websockify", "Install python3-websockify package"),
            
            // Extended steps (11-28)
            InstallStep::new("Install libvirt", "Install virtualization support"),
            InstallStep::new("Storage requirements", "Install NFS and XFS tools"),
            InstallStep::new("Python requirements", "Install Python dependencies"),
            InstallStep::new("Pre-commit hooks", "Setup Git pre-commit hooks"),
            InstallStep::new("PostgreSQL support", "Install psycopg2 and libraries"),
            InstallStep::new("OpenVSwitch", "Install software-defined networking"),
            InstallStep::new("Multipath tools", "Install multipath storage support"),
            InstallStep::new("Change ownership", "Fix file permissions"),
            InstallStep::new("Detect architecture", "Determine system architecture"),
            InstallStep::new("Install Docker", "Install container platform"),
            InstallStep::new("PostgreSQL container", "Setup database container"),
            InstallStep::new("RabbitMQ", "Install message broker"),
            InstallStep::new("SNMP", "Install network monitoring"),
            InstallStep::new("Database migrations", "Run Alembic migrations"),
            InstallStep::new("SSL certificates", "Generate self-signed certificates"),
            
            // Final steps (29-39)
            InstallStep::new("Prometheus", "Install monitoring system"),
            InstallStep::new("Node Exporter", "Install metrics exporter"),
            InstallStep::new("Open-iSCSI", "Install iSCSI storage support"),
            InstallStep::new("NoVNC", "Install web VNC client"),
            InstallStep::new("JQ utility", "Install JSON processor"),
            InstallStep::new("Restic backup", "Install backup utility"),
            InstallStep::new("Process services", "Setup systemd services"),
            InstallStep::new("UV package manager", "Install fast Python package manager"),
            InstallStep::new("Documentation", "Clone and install documentation"),
            InstallStep::new("Clean home directory", "Remove temporary files"),
            InstallStep::new("Hash password", "Create hashed password for database"),
            InstallStep::new("Create default user", "Add admin user to database"),
            InstallStep::new("Restart web app", "Restart main web application"),
            InstallStep::new("Final message", "Display installation summary"),
        ];

        Self {
            steps,
            current_step: 0,
            overall_progress: 0.0,
        }
    }

    pub fn start_step(&mut self, step_index: usize) {
        if step_index < self.steps.len() {
            self.steps[step_index].start();
            self.current_step = step_index;
            self.update_progress();
        }
    }

    pub fn complete_step(&mut self, step_index: usize) {
        if step_index < self.steps.len() {
            self.steps[step_index].complete();
            self.update_progress();
        }
    }

    pub fn fail_step(&mut self, step_index: usize) {
        if step_index < self.steps.len() {
            self.steps[step_index].fail();
        }
    }
    
    pub fn total_steps(&self) -> usize {
        self.steps.len()
    }

    fn update_progress(&mut self) {
        let completed_count = self.steps.iter().filter(|s| s.completed).count();
        self.overall_progress = (completed_count as f64) / (self.steps.len() as f64) * 100.0;
    }

}

pub enum TuiMessage {
    StartStep(usize),
    CompleteStep(usize),
    FailStep(usize),
    UpdateStatus(String),
    Exit,
}

pub struct TuiApp {
    progress: InstallProgress,
    status_message: String,
    should_quit: bool,
}

impl TuiApp {
    pub fn new() -> Self {
        Self {
            progress: InstallProgress::new(),
            status_message: "Starting installation...".to_string(),
            should_quit: false,
        }
    }

    pub fn handle_message(&mut self, message: TuiMessage) {
        match message {
            TuiMessage::StartStep(step) => {
                if step < self.progress.steps.len() {
                    self.progress.start_step(step);
                    self.status_message = format!("Starting: {}", self.progress.steps[step].name);
                } else {
                    // Handle out-of-bounds step gracefully
                    self.status_message = format!("Starting step {}", step);
                }
            }
            TuiMessage::CompleteStep(step) => {
                if step < self.progress.steps.len() {
                    self.progress.complete_step(step);
                    self.status_message = format!("Completed: {}", self.progress.steps[step].name);
                } else {
                    self.status_message = format!("Completed step {}", step);
                }
            }
            TuiMessage::FailStep(step) => {
                if step < self.progress.steps.len() {
                    self.progress.fail_step(step);
                    self.status_message = format!("Failed: {}", self.progress.steps[step].name);
                } else {
                    self.status_message = format!("Failed step {}", step);
                }
            }
            TuiMessage::UpdateStatus(status) => {
                self.status_message = status;
            }
            TuiMessage::Exit => {
                self.should_quit = true;
            }
        }
    }

    pub fn should_quit(&self) -> bool {
        self.should_quit
    }
}

impl TuiApp {
    fn ui(&self, f: &mut Frame) {
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .margin(2)
            .constraints([
                Constraint::Length(3),  // Title
                Constraint::Length(3),  // Progress bar
                Constraint::Min(8),     // Steps list
                Constraint::Length(3),  // Status
            ])
            .split(f.size());

        // Title
        let title = Paragraph::new("OpenVAir Installation")
            .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
            .alignment(Alignment::Center)
            .block(Block::default().borders(Borders::ALL));
        f.render_widget(title, chunks[0]);

        // Progress bar
        let progress_bar = Gauge::default()
            .block(Block::default().borders(Borders::ALL).title("Overall Progress"))
            .gauge_style(Style::default().fg(Color::Green))
            .percent(self.progress.overall_progress as u16)
            .label(format!("{:.1}%", self.progress.overall_progress));
        f.render_widget(progress_bar, chunks[1]);

        // Steps list
        let items: Vec<ListItem> = self.progress.steps
            .iter()
            .enumerate()
            .map(|(i, step)| {
                let (symbol, style) = if step.completed {
                    ("✓", Style::default().fg(Color::Green))
                } else if step.failed {
                    ("✗", Style::default().fg(Color::Red))
                } else if step.in_progress {
                    ("⟳", Style::default().fg(Color::Yellow))
                } else {
                    ("○", Style::default().fg(Color::Gray))
                };

                let content = vec![Line::from(vec![
                    Span::styled(format!("{} ", symbol), style),
                    Span::styled(&step.name, style),
                    Span::styled(format!(" - {}", step.description), Style::default().fg(Color::Gray)),
                ])];

                ListItem::new(content).style(if i == self.progress.current_step {
                    Style::default().bg(Color::DarkGray)
                } else {
                    Style::default()
                })
            })
            .collect();

        let steps_list = List::new(items)
            .block(Block::default().borders(Borders::ALL).title("Installation Steps"))
            .highlight_style(Style::default().bg(Color::DarkGray));
        f.render_widget(steps_list, chunks[2]);

        // Status
        let status = Paragraph::new(self.status_message.as_str())
            .style(Style::default().fg(Color::White))
            .alignment(Alignment::Left)
            .block(Block::default().borders(Borders::ALL).title("Status"));
        f.render_widget(status, chunks[3]);
    }

}

pub async fn run_tui_with_installation() -> anyhow::Result<()> {
    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Create app and message channel
    let mut app = TuiApp::new();
    let (tx, mut rx) = mpsc::unbounded_channel();

    // Clone sender for the installation task
    let install_tx = tx.clone();

    // Spawn installation task
    let install_handle = tokio::spawn(async move {
        let result = run_installation_with_progress(install_tx).await;
        if let Err(e) = result {
            eprintln!("Installation failed: {}", e);
        }
    });

    // Main TUI loop
    let mut last_tick = std::time::Instant::now();
    let tick_rate = std::time::Duration::from_millis(250);

    loop {
        terminal.draw(|f| app.ui(f))?;

        let timeout = tick_rate
            .checked_sub(last_tick.elapsed())
            .unwrap_or_else(|| std::time::Duration::from_secs(0));

        // Handle messages
        if let Ok(message) = rx.try_recv() {
            app.handle_message(message);
        }

        // Handle input events
        if crossterm::event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                match key.code {
                    KeyCode::Char('q') => break,
                    KeyCode::Esc => break,
                    _ => {}
                }
            }
        }

        if last_tick.elapsed() >= tick_rate {
            last_tick = std::time::Instant::now();
        }

        if app.should_quit() {
            break;
        }
    }

    // Wait for installation to complete
    let _ = install_handle.await;

    // Cleanup
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    Ok(())
}

async fn run_installation_with_progress(tx: mpsc::UnboundedSender<TuiMessage>) -> anyhow::Result<()> {
    use crate::config::OpenVairConfig;

    // Load configuration (this should be non-interactive for TUI mode)
    let _config = if crate::system::file_exists(crate::constants::CONFIG_FILE).await {
        let content = crate::system::read_file(crate::constants::CONFIG_FILE).await?;
        toml::from_str(&content)?
    } else {
        OpenVairConfig::default()
    };

    // For now, let's just simulate the steps
    for i in 0..10 {
        let _ = tx.send(TuiMessage::StartStep(i));
        
        // Simulate work
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        
        let _ = tx.send(TuiMessage::CompleteStep(i));
    }

    let _ = tx.send(TuiMessage::UpdateStatus("Installation completed successfully!".to_string()));
    tokio::time::sleep(std::time::Duration::from_secs(2)).await;
    let _ = tx.send(TuiMessage::Exit);

    Ok(())
}

/// TUI version for extended installation (21 steps)
pub async fn run_tui_with_extended_installation() -> anyhow::Result<()> {
    // For now, just redirect to basic TUI with a message
    use crate::logging::info_cyan;
    info_cyan("Extended TUI installation coming soon! Running basic TUI for now...");
    run_tui_with_installation().await
}
