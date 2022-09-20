from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Callable, Optional, Type, Union

from django.http import HttpRequest
from django.template import Context
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe

from datorum.forms import DatorumFilterForm, DatorumModelFilterForm
from datorum.types import ValueData


@dataclass
class Component:
    template_name: Optional[str] = None
    value: Optional[ValueData] = None
    defer: Optional[Callable[[HttpRequest], ValueData]] = None
    filter_form: Optional[Type[Union[DatorumFilterForm, DatorumModelFilterForm]]] = None
    dependents: Optional[list[str]] = None

    # attrs below can be set, but are inferred when fetching components from the dashboard class.
    key: Optional[str] = None
    dashboard_class: Optional[str] = None
    render_type: Optional[str] = None
    serializable: bool = True

    # replicated on LayoutBase TODO need to handle this better
    css_classes: Optional[str] = None
    width: Optional[int] = 6

    # attrs below should not be changed
    dependent_components: Optional[list["Component"]] = None

    @property
    def is_deferred(self) -> bool:
        return True if self.defer else False

    def get_value(self, request: HttpRequest = None, call_deferred=False) -> ValueData:
        if self.is_deferred and self.defer and call_deferred:
            value = self.defer(request)
        else:
            value = self.value

        if is_dataclass(value):
            value = asdict(value, dict_factory=value_render_encoder)

        return value

    def render(
        self, context: Context, htmx: Optional[bool] = None, call_deferred: bool = False
    ) -> str:
        request = context.get("request")
        context = {
            "request": request,
            "component": self,
            "rendered_value": self.get_value(
                request=request, call_deferred=call_deferred
            ),
            "htmx": self.is_deferred if htmx is None else htmx,
        }

        return mark_safe(render_to_string("datorum/components/component.html", context))

    def has_form(self):
        return True if self.filter_form else False

    def get_absolute_url(self):
        return reverse(
            "datorum:dashboard_component", args=[self.dashboard_class, self.key]
        )

    def __str__(self):
        return self.render()

    def __repr__(self):
        return f"{self.key}={self.value}"


@dataclass
class CTA(Component):
    template: str = "datorum/components/cta.html"
    href: str = ""
    text: str = ""

    def get_value(self, request: HttpRequest = None, call_deferred=False) -> str:
        return str(self.text)


def value_render_encoder(data) -> dict:
    def encode(o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        return o

    return dict((k, encode(v)) for k, v in data)
