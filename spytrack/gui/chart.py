from PyQt5.QtChart import QChartView, QBarSeries, QBarSet, \
    QBarCategoryAxis, QChart, QLegend
from PyQt5.QtGui import QPainter
from analyze.stats import PieChartData
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

    def draw(self, chart_data: PieChartData) -> None:
        # series = QPieSeries()
        # for project, duration in chart_data.data.items():
        #   series.append("{} ({} s)".format(project, int(duration)), duration)
        # self.chart_view.setRenderHint(QPainter.Antialiasing)
        # self.chart_view.chart().removeAllSeries()
        # self.chart_view.chart().addSeries(series)

        # TODO redo with stacked bar chart
        series = QBarSeries()
        bar_set = QBarSet('Default')
        categories = []
        for project, duration in chart_data.data.items():
            if project == self.config.projects.none_project:
                project = 'None'
            categories.append(project)
            bar_set.append(duration)
        series.append(bar_set)
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)

        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        self.chart.setAxisX(axis_x)
        series.attachAxis(axis_x)

        self.initialized = True

    def reload_config(self, config: Config) -> None:
        self.config = config
