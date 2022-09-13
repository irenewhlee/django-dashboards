from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import Callable, Optional, Type, Union

from datorum.forms import DatorumFilterForm, DatorumModelFilterForm
from datorum.types import ValueData
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe


@dataclass
class Component:
    template_name: str = None
    value: Optional[ValueData] = None
    defer: Optional[Callable[[HttpRequest], ValueData]] = None
    filter_form: Optional[Type[Union[DatorumFilterForm, DatorumModelFilterForm]]] = None
    dependents: Optional[list[str]] = None
    cta: Optional["CTA"] = None

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

    def for_render(self, request: HttpRequest, call_deferred=False) -> ValueData:
        if self.is_deferred and self.defer and call_deferred:
            value = self.defer(request)
        else:
            value = self.value

        if is_dataclass(value):
            value = asdict(value, dict_factory=dataclass_encoder)

        return value

    def has_form(self):
        return True if self.filter_form else False

    def get_absolute_url(self):
        return reverse(
            "datorum:dashboard_component", args=[self.dashboard_class, self.key]
        )

    def __str__(self):
        context = {
            "component": self,
            "rendered_value": self.value,
            "htmx": self.is_deferred,
        }

        return mark_safe(render_to_string("datorum/components/component.html", context))

    def __repr__(self):
        return f"{self.key}={self.value}"


@dataclass
class CTA(Component):
    template: str = "datorum/components/cta.html"
    href: str = None
    text: str = None

    def for_render(self, request: HttpRequest, call_deferred=False) -> str:
        return str(self.text)


def dataclass_encoder(data):
    def encode(o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        return o

    return dict((k, encode(v)) for k, v in data)
