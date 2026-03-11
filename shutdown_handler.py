"""
Graceful Shutdown Handler
===========================
Handles SIGINT/SIGTERM for clean shutdown of all threads.

You will implement:
- Signal handler registration
- Coordinated shutdown across all components
"""

import signal
import threading
from resource_manager import ResourceManager
from scheduler import JobScheduler


class ShutdownHandler:
    """
    Coordinates graceful shutdown across all components.

    When a signal is received:
    1. Stop accepting new jobs
    2. Wait for running jobs to complete
    3. Release all resources
    """

    def __init__(
        self,
        stop_event: threading.Event,
        resource_manager: ResourceManager,
        scheduler: JobScheduler,
    ):
        self._stop_event = stop_event
        self._resource_manager = resource_manager
        self._scheduler = scheduler
        self._shutdown_initiated = False

    def register(self) -> None:
        """
        Register signal handlers for SIGINT and SIGTERM.
        """
        # TODO 13: Register self._handle_signal for both SIGINT and SIGTERM
        #   - Use signal.signal(signal.SIGINT, self._handle_signal)
        #   - Use signal.signal(signal.SIGTERM, self._handle_signal)
        pass

    def _handle_signal(self, signum, frame) -> None:
        """
        Signal handler callback.
        """
        # TODO 14: Implement shutdown sequence:
        #   - If self._shutdown_initiated, return (avoid duplicate shutdown)
        #   - Set self._shutdown_initiated = True
        #   - Print a message: "\nShutdown signal received. Finishing running jobs..."
        #   - Set self._stop_event (this stops workers from picking up new jobs)
        #   - Call self._resource_manager.shutdown() (wakes up threads waiting for GPUs)
        pass

    def cleanup(self) -> None:
        """
        Final cleanup after all threads have stopped.
        """
        # TODO 15: Release any remaining GPU allocations
        #   - Check resource_manager._allocations (access for cleanup purposes)
        #   - For each remaining allocation, call resource_manager.release_gpus(job_id)
        #   - Print "Cleanup complete."
        pass
