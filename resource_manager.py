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
        # TODO 1: Initialize thread-safe tracking:
        #   - self._lock = threading.Lock()
        #   - self._condition = threading.Condition(self._lock)
        #   - self._available = {node.id: node.available_gpus for node in cluster.nodes}
        #     (dict mapping node_id -> available GPU count)
        #   - self._allocations = {}  (dict mapping job_id -> GpuAllocation)
        #   - self._shutdown = False
        pass

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
        # TODO 2: Acquire self._condition (use `with self._condition:`), then:
        #   - Loop (while not self._shutdown):
        #       - Search self._available for a node with >= gpu_count available GPUs
        #       - If found:
        #           - Decrement self._available[node_id] by gpu_count
        #           - Call self._sdk.allocate_gpus(node_id, gpu_count, job_id)
        #           - Store the allocation in self._allocations[job_id]
        #           - Return the allocation
        #       - If not found:
        #           - Call self._condition.wait(timeout=timeout)
        #           - If wait returns False (timeout), return None
        #   - Return None if shutdown
        #
        # Handle InsufficientResourcesError from SDK:
        #   - If SDK raises it (shouldn't if we track correctly), update self._available and retry
        pass

    def release_gpus(self, job_id: str) -> None:
        """
        Release GPUs allocated to a job and notify waiting threads.

        Args:
            job_id: The job whose GPUs to release
        """
        # TODO 3: Acquire self._condition, then:
        #   - Look up the allocation in self._allocations[job_id]
        #   - Call self._sdk.release_gpus(allocation)
        #   - Increment self._available[allocation.node_id] by allocation.gpu_count
        #   - Remove from self._allocations
        #   - Call self._condition.notify_all() to wake up waiting threads
        pass

    def shutdown(self) -> None:
        """Signal shutdown and wake all waiting threads."""
        with self._condition:
            self._shutdown = True
            self._condition.notify_all()

    def get_status(self) -> dict:
        """Return current GPU availability (for display)."""
        with self._lock:
            return dict(self._available)
