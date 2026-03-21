# GPU Job Scheduler

**Practice Project 3** -- Condition Variables, Priority Queues, Topological Sort, Graceful Shutdown

Schedule GPU training jobs on a simulated cluster with 4 nodes and 8 GPUs. Jobs have
priorities, dependencies on other jobs, and varying GPU requirements. Your scheduler
must allocate limited resources, respect the dependency DAG, handle failures with
retries, and shut down gracefully on SIGINT/SIGTERM.

**Target time:** 45-60 minutes

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

---

## Project Structure

```
concurrency-project-3/
├── main.py                         # Entry point (pre-built)
├── requirements.txt                # Dependencies
├── sdk_do_not_edit/
│   ├── __init__.py                 # Package exports
│   └── gpu_cluster_sdk.py          # Mocked GPU cluster SDK (DO NOT EDIT)
├── display.py                      # Rich display utilities (DO NOT EDIT)
├── dependency_resolver.py          # Dependency resolution (Kahn's algorithm)
├── scheduler.py                    # Priority-based job scheduling
├── resource_manager.py             # GPU resource allocation
├── worker_pool.py                  # Worker thread pool
├── shutdown_handler.py             # Graceful shutdown handling
├── app.py                          # Application orchestrator
└── README.md
```

---

## What You're Building

A **GPU job scheduler** that:

1. **Resolves dependencies** -- determines a valid execution order using topological sort
2. **Prioritizes jobs** -- higher-priority jobs run first (using a max-heap via `heapq`)
3. **Manages GPU resources** -- allocates/releases GPUs across cluster nodes using `Condition` variables
4. **Executes jobs concurrently** -- a pool of worker threads pulls jobs and runs them
5. **Handles failures** -- retries failed jobs up to 2 times before marking them permanently failed
6. **Shuts down gracefully** -- catches SIGINT/SIGTERM, finishes running jobs, releases all resources

---

## Concepts Covered

| Concept                  | Where                          | Details                                                      |
|--------------------------|--------------------------------|--------------------------------------------------------------|
| `threading.Condition`    | `resource_manager.py`          | Wait/notify for GPU availability instead of busy-polling     |
| `threading.Lock`         | `scheduler.py`, `resource_manager.py` | Protect shared mutable state from data races          |
| `threading.Event`        | `scheduler.py`, `app.py`       | Signal completion across threads                             |
| `heapq` (priority queue) | `scheduler.py`                | Max-heap via negated priorities for job ordering             |
| Topological sort (Kahn)  | `dependency_resolver.py`       | Resolve DAG execution order with cycle detection             |
| `signal` handling        | `shutdown_handler.py`          | Catch SIGINT/SIGTERM for graceful shutdown                   |
| Resource management      | `resource_manager.py`          | Track and allocate limited GPU resources across nodes        |
| Retry pattern            | `scheduler.py`, `worker_pool.py` | Re-enqueue failed jobs with bounded retries               |

---

## Files To Modify

### `dependency_resolver.py`
Builds an adjacency list and in-degree map from job dependencies, then implements
Kahn's algorithm for topological sort with priority tie-breaking and cycle detection.

### `scheduler.py`
Initializes a priority queue (max-heap) with dependency-free jobs. Implements
`get_next_ready_job` (pop from heap), `mark_completed` (promote dependents),
and `mark_failed` (retry or permanently fail).

### `resource_manager.py`
Tracks per-node GPU availability with a `Condition` variable. `acquire_gpus` blocks
until a node has enough GPUs. `release_gpus` frees them and wakes waiting threads.

### `worker_pool.py`
Worker loop: gets next job, acquires GPUs, executes via SDK, handles success/failure,
and **always** releases GPUs in a `finally` block.

### `shutdown_handler.py`
Registers SIGINT/SIGTERM handlers. On signal, sets the stop event and calls
`resource_manager.shutdown()`. Cleanup releases any remaining allocations.

### `app.py`
Wires everything together: resolves dependencies, creates components, starts 3 worker
threads, waits for completion, and displays the final summary.

---

## The Job DAG

```
                    data-preprocess [1G] P5
                     /              \
            tokenizer-train       embedding-train
              [1G] P4                [1G] P4
                     \              /
                   base-model-train [2G] P5
                   /       |        \
    finetune-classif.  finetune-gen  finetune-qa
       [1G] P3         [2G] P3       [1G] P3
           |               |             |
    eval-classif.      eval-gen       eval-qa
       [1G] P2         [1G] P2       [1G] P2
                \          |         /
                   merge-results [1G] P1
                        |
                   deploy-model [2G] P1
```

12 jobs, 4 levels of parallelism, 8 total GPUs across 4 nodes (2 per node).

---

## SDK Reference

### `GpuClusterSDK` Methods

