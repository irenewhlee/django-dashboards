from typing import Any, Dict, List, Optional, Type

from django.utils import timezone

from pydantic import BaseModel, ValidationError

from wildcoeus.pipelines.log import logger
from wildcoeus.pipelines.reporters import BasePipelineReporter
from wildcoeus.pipelines.status import PipelineTaskStatus
from wildcoeus.pipelines.tasks.registry import task_registry


class BaseTaskConfig(BaseModel):
    parents: List[
        str
    ] = (
        []
    )  # task ids that are required to have finished before this task can be started


class BaseTask:
    pipeline_task: str  # The attribute this tasks is named against - set via __new__ on BasePipeline
    title: Optional[str] = ""
    ConfigType: Type[BaseTaskConfig] = BaseTaskConfig
    InputType: Optional[
        Type[BaseModel]
    ] = None  # todo: can this a django form which can then be rendered?

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        task_registry.register(cls)

    def __init__(
        self,
        config: Dict[str, Any] = {},
    ):
        self.task_id = task_registry.get_task_id(
            self.__module__, self.__class__.__name__
        )
        self.cleaned_config = self.clean_config(config)

    def clean_config(self, config: Dict[str, Any]):
        try:
            model = self.ConfigType(**(config or {}))
            return model
        except ValidationError as e:
            raise ConfigValidationError(self, e.json(indent=False))

    def clean_input_data(self, input_data: Dict[str, Any]):
        if input_data and self.InputType is None:
            raise InputValidationError(
                self, "Input data was provided when no input type was specified"
            )

        if self.InputType is None:
            return None

        try:
            model = self.InputType(**(input_data or {}))
            return model
        except ValidationError as e:
            raise InputValidationError(self, e.json(indent=False))

    def start(
        self,
        pipeline_id: str,
        run_id: str,
        input_data: Dict[str, Any],
        reporter: BasePipelineReporter,
    ):
        try:
            cleaned_data = self.clean_input_data(input_data)
            logger.debug(cleaned_data)

            reporter.report_task(
                pipeline_task=self.pipeline_task,
                task_id=self.task_id,
                status=PipelineTaskStatus.RUNNING,
                message="Task is running",
            )

            # record the task is running
            self.save(
                pipeline_id=pipeline_id,
                run_id=run_id,
                status=PipelineTaskStatus.RUNNING.value,
                started=timezone.now(),
                config=self.cleaned_config.dict() if self.cleaned_config else None,
                input_data=cleaned_data.dict() if cleaned_data else None,
            )

            # run the task
            self.run(pipeline_id, run_id, cleaned_data)

            # update the result as completed
            self.save(
                pipeline_id=pipeline_id,
                run_id=run_id,
                status=PipelineTaskStatus.DONE.value,
                completed=timezone.now(),
            )

            reporter.report_task(
                pipeline_task=self.pipeline_task,
                task_id=self.task_id,
                status=PipelineTaskStatus.DONE,
                message="Done",
            )

            return True
        except (InputValidationError, Exception) as e:
            status = PipelineTaskStatus.VALIDATION_ERROR if isinstance(e, InputValidationError) else PipelineTaskStatus.RUNTIME_ERROR
            self.handle_exception(reporter, pipeline_id, run_id, e, status)

        return False

    def run(
        self,
        pipeline_id: str,
        run_id: str,
        cleaned_data: Optional[BaseModel],
    ):  # pragma: no cover
        raise NotImplementedError("run not implemented")

    def handle_exception(self, reporter, pipeline_id, run_id, e, status):
        from ..models import PipelineExecution
        # If there is an error running the task record the error
        reporter.report_task(
            pipeline_task=self.pipeline_task,
            task_id=self.task_id,
            status=status,
            message=str(e),
        )

        # update the task result as failed
        self.save(
            pipeline_id=pipeline_id,
            run_id=run_id,
            status=status.value,
        )

        # update PipelineExecution (if present) as failed
        PipelineExecution.objects.filter(pipeline_id=pipeline_id, run_id=run_id).update(
            pipeline_id=pipeline_id,
            run_id=run_id,
            status=status.value,
        )

    def save(self, pipeline_id, run_id, status, **defaults):
        from ..models import TaskResult, PipelineExecution
        # add to the defaults
        defaults["status"] = status
        defaults["pipeline_task"] = self.pipeline_task,

        result, _ = TaskResult.objects.update_or_create(
            pipeline_id=pipeline_id,
            task_id=self.task_id,
            run_id=run_id,
            defaults=defaults,
        )

        # if all tasks have ran then flag the PipelineExecution as complete
        if status == PipelineTaskStatus.DONE.value:
            if TaskResult.objects.not_completed(run_id=run_id).count() == 0:
                PipelineExecution.objects.filter(pipeline_id=pipeline_id, run_id=run_id).update(status=PipelineTaskStatus.DONE.value)

        return result


class BaseTaskError(Exception):
    def __init__(self, task: BaseTask, msg: str):
        super().__init__(msg)
        self.task = task
        self.msg = msg


class ConfigValidationError(BaseTaskError):
    pass


class InputValidationError(BaseTaskError):
    pass
