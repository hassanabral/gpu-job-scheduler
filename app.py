"""
Application Orchestrator
=========================
Wires together all components and runs the job scheduler.
"""

import time
import threading
from sdk_do_not_edit import GpuClusterSDK, JobStatus
from resource_manager import ResourceManager
from dependency_resolver import topological_sort, CyclicDependencyError
from scheduler import JobScheduler
from worker_pool import worker
from shutdown_handler import ShutdownHandler
from display import (
    display_cluster_info,
    display_job_list,
    display_dependency_graph,
    display_job_update,
    display_final_summary,
)

MAX_WORKERS = 3
def run():
    """Main application logic."""
    sdk = GpuClusterSDK()

    # Fetch cluster info and jobs
    cluster = sdk.get_cluster_info()
    jobs = sdk.list_pending_jobs()

    display_cluster_info(cluster)
    display_job_list(jobs)
    display_dependency_graph(jobs)

    # TODO 16: Resolve dependencies
    #   - Call topological_sort(jobs) to get execution_order
    #   - Handle CyclicDependencyError: print error and return
    #   - Print the execution order
    try:
        execution_order = topological_sort(jobs)
    except CyclicDependencyError as e:
        print(f"Cycle detected:", e)
        return

    print(f"Execution order:", ", ".join(execution_order))

    # TODO 17: Initialize components
    #   - resource_manager = ResourceManager(sdk, cluster)
    #   - scheduler = JobScheduler(jobs, execution_order)
    #   - stop_event = threading.Event()
    #   - shutdown_handler = ShutdownHandler(stop_event, resource_manager, scheduler)
    #   - shutdown_handler.register()
    resource_manager = ResourceManager(sdk, cluster)
    scheduler = JobScheduler(jobs, execution_order)
    stop_event = threading.Event()
    shutdown_handler = ShutdownHandler(stop_event, resource_manager, scheduler)
    shutdown_handler.register()

    # TODO 18: Start workers and wait for completion
    #   - Create 3 worker threads (targeting the worker function)
    #   - Pass: worker_id, sdk, scheduler, resource_manager, stop_event
    #   - Set daemon=True, start each
    #   - Record start_time
    #   - Call scheduler.wait_for_completion(timeout=120)
    #   - Set stop_event to stop workers
    #   - Join all worker threads with timeout=5
    #   - Call shutdown_handler.cleanup()
    #   - Compute total_time
    #   - Build results dict from scheduler.get_status_summary()
    #   - Call display_final_summary(results)
    
    wthreads = []
    for i in range(MAX_WORKERS):
        wthread = threading.Thread(target=worker, args=(i, sdk, scheduler, resource_manager, stop_event), daemon=True)

    # start worker threads
    for wthread in wthreads:
        wthread.start()
    
    start_time = time.time()

    # wait for all jobs to complete (via completion event)
    scheduler.wait_for_completion(timeout=120)
    stop_event.set()

    # wait for workers to complete
    for wthread in wthreads:
        wthread.join(timeout=5)
    
    shutdown_handler.cleanup()

    elapsted = time.time() - start_time
    result = scheduler.get_status_summary()

    total_jobs = 0
    total_completed = 0
    total_failed = 0
    gpu_utilization = 0
    job_results = []

    # run calculations
    for job_id, summary in result.items():
        status = summary['status']
        allocation = resource_manager._allocations[job_id]
        if status == JobStatus.COMPLETED:
            total_completed += 1
            gpu_utilization += allocation['gpu_count']
        if status == JobStatus.FAILED:
            total_failed += 1
        total_jobs += 1
        job_results.append({
            'job_id': job_id,
            'status': status,
            'duration_ms': 0,
            'node': allocation['node_id'],
            'retries': summary['retries']
        })
        


    display_final_summary({
        "total_jobs": total_jobs,
        "completed": total_completed,
        "failed": total_failed,
        "total_time": elapsted,
        "job_results": [
            {"job_id": str, "status": str, "duration_ms": int,
             "node": str, "retries": int},
            ...
        ],
        "gpu_utilization": float,
    })
    
