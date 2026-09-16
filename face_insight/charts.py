from __future__ import annotations

from pathlib import Path

from pyecharts import options as opts
from pyecharts.charts import Bar, Gauge, Line, Page, Pie, Radar
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode

from .storage import AnalysisRecord


SCORE_LABELS = ["无人脸", "1分", "2分", "3分", "4分", "5分", "6分", "7分", "8分", "9分", "10分"]

PALETTE = [
    "#00e5c3", "#29b6f6", "#ffd54f", "#ff7043", "#ab47bc", "#26a69a",
    "#ef5350", "#66bb6a", "#ffa726", "#7e57c2", "#ec407a",
]

PAGE_BG = "#0d1220"


def _init() -> opts.InitOpts:
    return opts.InitOpts(
        width="100%",
        height="480px",
        theme=ThemeType.DARK,
        bg_color=PAGE_BG,
    )


def _dark_title(title: str, subtitle: str = "") -> opts.TitleOpts:
    return opts.TitleOpts(
        title=title,
        subtitle=subtitle,
        title_textstyle_opts=opts.TextStyleOpts(color="#e8eef6", font_size=20),
        subtitle_textstyle_opts=opts.TextStyleOpts(color="#8fa1b8"),
    )


def _darken_page(path: Path):
    html = path.read_text(encoding="utf-8")
    html = html.replace(
        "<body>",
        '<body style="background:#0d1220; color:#e8eef6;">',
        1,
    )
    path.write_text(html, encoding="utf-8")


def build_score_chart(keyword: str, score_counts: list[int], beauty_avg: float | None) -> Bar:
    avg_text = f"{beauty_avg:.2f}" if beauty_avg is not None else "无有效人脸"
    items = [
        opts.BarItem(
            name=SCORE_LABELS[index],
            value=value,
            itemstyle_opts=opts.ItemStyleOpts(
                color=PALETTE[index % len(PALETTE)],
                border_radius=[6, 6, 0, 0],
            ),
        )
        for index, value in enumerate(score_counts)
    ]
    bar = (
        Bar(init_opts=_init())
        .add_xaxis(SCORE_LABELS)
        .add_yaxis("图片数量", items)
        .set_global_opts(
            title_opts=_dark_title(f"{keyword} · 颜值分布", f"平均分 {avg_text}"),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=30, color="#8fa1b8"),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#3a4a6e")),
            ),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(
                    is_show=True,
                    linestyle_opts=opts.LineStyleOpts(color="#243354"),
                )
            ),
            legend_opts=opts.LegendOpts(pos_left="center", textstyle_opts=opts.TextStyleOpts(color="#8fa1b8")),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        )
    )
    if beauty_avg is not None:
        bar.set_series_opts(
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(y=beauty_avg, name="平均分")],
                linestyle_opts=opts.LineStyleOpts(color="#ffd54f", type_="dashed"),
                label_opts=opts.LabelOpts(color="#ffd54f"),
            )
        )
    return bar


def build_score_pie(keyword: str, score_counts: list[int]) -> Pie:
    data = [
        (SCORE_LABELS[index], value)
        for index, value in enumerate(score_counts)
        if value > 0
    ]
    if not data:
        data = [("暂无数据", 1)]
    return (
        Pie(init_opts=_init())
        .add(
            "占比",
            data,
            radius=["38%", "68%"],
            center=["50%", "56%"],
            label_opts=opts.LabelOpts(formatter="{b}: {c} 张", color="#e8eef6"),
        )
        .set_colors(PALETTE)
        .set_global_opts(
            title_opts=_dark_title(f"{keyword} · 构成占比"),
            legend_opts=opts.LegendOpts(
                pos_bottom="0%", pos_left="center", textstyle_opts=opts.TextStyleOpts(color="#8fa1b8")
            ),
        )
    )


def build_gauge(beauty_avg: float | None) -> Gauge:
    value = beauty_avg if beauty_avg is not None else 0
    subtitle = "综合颜值指数" if beauty_avg is not None else "本轮未检出有效人脸"
    return (
        Gauge(init_opts=_init())
        .add(
            "颜值指数",
            [("得分", value)],
            min_=0,
            max_=10,
            radius="82%",
            center=["50%", "58%"],
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color=[
                        {"offset": 0.0, "color": "#ff7043"},
                        {"offset": 0.5, "color": "#ffd54f"},
                        {"offset": 1.0, "color": "#00e5c3"},
                    ],
                    width=16,
                )
            ),
            detail_label_opts=opts.LabelOpts(
                formatter="{value}",
                font_size=34,
                color="#00e5c3",
                offset=[0, 30],
            ),
        )
        .set_global_opts(title_opts=_dark_title("颜值仪表盘", subtitle))
    )


