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
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)



    def _handle_signal(self, signum, frame) -> None:
        """
        Signal handler callback.
        """
        if self._shutdown_initiated:
            return
        
        self._shutdown_initiated = True
        print("Shut down signal received. Finishing running jobs...")
        # stop works from picking up new jobs
        self._stop_event.set()
        self._resource_manager.shutdown()
        

    def cleanup(self) -> None:
        """
        Final cleanup after all threads have stopped.
        """
        for job_id in list(self._resource_manager._allocations.keys()):
            self._resource_manager.release_gpus(job_id)
        
        print("Cleanup complete.")
