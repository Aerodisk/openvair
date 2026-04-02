///! Модуль управления запуском команд
///!
///! Во время установки часто приходится запускать разные команды,
///! Передавать их друг в друга и т.п., данный модуль призван упростить эту задачу
///!
///! See also [`CommandRunner`]
use std::process::{Command, ExitStatus, Output, Stdio};

use anyhow::anyhow;

#[derive(Clone, Debug, Copy)]
pub struct CommandRunner;

impl CommandRunner {
    pub fn new() -> Self {
        Self
    }
}

#[derive(Clone, Debug)]
pub struct CommandResult {
    pub output: String,
    pub status: ExitStatus,
}

impl CommandResult {
    pub fn new(output: &str, status: &ExitStatus) -> Self {
        Self {
            output: output.to_string(),
            status: *status,
        }
    }
}
impl From<Output> for CommandResult {
    fn from(value: Output) -> Self {
        Self::new(
            &String::from_utf8(value.stdout).expect("invalid utf8 conversion in command output"),
            &value.status,
        )
    }
}

impl CommandRunner {
    pub fn try_pipe(
        &self,
        source: &mut Command,
        destination: &mut Command,
    ) -> anyhow::Result<CommandResult> {
        let source_child = source.stdout(Stdio::piped()).spawn()?;
        let source_out = source_child
            .stdout
            .ok_or(anyhow!("failed to get stdout of source in pipe"))?;
        let dst_child = destination
            .stdin(Stdio::from(source_out))
            .stdout(Stdio::piped())
            .spawn()?;
        let out = dst_child.wait_with_output()?;
        Ok(CommandResult::from(out))
    }

    pub fn try_run(&self, command: &mut Command) -> anyhow::Result<CommandResult> {
        Ok(CommandResult::from(
            command.stdout(Stdio::piped()).spawn()?.wait_with_output()?,
        ))
    }

    pub fn run(&self, command: &mut Command) -> CommandResult {
        self.try_run(command)
            .expect(&format!("failed to run command {command:?}"))
    }

    pub fn pipe(&self, source: &mut Command, destination: &mut Command) -> CommandResult {
        self.try_pipe(source, destination)
            .expect(&format!("pipe failed: {source:?} -> {destination:?}"))
    }
}

#[cfg(test)]
mod tests {
    use rstest::rstest;

    use crate::tests::fixtures::command_runner;

    use super::*;

    #[rstest]
    fn test_runner_run_command(command_runner: CommandRunner) {
        let mut cmd = Command::new("echo");
        let res = command_runner.run(cmd.arg("Hello world"));
        assert_eq!(res.output, String::from("Hello world\n"));
    }

    #[rstest]
    fn test_runner_pipe_commands(command_runner: CommandRunner) {
        let mut cmd_src = Command::new("echo");
        let mut cmd_sed = Command::new("sed");
        let res = command_runner.pipe(cmd_src.arg("Hello world"), cmd_sed.arg("s/world/me/"));
        assert_eq!(res.output, String::from("Hello me\n"));
        assert!(res.status.success())
    }
}
