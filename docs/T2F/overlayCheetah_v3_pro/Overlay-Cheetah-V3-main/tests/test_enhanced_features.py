"""
Tests for the enhanced autocoder features
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autocoder.core.template_matcher import TemplateMatcher
from autocoder.core.dependency_resolver import DependencyResolver, Task
from autocoder.core.parallel_generator import ParallelGenerator


class TestTemplateMatcher:
    """Tests for smart template matching"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.templates_dir = self.temp_dir / "templates"
        self.templates_dir.mkdir()

        # Create sample templates
        (self.templates_dir / "python").mkdir()
        (self.templates_dir / "python" / "api.py.j2").write_text("# API template")
        (self.templates_dir / "python" / "generic.py.j2").write_text("# Generic Python")
        (self.templates_dir / "javascript").mkdir()
        (self.templates_dir / "javascript" / "component.js.j2").write_text(
            "// Component"
        )
        (self.templates_dir / "generic.txt").write_text("Generic text")

    def teardown_method(self):
        """Cleanup test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_template_index_building(self):
        """Test that template index is built correctly"""
        matcher = TemplateMatcher(self.templates_dir)

        assert len(matcher.template_index) > 0
        assert "python/api.py.j2" in matcher.template_index
        assert "javascript/component.js.j2" in matcher.template_index

    def test_keyword_extraction(self):
        """Test keyword extraction from filenames"""
        matcher = TemplateMatcher(self.templates_dir)

        keywords = matcher._extract_keywords("api_endpoint_template")
        assert "api" in keywords
        assert "endpoint" in keywords
        assert "template" not in keywords  # Stop word

    def test_extension_match(self):
        """Test matching by file extension"""
        matcher = TemplateMatcher(self.templates_dir)

        match = matcher.match_template("src/api.py")
        assert match is not None
        assert match.score > 0
        assert "api.py.j2" in match.template_path

    def test_generic_fallback(self):
        """Test generic fallback for unknown patterns"""
        matcher = TemplateMatcher(self.templates_dir)

        # Create a generic fallback
        (self.templates_dir / "python" / "generic.j2").write_text("# Fallback")
        matcher = TemplateMatcher(self.templates_dir)  # Rebuild index

        match = matcher.match_template("src/unknown_file.py", min_score=0.0)
        assert match is not None

    def test_get_templates_by_extension(self):
        """Test getting templates by extension"""
        matcher = TemplateMatcher(self.templates_dir)

        py_templates = matcher.get_templates_by_extension("py")
        assert len(py_templates) > 0

        js_templates = matcher.get_templates_by_extension("js")
        assert len(js_templates) > 0


class TestDependencyResolver:
    """Tests for dependency resolution and topological sorting"""

    def test_add_task(self):
        """Test adding tasks to resolver"""
        resolver = DependencyResolver()

        task1 = Task(
            task_id="task1",
            output="file1.py",
            template="template1.j2",
            context={},
            dependencies=[],
        )

        resolver.add_task(task1)
        assert "task1" in resolver.tasks

    def test_topological_sort(self):
        """Test topological sorting of tasks"""
        resolver = DependencyResolver()

        task1 = Task(task_id="task1", output="base.py", template="t.j2", context={})
        task2 = Task(
            task_id="task2",
            output="derived.py",
            template="t.j2",
            context={},
            dependencies=["task1"],
        )
        task3 = Task(
            task_id="task3",
            output="final.py",
            template="t.j2",
            context={},
            dependencies=["task2"],
        )

        resolver.add_task(task1)
        resolver.add_task(task2)
        resolver.add_task(task3)

        sorted_tasks = resolver.get_sorted_tasks()

        assert len(sorted_tasks) == 3
        assert sorted_tasks[0].task_id == "task1"
        assert sorted_tasks[1].task_id == "task2"
        assert sorted_tasks[2].task_id == "task3"

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies"""
        resolver = DependencyResolver()

        task1 = Task(
            task_id="task1",
            output="a.py",
            template="t.j2",
            context={},
            dependencies=["task2"],
        )
        task2 = Task(
            task_id="task2",
            output="b.py",
            template="t.j2",
            context={},
            dependencies=["task1"],
        )

        resolver.add_task(task1)
        resolver.add_task(task2)

        with pytest.raises(ValueError, match="Circular dependency"):
            resolver.get_sorted_tasks()

    def test_dependency_inference(self):
        """Test automatic dependency inference"""
        resolver = DependencyResolver()

        context_task = Task(
            task_id="t1", output="src/context.tsx", template="t.j2", context={}
        )
        component_task = Task(
            task_id="t2", output="src/component.tsx", template="t.j2", context={}
        )

        resolver.add_task(context_task)
        resolver.add_task(component_task)

        # Infer dependencies
        resolver.infer_dependencies()

        # Component should depend on context
        assert "t1" in component_task.dependencies

    def test_parallel_batches(self):
        """Test grouping tasks into parallel batches"""
        resolver = DependencyResolver()

        # Independent tasks
        task1 = Task(task_id="task1", output="a.py", template="t.j2", context={})
        task2 = Task(task_id="task2", output="b.py", template="t.j2", context={})
        # Dependent task
        task3 = Task(
            task_id="task3",
            output="c.py",
            template="t.j2",
            context={},
            dependencies=["task1", "task2"],
        )

        resolver.add_task(task1)
        resolver.add_task(task2)
        resolver.add_task(task3)

        batches = resolver.get_parallel_batches()

        # First batch should have task1 and task2
        assert len(batches) == 2
        assert len(batches[0]) == 2
        assert len(batches[1]) == 1


