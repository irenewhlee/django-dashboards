from typing import Any, Dict, Iterable, List, Optional

from ..reporters import PipelineReporter
from ..tasks import Task
from .base import PipelineRunner


class Runner(PipelineRunner):
    def _task_can_be_ran(self, task: Task, ran_pipeline_tasks: List[str]):
        not_all_parents_ran = any(
            map(
                lambda parent: parent not in ran_pipeline_tasks,
                getattr(task.cleaned_config, "parents", []),
            )
        )

        return task.pipeline_task not in ran_pipeline_tasks and not not_all_parents_ran

    def _get_next_task(
        self,
        tasks: List[Task],
        ran_pipeline_tasks: List[str],
    ) -> Iterable[Task]:
        while True:
            task = next(
                (t for t in tasks if self._task_can_be_ran(t, ran_pipeline_tasks)),
                None,
            )

            if task:
                yield task
            else:
                break

    def start_runner(
        self,
        pipeline_id: str,
        run_id: str,
        tasks: List[Task],
        input_data: Dict[str, Any],
        reporter: PipelineReporter,
        obj: Optional[Any] = None,
    ) -> bool:

        object_lookup = self.object_lookup(obj=obj)

        self._report_pipeline_running(
            pipeline_id=pipeline_id,
            reporter=reporter,
            object_lookup=object_lookup,
        )

        ran_pipeline_tasks: List[str] = []

        for task in self._get_next_task(tasks, ran_pipeline_tasks):
            res = task.start(
                pipeline_id=pipeline_id,
                run_id=run_id,
                input_data=input_data,
                reporter=reporter,
                object_lookup=object_lookup,
            )
            if res:
                ran_pipeline_tasks.append(task.pipeline_task)
            else:
                # if a task fails record all others have been canceled
                for t in (
                    _t
                    for _t in tasks
                    if _t.pipeline_task != task.pipeline_task
                    and _t.pipeline_task not in ran_pipeline_tasks
                ):
                    self._report_task_cancelled(
                        task=t,
                        reporter=reporter,
                        object_lookup=object_lookup,
                    )

                self._report_pipeline_error(
                    pipeline_id=pipeline_id,
                    reporter=reporter,
                    object_lookup=object_lookup,
                )

                return False

        self._report_pipeline_done(
            pipeline_id=pipeline_id,
            reporter=reporter,
            object_lookup=object_lookup,
        )

        return True
