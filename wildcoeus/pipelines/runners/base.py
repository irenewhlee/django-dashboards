from graphlib import TopologicalSorter
from typing import Any, Dict, List, Optional

from wildcoeus.pipelines import PipelineReporter
from wildcoeus.pipelines.status import PipelineTaskStatus
from wildcoeus.pipelines.tasks import Task


class PipelineRunner:
    @staticmethod
    def _report_task_cancelled(
        task: Task,
        run_id: str,
        reporter: PipelineReporter,
        serializable_pipeline_object: Optional[Dict[str, Any]] = None,
        serializable_task_object: Optional[Dict[str, Any]] = None,
    ):
        reporter.report_task(
            pipeline_task=task.pipeline_task,
            task_id=task.task_id,
            run_id=run_id,
            status=PipelineTaskStatus.CANCELLED.value,
            message="There was an error running a different task",
            serializable_pipeline_object=serializable_pipeline_object,
            serializable_task_object=serializable_task_object,
        )

    @staticmethod
    def _report_pipeline_pending(
        pipeline_id: str,
        run_id: str,
        reporter: PipelineReporter,
        serializable_pipeline_object: Optional[Dict[str, Any]] = None,
    ):
        reporter.report_pipeline(
            pipeline_id=pipeline_id,
            run_id=run_id,
            status=PipelineTaskStatus.PENDING.value,
            message="Pipeline is waiting to start",
            serializable_pipeline_object=serializable_pipeline_object,
        )

    @staticmethod
    def _report_pipeline_running(
        pipeline_id: str,
        run_id: str,
        reporter: PipelineReporter,
        serializable_pipeline_object: Optional[Dict[str, Any]] = None,
    ):
        reporter.report_pipeline(
            pipeline_id=pipeline_id,
            run_id=run_id,
            status=PipelineTaskStatus.RUNNING.value,
            message="Running",
            serializable_pipeline_object=serializable_pipeline_object,
        )

    @staticmethod
    def _report_pipeline_done(
        pipeline_id: str,
        run_id: str,
        reporter: PipelineReporter,
        serializable_pipeline_object: Optional[Dict[str, Any]] = None,
    ):
        reporter.report_pipeline(
            pipeline_id=pipeline_id,
            run_id=run_id,
            status=PipelineTaskStatus.DONE.value,
            message="Done",
            serializable_pipeline_object=serializable_pipeline_object,
        )

    @staticmethod
    def _report_pipeline_error(
        pipeline_id: str,
        run_id: str,
        reporter: PipelineReporter,
        serializable_pipeline_object: Optional[Dict[str, Any]] = None,
    ):
        reporter.report_pipeline(
            pipeline_id=pipeline_id,
            run_id=run_id,
            status=PipelineTaskStatus.RUNTIME_ERROR.value,
            message="Error",
            serializable_pipeline_object=serializable_pipeline_object,
        )

    @staticmethod
    def _get_task_graph(tasks: List[Task]) -> List[Task]:
        task_graph = {}

        for task in tasks:
            task_graph[task.pipeline_task] = set(
                getattr(task.cleaned_config, "parents", [])
            )

        task_order = tuple(TopologicalSorter(task_graph).static_order())
        tasks_ordered = sorted(tasks, key=lambda t: task_order.index(t.pipeline_task))
        return tasks_ordered

    def start(
        self,
        pipeline_id: str,
        run_id: str,
        tasks: List[Task],
        input_data: Dict[str, Any],
        reporter: PipelineReporter,
        pipeline_object: Optional[Any] = None,
    ):
        return self.start_runner(
            pipeline_id=pipeline_id,
            run_id=run_id,
            tasks=tasks,
            input_data=input_data,
            reporter=reporter,
            pipeline_object=pipeline_object,
        )

    def start_runner(
        self,
        pipeline_id: str,
        run_id: str,
        tasks: List[Task],
        input_data: Dict[str, Any],
        reporter: PipelineReporter,
        pipeline_object: Optional[Any] = None,
    ):  # pragma: no cover
        """
        Start runner, is called by start and applies any runner specific steps.
        """
        raise NotImplementedError