| Method                                    | Returns            | Latency      | Notes                                    |
|-------------------------------------------|--------------------|--------------|------------------------------------------|
| `get_cluster_info()`                      | `ClusterInfo`      | ~50ms        | 4 nodes, 2 GPUs each                    |
| `list_pending_jobs()`                     | `list[Job]`        | ~100ms       | 12 jobs forming a DAG                   |
| `allocate_gpus(node_id, gpu_count, job_id)` | `GpuAllocation`  | ~50ms        | Raises `InsufficientResourcesError`      |
| `release_gpus(allocation)`                | `None`             | ~30ms        |                                          |
| `execute_job(job_id, allocation)`         | `JobResult`        | 300-1500ms   | 15% failure, 5% catastrophic exception   |

### Types

- `ClusterInfo` -- `nodes: list[NodeInfo]`, `total_gpus: int`
- `NodeInfo` -- `id: str`, `total_gpus: int`, `available_gpus: int`
- `Job` -- `id`, `name`, `priority` (1-5), `gpu_count` (1-2), `dependencies: list[str]`, `estimated_duration_ms`
- `JobResult` -- `job_id`, `success: bool`, `duration_ms`, `error_msg`
- `GpuAllocation` -- `job_id`, `node_id`, `gpu_count`
- `JobStatus` -- enum: `PENDING`, `READY`, `RUNNING`, `COMPLETED`, `FAILED`

### Exceptions

- `InsufficientResourcesError` -- not enough GPUs on the requested node
- `JobExecutionError` -- catastrophic job failure (~5% chance)

---

## Suggested Implementation Order

1. **`dependency_resolver.py`** -- Pure logic, no threading. Build the graph, implement
   Kahn's algorithm, add cycle detection. Test mentally with the DAG above.

2. **`scheduler.py`** -- Initialize the heap with root jobs, implement get/complete/fail.
   Remember: negate priority for max-heap behavior with `heapq`.

3. **`resource_manager.py`** -- The trickiest file. Use `Condition` so `acquire_gpus`
   blocks efficiently. Make sure `release_gpus` calls `notify_all()`.

4. **`worker_pool.py`** -- The worker loop. The critical detail: GPU release MUST be
   in a `finally` block, or a failed job will leak GPUs and deadlock the system.

5. **`shutdown_handler.py`** -- Register signal handlers, set the stop event, wake
   blocked threads, clean up remaining allocations.

6. **`app.py`** -- Orchestrate everything. Create 3 daemon worker threads, wait for
   completion, build the results dict for `display_final_summary`.

---

## Tips

### Common Mistakes

- **Forgetting `finally` for GPU release** -- If a job fails or raises an exception
  and you don't release GPUs, those GPUs are lost forever. Other jobs will deadlock
  waiting for resources that will never be freed.

- **Busy-polling instead of `Condition.wait()`** -- Don't loop with `time.sleep(0.1)`
  checking GPU availability. Use `Condition` so the thread sleeps until notified.

- **`heapq` is a min-heap** -- Python's `heapq` gives you the smallest element first.
  For highest-priority-first, push `(-priority, job_id)` tuples.

- **Cycle detection** -- If Kahn's algorithm processes fewer jobs than exist, there's
  a cycle. Don't forget to raise `CyclicDependencyError`.

- **Promoting dependents too eagerly** -- When marking a job complete, check that
  ALL of a dependent's dependencies are complete, not just the one you finished.

- **Thread safety in `mark_completed`/`mark_failed`** -- These can be called from
  multiple worker threads simultaneously. The lock must protect all shared state.

### Debugging

- If the scheduler hangs, check: are GPUs being released? Is `notify_all()` called?
- If jobs run out of order, check: is the heap correctly using negated priorities?
- If not all jobs run, check: does `mark_completed` correctly promote dependents?

---

## Discussion Points

Think about these tradeoffs as you implement:

1. **Number of workers** -- We use 3 workers with 8 GPUs. What happens with 1 worker?
   With 8 workers? What's the optimal number and why?

2. **Retry strategy** -- We retry up to 2 times. What if a job keeps failing? Should
   we back off? Should we try a different node?

3. **Dependency failure** -- What happens when a job permanently fails? Should its
   dependents be automatically cancelled? (Current design: they stay PENDING forever.)

4. **Resource fragmentation** -- A 2-GPU job needs both GPUs on the same node. What
   if each node has 1 GPU free? Should we preempt a 1-GPU job?

5. **Fairness vs. priority** -- Lower-priority jobs might starve if high-priority
   jobs keep failing and retrying. How would you prevent this?

6. **Condition vs. Semaphore** -- Could you use a `Semaphore` instead of `Condition`
   for GPU tracking? What are the tradeoffs?
