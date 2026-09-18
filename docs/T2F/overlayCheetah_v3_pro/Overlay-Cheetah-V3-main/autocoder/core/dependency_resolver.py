"""
Task dependency analysis and topological sorting
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class Task:
    """Represents a code generation task"""

    task_id: str
    output: str
    template: str
    context: Dict[str, Any]
    weight: float = 1.0
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class DependencyResolver:
    """Resolves task dependencies and provides topological ordering"""

    def __init__(self):
        """Initialize dependency resolver"""
        self.tasks: Dict[str, Task] = {}
        self.graph: Dict[str, List[str]] = defaultdict(list)
        self.in_degree: Dict[str, int] = defaultdict(int)

    def add_task(self, task: Task):
        """Add a task to the resolver

        Args:
            task: Task to add
        """
        self.tasks[task.task_id] = task

        # Add to graph
        if task.task_id not in self.graph:
            self.graph[task.task_id] = []

        for dep in task.dependencies:
            self.graph[dep].append(task.task_id)
            self.in_degree[task.task_id] += 1

    def infer_dependencies(self):
        """Infer dependencies based on file patterns and context

        This looks for common patterns like:
        - context.tsx before component.tsx
        - types.ts before implementation files
        - config files before main files
        """
        for task_id, task in self.tasks.items():
            output_lower = task.output.lower()

            # Find potential dependencies
            for other_id, other_task in self.tasks.items():
                if task_id == other_id:
                    continue

                other_output_lower = other_task.output.lower()

                # Pattern-based inference
                if self._should_depend_on(output_lower, other_output_lower):
                    if other_id not in task.dependencies:
                        task.dependencies.append(other_id)
                        self.graph[other_id].append(task_id)
                        self.in_degree[task_id] += 1

    def _should_depend_on(self, file: str, dependency: str) -> bool:
        """Determine if file should depend on dependency based on patterns

        Args:
            file: Output file path
            dependency: Potential dependency file path

        Returns:
            True if file should depend on dependency
        """
        # Context files come before components
        if "context" in dependency and "component" in file:
            return True

        # Types before implementations
        if ("type" in dependency or "interface" in dependency) and (
            "type" not in file and "interface" not in file
        ):
            return True

        # Config before main
        if "config" in dependency and "main" in file:
            return True

        # Utils before other files
        if "util" in dependency and "util" not in file:
            return True

        # Index/barrel files last
        if "index" in file and "index" not in dependency:
            return True

        return False

    def get_sorted_tasks(self) -> List[Task]:
        """Get tasks in topological order (dependencies first)

        Returns:
            List of tasks in dependency order

        Raises:
            ValueError: If circular dependency detected
        """
        # Kahn's algorithm for topological sort
        sorted_tasks = []
        queue = deque()
        in_degree_copy = self.in_degree.copy()

        # Start with tasks that have no dependencies
        for task_id in self.tasks:
            if in_degree_copy[task_id] == 0:
                queue.append(task_id)

        while queue:
            task_id = queue.popleft()
            sorted_tasks.append(self.tasks[task_id])

            # Reduce in-degree for dependent tasks
            for dependent in self.graph[task_id]:
                in_degree_copy[dependent] -= 1
                if in_degree_copy[dependent] == 0:
                    queue.append(dependent)

        # Check for cycles
        if len(sorted_tasks) != len(self.tasks):
            raise ValueError("Circular dependency detected in tasks")

        return sorted_tasks

    def get_parallel_batches(self) -> List[List[Task]]:
        """Get tasks grouped in batches that can be executed in parallel

        Returns:
            List of batches, where each batch contains tasks that can run in parallel
        """
        batches = []
        in_degree_copy = self.in_degree.copy()
        remaining_tasks = set(self.tasks.keys())

        while remaining_tasks:
            # Find all tasks with no remaining dependencies
            batch = []
            for task_id in list(remaining_tasks):
                if in_degree_copy[task_id] == 0:
                    batch.append(self.tasks[task_id])
                    remaining_tasks.remove(task_id)

            if not batch:
                raise ValueError("Circular dependency detected in tasks")

            batches.append(batch)

            # Update in-degrees
            for task in batch:
                for dependent in self.graph[task.task_id]:
                    in_degree_copy[dependent] -= 1

        return batches

    def get_dependencies(self, task_id: str) -> List[str]:
        """Get direct dependencies for a task

        Args:
            task_id: Task identifier

        Returns:
            List of task IDs that this task depends on
        """
        if task_id not in self.tasks:
            return []
        return self.tasks[task_id].dependencies

    def get_dependents(self, task_id: str) -> List[str]:
        """Get tasks that depend on this task

        Args:
            task_id: Task identifier

        Returns:
            List of task IDs that depend on this task
        """
        return self.graph.get(task_id, [])
