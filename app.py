"""
Application Orchestrator
=========================
Wires together all components and runs the job scheduler.
"""

import time
import threading
from sdk_do_not_edit import GpuClusterSDK
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

    # TODO 17: Initialize components
    #   - resource_manager = ResourceManager(sdk, cluster)
    #   - scheduler = JobScheduler(jobs, execution_order)
    #   - stop_event = threading.Event()
    #   - shutdown_handler = ShutdownHandler(stop_event, resource_manager, scheduler)
    #   - shutdown_handler.register()

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
    pass
