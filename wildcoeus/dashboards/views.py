import json
from typing import Callable, Dict, Optional, Protocol, Type

from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView

from wildcoeus.dashboards.dashboard import Dashboard
from wildcoeus.dashboards.exceptions import DashboardNotFoundError
from wildcoeus.dashboards.utils import get_dashboard_class


class HasValueProtocol(Protocol):
    dashboard_class: Type[Dashboard]
    kwargs: Dict
    get_dashboard_kwargs: Callable


class DashboardObjectMixin:
    dashboard_class: Optional[Dashboard] = None

    def get_dashboard_kwargs(self: HasValueProtocol, request: HttpRequest) -> dict:
        kwargs = {"request": request}
        if self.dashboard_class:
            kwargs[self.dashboard_class._meta.lookup_kwarg] = self.kwargs.get(
                self.dashboard_class._meta.lookup_kwarg
            )

        return kwargs

    def get_dashboard(self: HasValueProtocol, request: HttpRequest) -> Dashboard:
        if not self.dashboard_class:
            try:
                self.dashboard_class = get_dashboard_class(
                    self.kwargs["app_label"], self.kwargs["dashboard"]
                )
            except DashboardNotFoundError as e:
                raise Http404(str(e))

        has_permissions = self.dashboard_class.has_permissions(request=request)
        if not has_permissions:
            raise PermissionDenied()

        return self.dashboard_class(**self.get_dashboard_kwargs(request=request))


class DashboardView(DashboardObjectMixin, TemplateView):
    """
    Dashboard view, allows a single Dashboard to be auto rendered.
    """

    template_name: str = "wildcoeus/dashboards/dashboard.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**{"dashboard": self.get_dashboard(request)})
        return self.render_to_response(context)


class ComponentView(DashboardObjectMixin, TemplateView):
    """
    Component view, partial rendering of a single component to support HTMX calls.
    """

    template_name: str = "wildcoeus/dashboards/components/partial.html"

    def is_ajax(self):
        return self.request.headers.get("x-requested-with") == "XMLHttpRequest"

    def get(self, request: HttpRequest, *args, **kwargs):
        dashboard = self.get_dashboard(request)
        component = self.get_partial_component(dashboard)

        if self.is_ajax() and component:
            filters = request.GET.dict()
            # Return json, calling the deferred value.
            return HttpResponse(
                json.dumps(
                    component.get_value(
                        request=self.request, call_deferred=True, filters=filters
                    ),
                    cls=DjangoJSONEncoder,
                ),
                content_type="application/json",
            )
        else:
            context = self.get_context_data(
                **{"component": component, "dashboard": dashboard}
            )

            return self.render_to_response(context)

    def get_partial_component(self, dashboard):
        for component in dashboard.get_components():
            if component.key == self.kwargs["component"]:
                return component

        raise Http404(
            f"Component {self.kwargs['component']} does not exist in dashboard {self.dashboard_class.class_name()}"
        )


class FormComponentView(ComponentView):
    """
    Form Component view, partial rendering of dependant components to support HTMX calls.
    """

    template_name: str = "wildcoeus/dashboards/components/partial.html"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        dashboard = self.get_dashboard(request)
        component = self.get_partial_component(dashboard)
        form = component.get_form(request=request)
        if form.is_valid():
            form.save()
            if self.is_ajax():
                return HttpResponse({"success": True}, content_type="application/json")

            return HttpResponseRedirect(component.get_absolute_url())

        return self.get(request, *args, **kwargs)