def build_average_trend(records: list[AnalysisRecord]) -> Line:
    labels = [f"#{record.record_id} {record.keyword}" for record in records]
    values = [record.beauty_avg or 0 for record in records]
    return (
        Line(init_opts=_init())
        .add_xaxis(labels)
        .add_yaxis(
            "平均分",
            values,
            is_smooth=True,
            symbol="circle",
            symbol_size=10,
            label_opts=opts.LabelOpts(is_show=True, color="#e8eef6"),
            linestyle_opts=opts.LineStyleOpts(color="#00e5c3", width=3),
            itemstyle_opts=opts.ItemStyleOpts(color="#00e5c3"),
            areastyle_opts=opts.AreaStyleOpts(
                opacity=0.35,
                color=JsCode(
                    "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
                    "[{offset: 0, color: 'rgba(0,229,195,0.55)'}, "
                    "{offset: 1, color: 'rgba(0,229,195,0.02)'}])"
                ),
            ),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最高"),
                    opts.MarkPointItem(type_="min", name="最低"),
                ]
            ),
        )
        .set_global_opts(
            title_opts=_dark_title("历史平均分趋势"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30, color="#8fa1b8")),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#243354")
                )
            ),
        )
    )


def build_face_distribution(records: list[AnalysisRecord]) -> Pie:
    has_face = sum(sum(record.score_counts[1:]) for record in records)
    no_face = sum(record.score_counts[0] for record in records)
    return (
        Pie(init_opts=_init())
        .add(
            "人脸检出分布",
            [("有人脸", has_face), ("无人脸", no_face)],
            radius=["30%", "68%"],
            rosetype="radius",
            center=["50%", "56%"],
            label_opts=opts.LabelOpts(formatter="{b}: {c} 张", color="#e8eef6"),
        )
        .set_colors(["#00e5c3", "#ff7043"])
        .set_global_opts(title_opts=_dark_title("人脸检出分布"))
    )


def build_keyword_comparison(records: list[AnalysisRecord]) -> Bar:
    keywords: list[str] = []
    face_counts: dict[str, int] = {}
    no_face_counts: dict[str, int] = {}
    for record in records:
        if record.keyword not in face_counts:
            keywords.append(record.keyword)
            face_counts[record.keyword] = 0
            no_face_counts[record.keyword] = 0
        face_counts[record.keyword] += sum(record.score_counts[1:])
        no_face_counts[record.keyword] += record.score_counts[0]

    return (
        Bar(init_opts=_init())
        .add_xaxis(keywords)
        .add_yaxis(
            "有人脸",
            [face_counts[key] for key in keywords],
            itemstyle_opts=opts.ItemStyleOpts(color="#00e5c3", border_radius=[5, 5, 0, 0]),
        )
        .add_yaxis(
            "无人脸",
            [no_face_counts[key] for key in keywords],
            itemstyle_opts=opts.ItemStyleOpts(color="#ff7043", border_radius=[5, 5, 0, 0]),
        )
        .set_global_opts(
            title_opts=_dark_title("关键词检测结果对比"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30, color="#8fa1b8")),
            legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color="#8fa1b8")),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        )
    )


def build_score_radar(records: list[AnalysisRecord]) -> Radar:
    totals = [
        sum(record.score_counts[score] for record in records)
        for score in range(1, 11)
    ]
    max_value = max(totals) or 1
    indicators = [
        opts.RadarIndicatorItem(name=f"{score}分", max_=max_value)
        for score in range(1, 11)
    ]
    radar = (
        Radar(init_opts=_init())
        .add_schema(
            schema=indicators,
            splitarea_opt=opts.SplitAreaOpts(is_show=False),
            axisline_opt=opts.LineStyleOpts(color="#3a4a6e"),
        )
        .add(
            "累计分数分布",
            [totals],
            color="#29b6f6",
            linestyle_opts=opts.LineStyleOpts(color="#29b6f6", width=2),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.28, color="#29b6f6"),
        )
        .set_global_opts(title_opts=_dark_title("分数形状雷达"))
    )
    return radar


def save_score_chart(
    keyword: str,
    score_counts: list[int],
    beauty_avg: float | None,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    page = Page(page_title=f"{keyword} 分析报告", layout=Page.SimplePageLayout)
    page.add(
        build_gauge(beauty_avg),
        build_score_chart(keyword, score_counts, beauty_avg),
        build_score_pie(keyword, score_counts),
    )
    page.render(str(path))
    _darken_page(path)
    return path


def save_history_screen(records: list[AnalysisRecord], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    overall_avg = calculate_history_average(records)
    page = Page(page_title="人脸颜值数据分析系统大屏", layout=Page.DraggablePageLayout)
    page.add(
        build_gauge(overall_avg),
        build_average_trend(records),
        build_face_distribution(records),
        build_keyword_comparison(records),
        build_score_radar(records),
    )
    for record in records:
        page.add(build_score_chart(record.keyword, record.score_counts, record.beauty_avg))
        page.add(build_score_pie(record.keyword, record.score_counts))
    page.render(str(path))
    _darken_page(path)
    return path


def calculate_history_average(records: list[AnalysisRecord]) -> float | None:
    face_count = sum(sum(record.score_counts[1:]) for record in records)
    if face_count == 0:
        return None
    total = sum(
        sum(score * count for score, count in enumerate(record.score_counts))
        for record in records
    )
    return round(total / face_count, 2)
