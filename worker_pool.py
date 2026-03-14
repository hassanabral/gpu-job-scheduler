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
    while not stop_event.is_set() and not scheduler.is_complete():
        job = None
        try:
            job = scheduler.get_next_ready_job()
            if job is None:
                time.sleep(0.2)
                continue
                
            display_job_update(job.id, "ACQUIRING", "", f"Worker {worker_id} acquiring {job.gpu_count} GPUs")
            alloc_gpu = resource_manager.acquire_gpus(job.id, job.gpu_count)
            
            if alloc_gpu is None:
                scheduler.mark_failed(job.id)
                continue

            try:
                display_job_update(job.id, "RUNNING", alloc_gpu.node_id, f"Worker {worker_id} executing")
                result = sdk.execute_job(job.id, alloc_gpu)
                if result.success:
                    display_job_update(job.id, "COMPLETED", alloc_gpu.node_id, f"Done in {result.duration_ms}ms")
                    scheduler.mark_completed(job.id)
                else:
                    retrying = scheduler.mark_failed(job.id)
            except JobExecutionError as e:
                retrying = scheduler.mark_failed(job.id)
                print(f"Error executing job {job.id}", e)
            finally:
                resource_manager.release_gpus(job.id)

        except Exception as e:
            if job is not None:
                scheduler.mark_failed(job.id)
            print(f"Error allocating worker {worker_id}", e)
