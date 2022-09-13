from datorum.component import CTA, HTML, Chart, Form, Map, Stat, Table, Text
from datorum.dashboard import Dashboard
from datorum.component.layout import HR
from datorum.component.layout import HTML as LayoutHTML
from datorum.component.layout import (
    Card,
    Div,
    Header,
    ComponentLayout,
    Tab,
    TabContainer,
)
from datorum.permissions import IsAdminUser
from django.urls import reverse_lazy

from demo.demo_app.data import DashboardData
from demo.demo_app.forms import AnimalForm, ExampleForm


class DemoDashboardOne(Dashboard):
    link = CTA(
        href=reverse_lazy("datorum:dashboards:demodashboardonecustom_dashboard"),
        text="Find out more!",
        width=3,
    )
    text_example = Text(
        value="Rendered on load",
        cta=CTA(
            href=reverse_lazy("datorum:dashboards:demodashboardonecustom_dashboard"),
            text="Find out more!",
        ),
        width=6,
    )
    html_example = HTML(value="<strong>HTML also rendered on load</strong>")
    calculated_example = Text(defer=lambda _: "Deferred text")
    form_example = Form(
        form=AnimalForm,
        method="get",
        dependents=["chart_example", "stacked_chart_example"],
        width=3,
    )
    chart_example = Chart(defer=DashboardData.fetch_bar_chart_data)
    stacked_chart_example = Chart(defer=DashboardData.fetch_stacked_bar_chart_data)
    bubble_chart_example = Chart(defer=DashboardData.fetch_bubble_chart_data)
    line_chart_example = Chart(
        defer=DashboardData.fetch_scatter_chart_data,
        filter_form=ExampleForm,
        dependents=["stat_three"],
    )
    stat_one = Stat(value={"text": "100%", "sub_text": "increase"})
    stat_two = Stat(value={"text": "88%", "sub_text": "increase"})
    stat_three = Stat(
        defer=lambda request: {
            "text": "33%",
            "sub_text": request.GET.get("country", "all"),
        }
    )
    free_text_example = HTML(defer=DashboardData.fetch_html)
    gauge_one = Chart(defer=DashboardData.fetch_gauge_chart_data)
    gauge_two = Chart(defer=DashboardData.fetch_gauge_chart_data_two)
    # table_example = Table(defer=DashboardData.fetch_table_data)
    # table_example_not_deferred = Table(
    #     value=TableData(
    #         headers=[],
    #         rows=[
    #             {
    #                 "id": 1,
    #                 "name": "Oli Bob",
    #                 "progress": 12,
    #                 "gender": "male",
    #                 "rating": 1,
    #                 "col": "red",
    #                 "dob": "19/02/1984",
    #                 "car": 1,
    #             }
    #         ],
    #     )
    # )
    scatter_map_example = Map(defer=DashboardData.fetch_scatter_map_data)
    choropleth_map_example = Map(defer=DashboardData.fetch_choropleth_map_data)

    class Meta:
        name = "Dashboard One"



class DemoDashboardOneCustom(DemoDashboardOne):
    template_name = "demo/custom.html"


class DemoDashboardOneVary(DemoDashboardOne):
    chart_example = Chart(defer=DashboardData.fetch_bar_chart_data, width=12)
    calculated_example = Text(defer=lambda _: "some calculated text", width=3)
    table_example = Table(defer=DashboardData.fetch_table_data, width=12)

    class Meta:
        name = "Dashboard One Vary"

    class Layout(Dashboard.Layout):
        components = ComponentLayout(
            Header("Header", size=2),
            LayoutHTML(
                html="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin nec vestibulum orci. Sed ac eleifend diam. Duis quis congue ex. Mauris at bibendum est, nec bibendum ipsum. Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            Card(
                "text_example",
                "html_example",
            ),
            Card(
                Div("stat_one"),
                Div("stat_two"),
                Div("stat_three"),
                Div(
                    "stat_one",
                    "stat_two",
                    "stat_three",
                ),
            ),
            HR(),
            Header("Tab Example", size=3),
            TabContainer(
                Tab(
                    "Calculated Example",
                    "calculated_example",
                ),
                Tab(
                    "Chart Example",
                    "chart_example",
                ),
                Tab(
                    "Table Example",
                    "table_example",
                ),
                Tab(
                    "Gauge Example",
                    "gauge_two",
                ),
            ),
        )


class DemoDashboardAdmin(Dashboard):
    permission_classes = [IsAdminUser]
    admin_text = Text(value="Admin Only Text")
    scatter_map_example = Map(defer=DashboardData.fetch_scatter_map_data)
    choropleth_map_example = Map(defer=DashboardData.fetch_choropleth_map_data)

    class Meta:
        name = "Admin Dashboard"
