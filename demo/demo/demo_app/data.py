from datorum.component.chart import ChartData
from demo.demo_app.models import FlatText


class DashboardData:
    def _apply_filter_age_range(self):
        pass

    @staticmethod
    def fetch_html(request) -> str:
        return FlatText.objects.all().first().text

    @staticmethod
    def fetch_gauge_chart_data(request) -> ChartData:
        return ChartData(
            data=[ChartData.Gauge(
                domain={"x": [0, 1], "y": [0, 1]},
                value=2700,
                title={"text": "Average RPM"},
                mode=ChartData.Gauge.Mode.STANDARD,
            )]
        )

    @staticmethod
    def fetch_gauge_chart_data_two(request) -> ChartData:
        return ChartData(
            data=[ChartData.Gauge(
                domain={"x": [0, 1], "y": [0, 1]},
                value=45,
                title={"text": "MPG"},
                mode=ChartData.Gauge.Mode.DELTA,
                delta={"reference": 38},
                gauge={
                    "axis": {"range": [None, 50]},
                    "steps": [
                        {"range": [0, 25], "color": "lightgray"},
                        {"range": [25, 40], "color": "gray"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 49,
                    },
                }
            )]
        )

    @staticmethod
    def fetch_bar_chart_data(request) -> ChartData:
        return ChartData(
            data=[ChartData.Trace(
                x=["giraffes", "orangutans", "monkeys"],
                y=[20, 14, 23],
                type=ChartData.Trace.Type.BAR,
            )]
        )

    @staticmethod
    def fetch_stacked_bar_chart_data(request) -> ChartData:
        return ChartData(
            data=[
                ChartData.Trace(
                    x=["giraffes", "orangutans", "monkeys"],
                    y=[20, 14, 23],
                    name="SF Zoo",
                    type=ChartData.Trace.Type.BAR,
                ),
                ChartData.Trace(
                    x=["giraffes", "orangutans", "monkeys"],
                    y=[12, 18, 29],
                    name="LA Zoo",
                    type=ChartData.Trace.Type.BAR,
                ),
            ],
            layout={"barmode": "stack"}
        )


    @staticmethod
    def fetch_bubble_chart_data(request) -> ChartData:
        return ChartData(
            data=[ChartData.Trace(
                x=[1, 2, 3, 4],
                y=[10, 11, 12, 13],
                mode=ChartData.Trace.Mode.SCATTER,
                marker={"size": [40, 60, 80, 100]},
            )]
        )

    @staticmethod
    def fetch_scatter_chart_data(request) -> ChartData:
        na = ChartData.Trace(
            x=[52698, 43117],
            y=[53, 31],
            mode=ChartData.Trace.Mode.SCATTER,
            name="North America",
            text=["United States", "Canada"],
            marker={
                "color": "rgb(164, 194, 244)",
                "size": 12,
                "line": {"color": "white", "width": 0.5},
            },
            type=ChartData.Trace.Type.SCATTER,
        )

        europe = ChartData.Trace(
            x=[39317, 37236, 35650, 30066, 29570, 27159, 23557, 21046, 18007],
            y=[33, 20, 13, 19, 27, 19, 49, 44, 38],
            mode=ChartData.Trace.Mode.SCATTER,
            name="Europe",
            text=[
                "Germany",
                "Britain",
                "France",
                "Spain",
                "Italy",
                "Czech Rep.",
                "Greece",
                "Poland",
            ],
            marker={"color": "rgb(255, 217, 102)", "size": 12},
            type=ChartData.Trace.Type.SCATTER,
        )

        asia = ChartData.Trace(
            x=[42952, 37037, 33106, 17478, 9813, 5253, 4692, 3899],
            y=[23, 42, 54, 89, 14, 99, 93, 70],
            mode=ChartData.Trace.Mode.SCATTER,
            name="Asia/Pacific",
            text=[
                "Australia",
                "Japan",
                "South Korea",
                "Malaysia",
                "China",
                "Indonesia",
                "Philippines",
                "India",
            ],
            marker={"color": "rgb(234, 153, 153)", "size": 12},
            type=ChartData.Trace.Type.SCATTER,
        )

        # Very noddy example of filtering, should and could validate against the form class itself :)
        filter_country = request.GET.get("country")
        if filter_country and filter_country != "all":
            return ChartData(data={"na": [na], "europe": [europe], "asia": [asia]}[filter_country])

        return ChartData(data=[na, europe, asia])

    @staticmethod
    def fetch_table_data(request):
        """
        Mock return some results for tabular.
        """
        data = [
            {
                "id": 1,
                "name": "Oli Bob",
                "progress": 12,
                "gender": "male",
                "rating": 1,
                "col": "red",
                "dob": "19/02/1984",
                "car": 1,
            },
            {
                "id": 2,
                "name": "Mary May",
                "progress": 1,
                "gender": "female",
                "rating": 2,
                "col": "blue",
                "dob": "14/05/1982",
                "car": True,
            },
            {
                "id": 3,
                "name": "Christine Lobowski",
                "progress": 42,
                "gender": "female",
                "rating": 0,
                "col": "green",
                "dob": "22/05/1982",
                "car": "true",
            },
            {
                "id": 4,
                "name": "Brendon Philips",
                "progress": 100,
                "gender": "male",
                "rating": 1,
                "col": "orange",
                "dob": "01/08/1980",
            },
            {
                "id": 5,
                "name": "Margret Marmajuke",
                "progress": 16,
                "gender": "female",
                "rating": 5,
                "col": "yellow",
                "dob": "31/01/1999",
            },
            {
                "id": 6,
                "name": "Frank Harbours",
                "progress": 38,
                "gender": "male",
                "rating": 4,
                "col": "red",
                "dob": "12/05/1966",
                "car": 1,
            },
        ]

        return {"last_page": 1, "data": data}
