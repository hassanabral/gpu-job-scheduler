from __future__ import annotations

"""
Priority Job Scheduler
========================
Schedules jobs based on priority and dependency resolution.

You will implement:
- Priority queue using heapq
- Job state tracking
- Ready-job selection based on completed dependencies
"""

import heapq
import threading
from sdk_do_not_edit import Job, JobStatus


class JobScheduler:
    """
    Manages job scheduling with priority ordering and dependency tracking.

    Jobs start as PENDING. Once all their dependencies are COMPLETED,
    they become READY. Workers pull READY jobs in priority order.
    """

    def __init__(self, jobs: list[Job], execution_order: list[str]):
        """
        Args:
            jobs: All jobs to schedule
            execution_order: Valid execution order from topological sort
        """
        # TODO 7: Initialize the scheduler:
        #   - self._lock = threading.Lock()
        #   - self._jobs = {job.id: job for job in jobs}
        #   - self._status = {job.id: JobStatus.PENDING for job in jobs}
        #   - self._ready_queue = []  (heap: list of (-priority, job_id) tuples -- negate for max-heap)
        #   - self._retries = {job.id: 0 for job in jobs}  (retry count per job)
        #   - self._completion_event = threading.Event()
        #
        # Initialize ready queue with jobs that have no dependencies:
        #   - For each job, if len(job.dependencies) == 0:
        #       - Set status to READY
        #       - Push (-job.priority, job.id) onto self._ready_queue using heapq.heappush
        pass

    def get_next_ready_job(self, timeout: float = 5.0) -> Job | None:
        """
        Get the highest-priority READY job.

        Args:
            timeout: Max seconds to wait (not used in basic impl -- just return None if empty)

        Returns:
            Job if one is ready, None if no ready jobs
        """
        # TODO 8: Acquire self._lock, then:
        #   - If self._ready_queue is empty, return None
        #   - Pop from the heap using heapq.heappop
        #   - Set that job's status to RUNNING
        #   - Return the Job object
        pass

    def mark_completed(self, job_id: str) -> None:
        """
        Mark a job as completed and promote its dependents to READY if all their deps are done.
        """
        # TODO 9: Acquire self._lock, then:
        #   - Set self._status[job_id] = JobStatus.COMPLETED
        #   - For each job in self._jobs.values():
        #       - If job's status is PENDING and job_id is in job.dependencies:
        #           - Check if ALL of job.dependencies are now COMPLETED
        #           - If yes: set status to READY, push onto self._ready_queue
        #   - If all jobs are COMPLETED or FAILED, set self._completion_event
        pass

    def mark_failed(self, job_id: str) -> bool:
        """
        Mark a job as failed. Returns True if it should be retried.

        Max retries: 2. If retries remain, re-enqueue as READY.
        If no retries left, mark as FAILED permanently.
        """
        # TODO 10: Acquire self._lock, then:
        #   - Increment self._retries[job_id]
        #   - If self._retries[job_id] <= 2:
        #       - Set status to READY
        #       - Push back onto ready_queue
        #       - Return True (will retry)
        #   - Else:
        #       - Set status to FAILED
        #       - Check if all jobs are done (COMPLETED or FAILED), set completion_event
        #       - Return False (permanently failed)
        pass

    def is_complete(self) -> bool:
        """Check if all jobs are in a terminal state."""
        with self._lock:
            return all(
                s in (JobStatus.COMPLETED, JobStatus.FAILED)
                for s in self._status.values()
            )

    def wait_for_completion(self, timeout: float = 60.0) -> bool:
        """Wait for all jobs to complete or fail."""
        return self._completion_event.wait(timeout=timeout)

    def get_status_summary(self) -> dict:
        """Return current status of all jobs."""
        with self._lock:
            return {
                job_id: {
                    "status": status.value,
                    "retries": self._retries[job_id],
                }
                for job_id, status in self._status.items()
            }
