from __future__ import annotations

"""
Thread-Safe GPU Resource Manager
==================================
Manages GPU allocation across cluster nodes using Condition variables.

You will implement:
- Thread-safe GPU tracking with Lock
- Blocking GPU acquisition with Condition (wait if no resources available)
- GPU release with notification to waiting threads
"""

import threading
from sdk_do_not_edit import GpuClusterSDK, ClusterInfo, GpuAllocation, InsufficientResourcesError

MAX_NODES = 4

class ResourceManager:
    """
    Manages GPU resources across the cluster.

    Uses a Condition variable so that threads requesting GPUs can
    wait (block) until resources become available, rather than
    busy-polling.
    """

    def __init__(self, sdk: GpuClusterSDK, cluster: ClusterInfo):
        """
        Args:
            sdk: The GPU cluster SDK
            cluster: Cluster info with node details
        """
        self._sdk = sdk
        self._cluster = cluster
        self._cond = threading.Condition()
        self._available = {node.id: node.available_gpus for node in self._cluster.nodes}
        self._allocations = {}
        self._allocation_history = {}  # persists after release for reporting
        self._shutdown = False

    def acquire_gpus(self, job_id: str, gpu_count: int, timeout: float = 30.0) -> GpuAllocation | None:
        """
        Acquire GPUs for a job. Blocks until resources are available.

        Args:
            job_id: The job requesting resources
            gpu_count: Number of GPUs needed (1 or 2)
            timeout: Max seconds to wait for resources

        Returns:
            GpuAllocation if successful, None if timeout or shutdown
        """
        with self._cond:
            # while not shutdown
            while not self._shutdown:
                # Check all nodes first
                target_node = None
                for node_id, avail_gpus in self._available.items():
                    if avail_gpus >= gpu_count:
                        target_node = node_id
                        break
                
                # allocate gpus if target is found
                if target_node is not None:
                    try:
                        # allocate gpus
                        alloc_gpu = self._sdk.allocate_gpus(target_node, gpu_count, job_id)
                        self._allocations[job_id] = alloc_gpu
                        self._allocation_history[job_id] = {'node_id': target_node, 'gpu_count': gpu_count}
                        self._available[target_node] -= gpu_count
                        return alloc_gpu
                    except InsufficientResourcesError as e:
                        self._available[target_node] = 0 # update tracking
                        continue # retry
                
                # wait till we get gpu available signal
                if not self._cond.wait(timeout=timeout):
                    return None            

            return None

    def release_gpus(self, job_id: str) -> None:
        """
        Release GPUs allocated to a job and notify waiting threads.

        Args:
            job_id: The job whose GPUs to release
        """
        with self._cond:
            try:
                allocation = self._allocations.pop(job_id)
                self._sdk.release_gpus(allocation)
                self._available[allocation.node_id] += allocation.gpu_count

                self._cond.notify_all()
            except Exception as e:
                print(f"Error releasing gpus", e)

    def shutdown(self) -> None:
        """Signal shutdown and wake all waiting threads."""
        with self._cond:
            self._shutdown = True
            self._cond.notify_all()

    def get_status(self) -> dict:
        """Return current GPU availability (for display)."""
        with self._cond:
            return dict(self._available)