class TestParallelGenerator:
    """Tests for parallel generation with incremental builds"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.templates_dir = self.temp_dir / "templates"
        self.output_dir = self.temp_dir / "output"
        self.templates_dir.mkdir()
        self.output_dir.mkdir()

        # Create sample template
        template_file = self.templates_dir / "simple.j2"
        template_file.write_text("Hello {{ name }}!")

    def teardown_method(self):
        """Cleanup test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_single_generation(self):
        """Test generating a single file"""
        generator = ParallelGenerator(
            templates_dir=self.templates_dir, output_dir=self.output_dir
        )

        result = generator._generate_single(
            task_id="test1",
            template_path="simple.j2",
            output_rel="output.txt",
            context={"name": "World"},
        )

        assert result.success
        assert (self.output_dir / "output.txt").exists()
        assert (self.output_dir / "output.txt").read_text() == "Hello World!"

    def test_parallel_generation(self):
        """Test parallel generation of multiple files"""
        generator = ParallelGenerator(
            templates_dir=self.templates_dir, output_dir=self.output_dir, max_workers=2
        )

        tasks = [
            {
                "task_id": "task1",
                "template": "simple.j2",
                "output": "file1.txt",
                "context": {"name": "Alice"},
            },
            {
                "task_id": "task2",
                "template": "simple.j2",
                "output": "file2.txt",
                "context": {"name": "Bob"},
            },
        ]

        results = generator.generate_parallel(tasks)

        assert len(results) == 2
        assert all(r.success for r in results)
        assert (self.output_dir / "file1.txt").read_text() == "Hello Alice!"
        assert (self.output_dir / "file2.txt").read_text() == "Hello Bob!"

    def test_incremental_builds(self):
        """Test incremental build (skip unchanged files)"""
        generator = ParallelGenerator(
            templates_dir=self.templates_dir, output_dir=self.output_dir
        )

        tasks = [
            {
                "task_id": "task1",
                "template": "simple.j2",
                "output": "file.txt",
                "context": {"name": "Test"},
            }
        ]

        # First generation
        results1 = generator.generate_sequential(tasks, incremental=True)
        assert results1[0].success
        assert not results1[0].skipped

        # Second generation (should skip)
        results2 = generator.generate_sequential(tasks, incremental=True)
        assert results2[0].success
        assert results2[0].skipped
        assert "unchanged" in results2[0].reason

    def test_dry_run(self):
        """Test dry run mode (no file writing)"""
        generator = ParallelGenerator(
            templates_dir=self.templates_dir, output_dir=self.output_dir
        )

        result = generator._generate_single(
            task_id="test1",
            template_path="simple.j2",
            output_rel="dry_run.txt",
            context={"name": "DryRun"},
            dry_run=True,
        )

        assert result.success
        assert result.skipped
        assert "dry run" in result.reason
        assert not (self.output_dir / "dry_run.txt").exists()

    def test_cache_clearing(self):
        """Test cache clearing functionality"""
        generator = ParallelGenerator(
            templates_dir=self.templates_dir, output_dir=self.output_dir
        )

        # Generate with cache
        tasks = [
            {
                "task_id": "task1",
                "template": "simple.j2",
                "output": "cached.txt",
                "context": {"name": "Cache"},
            }
        ]

        generator.generate_sequential(tasks, incremental=True)

        # Verify cache exists
        cache_files = list(generator.cache_dir.glob("*.hash"))
        assert len(cache_files) > 0

        # Clear cache
        generator.clear_cache()

        cache_files = list(generator.cache_dir.glob("*.hash"))
        assert len(cache_files) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
