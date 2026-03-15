from __future__ import annotations
from collections import defaultdict
import heapq

"""
Job Dependency Resolver
========================
Resolves job execution order using topological sort.

You will implement:
- Building an adjacency list from job dependencies
- Topological sort using Kahn's algorithm
- Cycle detection
"""

from sdk_do_not_edit import Job


class CyclicDependencyError(Exception):
    """Raised when job dependencies contain a cycle."""
    pass


def build_dependency_graph(jobs: list[Job]) -> tuple[dict[str, list[str]], dict[str, int]]:
    """
    Build an adjacency list and in-degree count from job dependencies.

    Args:
        jobs: List of jobs with their dependencies

    Returns:
        Tuple of:
        - adjacency: dict mapping job_id -> list of job_ids that depend on it
          (i.e., if B depends on A, then adjacency[A] contains B)
        - in_degree: dict mapping job_id -> number of dependencies it has
    """
    adjacency = {}
    in_degree = {}

    for job in jobs:
        adjacency[job.id] = []
        in_degree[job.id] = 0

    for job in jobs:
        for dep in job.dependencies:
            adjacency[dep].append(job.id)
            in_degree[job.id] += 1
    
    return (adjacency, in_degree)


def topological_sort(jobs: list[Job]) -> list[str]:
    """
    Return job IDs in a valid execution order using Kahn's algorithm.

    Jobs with no dependencies come first. Among jobs at the same "level",
    higher priority jobs come first (priority 5 > priority 1).

    Args:
        jobs: List of all jobs

    Returns:
        List of job IDs in execution order

    Raises:
        CyclicDependencyError: If dependencies contain a cycle
    """
    adjacency, in_degree = build_dependency_graph(jobs)

    # build {job_id: job}
    jid_to_job = {job.id: job for job in jobs}

    # create queue with jobs with in degree of 0
    queue = []
    for job_id, indegree in in_degree.items():
        if indegree == 0:
            heapq.heappush(queue, (-jid_to_job[job_id].priority, job_id))


    ordered_jobs = []

    while queue:
        # pop from queue
        _, job = heapq.heappop(queue)
        ordered_jobs.append(job)

        # decrement next jobs in degree and add to queue if it's 0
        for next_job in adjacency[job]:
            in_degree[next_job] -= 1
            if in_degree[next_job] == 0:
                heapq.heappush(queue, (-jid_to_job[next_job].priority, next_job))
    
    # detect cycle
    if len(ordered_jobs) != len(jobs):
        raise CyclicDependencyError("Cycle detected in job dependencies")
    
    return ordered_jobs
