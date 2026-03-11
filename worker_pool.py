"""
Worker Pool
=============
Worker threads that execute jobs by acquiring resources, running the job,
and releasing resources.

You will implement:
- Worker function that processes jobs from the scheduler
- Resource acquisition and release
- Failure handling with retries
"""

import time
import threading
from sdk_do_not_edit import GpuClusterSDK, JobExecutionError
from resource_manager import ResourceManager
from scheduler import JobScheduler
from display import display_job_update


def worker(
    worker_id: int,
    sdk: GpuClusterSDK,
    scheduler: JobScheduler,
    resource_manager: ResourceManager,
    stop_event: threading.Event,
) -> None:
    """
    Worker function -- runs in its own thread.

    Repeatedly:
    1. Gets the next ready job from the scheduler
    2. Acquires GPU resources
    3. Executes the job via the SDK
    4. Releases resources
    5. Updates the scheduler with success/failure

    Args:
        worker_id: This worker's ID (for logging)
        sdk: The GPU cluster SDK
        scheduler: The job scheduler
        resource_manager: The GPU resource manager
        stop_event: Event that signals shutdown
    """
    # TODO 11: Loop until stop_event is set or scheduler.is_complete():
    #   - Call scheduler.get_next_ready_job()
    #   - If None (no ready jobs): sleep 0.2 seconds and continue
    #   - Display: display_job_update(job.id, "ACQUIRING", "", f"Worker {worker_id} acquiring {job.gpu_count} GPUs")
    #   - Call resource_manager.acquire_gpus(job.id, job.gpu_count)
    #   - If allocation is None (timeout/shutdown):
    #       scheduler.mark_failed(job.id) and continue
    #
    # TODO 12: Execute the job:
    #   - Display: display_job_update(job.id, "RUNNING", allocation.node_id, f"Worker {worker_id} executing")
    #   - Try: result = sdk.execute_job(job.id, allocation)
    #   - If result.success:
    #       - Display: display_job_update(job.id, "COMPLETED", allocation.node_id, f"Done in {result.duration_ms}ms")
    #       - Call scheduler.mark_completed(job.id)
    #   - Else (result.success is False):
    #       - retrying = scheduler.mark_failed(job.id)
    #       - Display appropriate message (retrying or permanently failed)
    #   - Except JobExecutionError:
    #       - retrying = scheduler.mark_failed(job.id)
    #       - Display error message
    #   - Finally: ALWAYS call resource_manager.release_gpus(job.id)
    #     (this is critical -- forgetting this causes deadlocks!)
    pass
