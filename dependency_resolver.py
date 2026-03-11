from __future__ import annotations

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
    # TODO 4: Build the graph:
    #   - Initialize adjacency = {job.id: [] for job in jobs}
    #   - Initialize in_degree = {job.id: 0 for job in jobs}
    #   - For each job, for each dep in job.dependencies:
    #       - Add job.id to adjacency[dep] (dep must complete before job can run)
    #       - Increment in_degree[job.id]
    #   - Return (adjacency, in_degree)
    pass


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
    # TODO 5: Implement Kahn's algorithm:
    #   - Call build_dependency_graph(jobs) to get adjacency and in_degree
    #   - Create a job_map: dict mapping job_id -> Job (for priority lookup)
    #   - Initialize a list (queue) with all jobs where in_degree == 0
    #   - Sort this initial queue by priority descending (highest priority first)
    #   - While the queue is not empty:
    #       - Pop the first job_id from the queue
    #       - Add it to the result list
    #       - For each dependent in adjacency[job_id]:
    #           - Decrement in_degree[dependent]
    #           - If in_degree[dependent] == 0, add to queue
    #       - Re-sort queue by priority descending
    #   - Return the result list
    #
    # TODO 6: Check for cycles:
    #   - After the algorithm, if len(result) != len(jobs), there's a cycle
    #   - Raise CyclicDependencyError with the job IDs that weren't processed
    pass
