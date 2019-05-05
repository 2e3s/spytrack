from typing import List
from PyQt5.QtChart import QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QChart, QLegend
from PyQt5.QtGui import QPainter
from analyze.matched_event import MatchedEvent
from analyze.stats import get_pie_chart
from config import Config


class Chart:
    def __init__(self, config: Config, chart_view: QChartView) -> None:
        self.chart_view = chart_view
        self.config = config
        self.initialized = False

        chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart: QChart = chart_view.chart()
        legend: QLegend = self.chart.legend()
        legend.hide()

        self.chart_view.repaint()

    def draw(self, matched_events: List[MatchedEvent]) -> None:
        chart_data = get_pie_chart(matched_events)
        # series = QPieSeries()
        # for project, duration in chart_data.data.items():
        #     series.append("{} ({} s)".format(project, int(duration)), duration)
        # self.chart_view.setRenderHint(QPainter.Antialiasing)
        # self.chart_view.chart().removeAllSeries()
        # self.chart_view.chart().addSeries(series)

        series = QBarSeries()
        bar_set = QBarSet('Default')
        categories = []
        for project, duration in chart_data.data.items():
            if project == self.config.none_project:
                project = 'None'
            categories.append("{} ({} s)".format(project, int(duration)))
            bar_set.append(duration)
        series.append(bar_set)
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)

        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        self.chart.setAxisX(axis_x)
        series.attachAxis(axis_x)

        self.initialized = True
