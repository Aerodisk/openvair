"""Background task management framework.

This module provides a framework for managing background tasks that run
periodically in a separate thread. It includes classes for defining and
managing these tasks, handling graceful shutdowns, and supporting
decorators for periodic tasks.

Classes:
    ServiceExitError: Custom exception used to signal service shutdown.
    Task: A thread-based task that executes periodically.
    MetaBackgroundTasks: Metaclass that automatically registers periodic
        tasks.
    BackgroundTasks: Base class that manages background tasks, including
        starting, stopping, and handling shutdowns.

Functions:
    service_shutdown: Signal handler function to initiate service shutdown.
    periodic_task: Decorator to mark a method as a periodic task with a
        specified interval.
"""

import time
import types
import signal
from typing import Any, NoReturn
from threading import Event, Thread
from collections.abc import Callable


class ServiceExitError(Exception):
    """Custom exception used to signal service shutdown."""

    pass


def service_shutdown(
    _signum: int,
    _frame: types.FrameType | None,
) -> NoReturn:
    """Signal handler function to initiate service shutdown.

    This function raises a ServiceExitError when a shutdown signal is received.

    Args:
        signum: The signal number received.
        frame: The current stack frame.
    """
    raise ServiceExitError


class Task(Thread):
    """A thread-based task that executes periodically.

    This class represents a task that runs in a separate thread and executes
    a specified function at regular intervals.

    Attributes:
        stopped (Event): Event to signal the task to stop.
        interval (float): Interval between task executions.
        execute (callable): The function to execute periodically.
        manager (callable): The manager instance to pass to the execute
            function.
        args: Additional positional arguments for the execute function.
        kwargs: Additional keyword arguments for the execute function.
    """

    def __init__(
        self,
        interval: float,
        execute: Callable,
        manager: Callable,
        *args: Any,  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        **kwargs: Any,  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
    ) -> None:
        """Initialize the Task instance.

        Args:
            interval (float): Interval between task executions.
            execute (callable): The function to execute periodically.
            manager (callable): The manager instance to pass to the execute
                function.
            *args: Additional positional arguments for the execute function.
            **kwargs: Additional keyword arguments for the execute function.
        """
        Thread.__init__(self)
        self.stopped = Event()
        self.interval = interval
        self.execute = execute
        self.manager = manager
        self.args = args
        self.kwargs = kwargs

    def stop(self) -> None:
        """Stop the task from executing and terminate the thread."""
        self.stopped.set()
        self.join()

    def run(self) -> None:
        """Run the task periodically until stopped."""
        while not self.stopped.wait(self.interval):
            self.execute(self.manager())


class MetaBackgroundTasks(type):
    """Metaclass that automatically registers periodic tasks.

    This metaclass scans for methods decorated with `@periodic_task` and
    registers them as background tasks to be managed by the
    `BackgroundTasks` class.
    """

    def __init__(cls, names: str, bases: tuple, dict_: dict):
        """Initialize the MetaBackgroundTasks instance.

        Args:
            names: The name of the class being defined.
            bases: The base classes of the class being defined.
            dict_: The class dictionary.
        """
        cls._background_tasks = []
        super().__init__(names, bases, dict_)
        for method in cls.__dict__.values():
            if callable(method) and hasattr(method, '_periodic'):
                cls._background_tasks.append(
                    Task(method._interval, method, cls)  # noqa: SLF001 becasue it only way with Dynamic working for getting interval arg
                )


class BackgroundTasks(metaclass=MetaBackgroundTasks):
    """Base class that manages background tasks.

    This class provides methods to start, stop, and manage background tasks
    that run periodically in separate threads.

    Attributes:
        _background_tasks (List[Task]): List of registered background tasks.
    """

    def __init__(self) -> None:
        """Initialize the BackgroundTasks instance."""
        super(BackgroundTasks, self).__init__()

    @classmethod
    def start(cls, *, block: bool) -> None:
        """Start all registered background tasks.

        Args:
            block (bool): If True, the main thread is blocked and waits for
                shutdown signals. If False, tasks run as daemon threads.
        """
        cls._start_tasks(block=block)

        if block:
            cls._block_main_thread()

    @classmethod
    def _start_tasks(cls, *, block: bool) -> None:
        """Start each background task.

        Args:
            block (bool): If True, tasks run in non-daemon mode, allowing the
                main thread to block. If False, tasks run as daemon threads.
        """
        for task in cls._background_tasks:
            task.daemon = not block
            task.start()

    @classmethod
    def stop(cls) -> None:
        """Stop all running background tasks."""
        cls._stop_tasks()

    @classmethod
    def _stop_tasks(cls) -> None:
        """Stop each background task."""
        for task in cls._background_tasks:
            task.stop()

    @classmethod
    def _block_main_thread(cls) -> None:
        """Block the main thread and handle shutdown signals.

        This method blocks the main thread, waits for shutdown signals, and
        handles the cleanup of background tasks upon receiving a shutdown
        signal.
        """
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)

        while True:
            try:
                time.sleep(1)
            except ServiceExitError:
                cls.stop()
                break


def periodic_task(interval: int = 5) -> Callable[[Callable], Callable]:
    """Decorator that wraps a method for periodic execution."""

    def decorator(method: Callable) -> Callable:
        method._periodic = True  # type: ignore # noqa: SLF001 because its dynamic working in decorator
        method._interval = interval  # type: ignore # noqa: SLF001 because its dynamic working in decorator

        return method

    return decorator
