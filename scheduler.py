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
from dependency_resolver import build_dependency_graph

MAX_RETRIES = 2

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
        self._jobs = {job.id: job for job in jobs}
        self._adjacency, _ = build_dependency_graph(jobs)
        self._status = {job.id: JobStatus.PENDING for job in jobs}
        self._retries = {job.id: 0 for job in jobs}
        self._durations = {job.id: 0 for job in jobs}
        self._ready_jobs = [] # max heap (-priority, job_id)
        self._lock = threading.Lock() # for thread-safe access to ordered jobs
        self._completion_event = threading.Event()

        # init ready jobs
        for job in jobs:
            if len(job.dependencies) == 0:
                self._status[job.id] = JobStatus.READY
                heapq.heappush(self._ready_jobs, (-job.priority, job.id))

    def get_next_ready_job(self, timeout: float = 5.0) -> Job | None:
        """
        Get the highest-priority READY job.

        Args:
            timeout: Max seconds to wait (not used in basic impl -- just return None if empty)

        Returns:
            Job if one is ready, None if no ready jobs
        """
        with self._lock:
            if not len(self._ready_jobs):
                return None
            _, job_id = heapq.heappop(self._ready_jobs) 
            job = self._jobs[job_id]
            self._status[job_id] = JobStatus.RUNNING
            
            return job

    def mark_completed(self, job_id: str, duration_ms: int = 0) -> None:
        """
        Mark a job as completed and promote its dependents to READY if all their deps are done.
        """
        with self._lock:
            self._status[job_id] = JobStatus.COMPLETED
            self._durations[job_id] = duration_ms
            # set the next job's status to READY
            for next_job in self._adjacency[job_id]:
                if self._status[next_job] == JobStatus.PENDING:
                    # check if all of next jobs dependency jobs are complete
                    if all(self._status[d] == JobStatus.COMPLETED for d in self._jobs[next_job].dependencies):
                        self._status[next_job] = JobStatus.READY
                        heapq.heappush(self._ready_jobs, (-self._jobs[next_job].priority, next_job))

            if self._is_complete_unlocked():
                self._completion_event.set()

    def mark_failed(self, job_id: str) -> bool:
        """
        Mark a job as failed. Returns True if it should be retried.

        Max retries: 2. If retries remain, re-enqueue as READY.
        If no retries left, mark as FAILED permanently.
        """
        with self._lock:
            self._retries[job_id] += 1
            if self._retries[job_id] <= MAX_RETRIES:
                self._status[job_id] = JobStatus.READY
                heapq.heappush(self._ready_jobs, (-self._jobs[job_id].priority, job_id))

                return True
            
            self._status[job_id] = JobStatus.FAILED

            if self._is_complete_unlocked():
                self._completion_event.set()
            return False

    
    def _is_complete_unlocked(self) -> bool:
        return all(
                s in (JobStatus.COMPLETED, JobStatus.FAILED)
                for s in self._status.values()
            )

    def is_complete(self) -> bool:
        """Check if all jobs are in a terminal state."""
        with self._lock:
            return self._is_complete_unlocked()
            

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
                    "duration_ms": self._durations[job_id],
                }
                for job_id, status in self._status.items()
            }
