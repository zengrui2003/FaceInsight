from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt


BG = RGBColor(0x0D, 0x12, 0x20)
PANEL = RGBColor(0x15, 0x1D, 0x30)
PANEL_LIGHT = RGBColor(0x1D, 0x28, 0x42)
ACCENT = RGBColor(0x00, 0xE5, 0xC3)
BLUE = RGBColor(0x29, 0xB6, 0xF6)
YELLOW = RGBColor(0xFF, 0xD5, 0x4F)
ORANGE = RGBColor(0xFF, 0x70, 0x43)
TEXT = RGBColor(0xE8, 0xEE, 0xF6)
MUTED = RGBColor(0x8F, 0xA1, 0xB8)


def add_slide(prs: Presentation, title: str):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG
    bg.line.fill.background()

    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(0.62), Inches(0.16), Inches(0.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()

    box = slide.shapes.add_textbox(Inches(0.92), Inches(0.48), Inches(11.6), Inches(0.8))
    frame = box.text_frame
    frame.word_wrap = True
    frame.text = title
    frame.paragraphs[0].font.size = Pt(28)
    frame.paragraphs[0].font.bold = True
    frame.paragraphs[0].font.color.rgb = TEXT
    return slide


def add_footer(slide, section: str):
    box = slide.shapes.add_textbox(Inches(0.92), Inches(6.95), Inches(11.5), Inches(0.4))
    frame = box.text_frame
    frame.text = section
    frame.paragraphs[0].font.size = Pt(12)
    frame.paragraphs[0].font.color.rgb = MUTED


def add_bullets(slide, lines, top=1.55, left=0.92, width=11.5, height=5.2, size=18):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = box.text_frame
    frame.word_wrap = True
    for index, line in enumerate(lines):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = line
        paragraph.font.size = Pt(size)
        paragraph.font.color.rgb = TEXT
        paragraph.space_after = Pt(10)
    return box


def add_card(slide, x, y, w, h, title, lines, color=ACCENT, title_size=14, text_size=12):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid()
    card.fill.fore_color.rgb = PANEL
    card.line.color.rgb = PANEL_LIGHT
    card.shadow.inherit = False

    title_box = slide.shapes.add_textbox(Inches(x + 0.22), Inches(y + 0.14), Inches(w - 0.44), Inches(0.4))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    title_frame.text = title
    title_frame.paragraphs[0].font.size = Pt(title_size)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = color

    body_box = slide.shapes.add_textbox(Inches(x + 0.22), Inches(y + 0.56), Inches(w - 0.44), Inches(h - 0.7))
    body_frame = body_box.text_frame
    body_frame.word_wrap = True
    for index, line in enumerate(lines):
        paragraph = body_frame.paragraphs[0] if index == 0 else body_frame.add_paragraph()
        paragraph.text = line
        paragraph.font.size = Pt(text_size)
        paragraph.font.color.rgb = TEXT
        paragraph.space_after = Pt(5)


def add_code_panel(slide, lines, top=1.55, left=0.92, width=11.5, height=3.6):
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    panel.fill.solid()
    panel.fill.fore_color.rgb = RGBColor(0x10, 0x19, 0x2C)
    panel.line.color.rgb = PANEL_LIGHT
    panel.shadow.inherit = False

    box = slide.shapes.add_textbox(Inches(left + 0.3), Inches(top + 0.2), Inches(width - 0.6), Inches(height - 0.4))
    frame = box.text_frame
    frame.word_wrap = True
    for index, line in enumerate(lines):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = line if line else " "
        paragraph.font.name = "Consolas"
        paragraph.font.size = Pt(13)
        paragraph.font.color.rgb = RGBColor(0xC9, 0xD6, 0xE8)
        paragraph.space_after = Pt(3)


def build(path: Path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG
    bg.line.fill.background()
    glow = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(2.28), Inches(0.2), Inches(1.4))
    glow.fill.solid()
    glow.fill.fore_color.rgb = ACCENT
    glow.line.fill.background()
    title_box = slide.shapes.add_textbox(Inches(1.3), Inches(2.3), Inches(11), Inches(1.3))
    title_frame = title_box.text_frame
    title_frame.text = "人脸颜值数据分析系统"
    title_frame.paragraphs[0].font.size = Pt(48)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = TEXT
    sub_box = slide.shapes.add_textbox(Inches(1.34), Inches(3.5), Inches(11), Inches(0.6))
    sub_frame = sub_box.text_frame
    sub_frame.text = "icrawler 爬取 · 百度智能云人脸检测 · SQLite 留存 · pyecharts 大屏 · tkinter 桌面端"
    sub_frame.paragraphs[0].font.size = Pt(18)
    sub_frame.paragraphs[0].font.color.rgb = ACCENT

    slide = add_slide(prs, "项目介绍：一句话讲清楚这个项目")
    add_bullets(
        slide,
        [
            "人脸颜值数据分析系统是一个从数据采集到智能分析再到可视化洞察的一体化桌面工具。",
            "输入一个关键词，程序自动完成：爬取图片 → 百度人脸检测 → 颜值打分 → 入库留存 → 生成可视化报告。",
            "课堂要求的三大核心全部保留：爬虫 icrawler、人脸检测百度智能云、图表 pyecharts。",
            "在课堂项目之上，我们拓展了桌面界面、三码在线配置、本地图片兜底、历史数据大屏、CSV 导出与自动打包。",
        ],
        size=20,
    )
    add_card(slide, 0.92, 5.0, 3.6, 1.6, "数据从哪来", ["icrawler 多线程图片爬虫", "支持本地图片文件夹兜底"], BLUE)
    add_card(slide, 4.86, 5.0, 3.6, 1.6, "智能在哪", ["百度 AipFace 人脸检测", "beauty 分数换算 1-10 分段"], ACCENT)
    add_card(slide, 8.82, 5.0, 3.6, 1.6, "价值在哪", ["SQLite 历史可追溯", "多维图表一眼看结论"], YELLOW)
    add_footer(slide, "① 项目介绍和展示")

    slide = add_slide(prs, "项目展示：录制一段 60-90 秒的演示视频")
    video = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.92), Inches(1.6), Inches(6.4), Inches(4.9))
    video.fill.solid()
    video.fill.fore_color.rgb = RGBColor(0x10, 0x19, 0x2C)
    video.line.color.rgb = ACCENT
    video.shadow.inherit = False
    vtext = video.text_frame
    vtext.word_wrap = True
    vtext.text = "▶  演示视频占位区"
    vtext.paragraphs[0].font.size = Pt(24)
    vtext.paragraphs[0].font.bold = True
    vtext.paragraphs[0].font.color.rgb = ACCENT
    vtext.paragraphs[0].alignment = 1
    for line in ["", "把录制好的 mp4 拖进这个区域即可", "插入方法：插入 → 视频 → 此设备"]:
        paragraph = vtext.add_paragraph()
        paragraph.text = line
        paragraph.font.size = Pt(13)
        paragraph.font.color.rgb = MUTED
        paragraph.alignment = 1
    add_card(
        slide, 7.7, 1.6, 4.7, 4.9, "视频录制脚本（照着录就行）",
        [
            "1. 双击“人脸颜值数据分析系统”，首次进入右上角“三码配置”。",
            "2. 输入 APP_ID / API_KEY / SECRET_KEY，点击保存并验证。",
            "3. 输入关键词“周杰伦”，点击开始分析。",
            "4. 展示进度条、日志滚动与状态徽章变化。",
            "5. 自动打开三联报告：颜值仪表盘 / 彩色柱状分布 / 环形占比。",
            "6. 再分析一个关键词，生成并拖动展示历史数据大屏。",
            "7. 最后点导出历史 CSV，展示表格数据。",
            "",
            "录制方式：Win+G 或 OBS，建议 60-90 秒，配一段简短解说。",
        ],
        BLUE, title_size=15, text_size=12,
    )
    add_footer(slide, "① 项目介绍和展示")

    slide = add_slide(prs, "关键代码讲解 1：数据采集与清洗")
    add_code_panel(
        slide,
        [
            "folder = root_dir / safe_folder_name(keyword)",
            "if folder.exists(): shutil.rmtree(folder)   # 清掉旧图，防止统计污染",
            "crawler = BingImageCrawler(feeder_threads=2, parser_threads=4,",
            "                           downloader_threads=8, storage={'root_dir': str(folder)})",
            "crawler.crawl(keyword=keyword, max_num=max_num)",
            "",
            "VALID_IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.bmp'}",
        ],
    )
    add_bullets(
        slide,
        [
            "讲解点 1：每次分析前清空关键词目录，保证统计口径干净。",
            "讲解点 2：feeder/parser/downloader 三类线程分工，体现 icrawler 的并发设计。",
            "讲解点 3：只接受四种常见图片格式，后续无效文件直接过滤。",
        ],
        top=5.35, height=1.5, size=15,
    )
    add_footer(slide, "② 关键代码讲解 · face_insight/crawler.py")

    slide = add_slide(prs, "关键代码讲解 2：百度检测与限流自愈")
    add_code_panel(
        slide,
        [
            "options = {'face_field': 'age,expression,beauty'}",
            "response = self.client.detect(base64_img, 'BASE64', options)",
            "",
            "while error_code == 18 and retries < max_retries:   # QPS 限流",
            "    time.sleep(1.2 * (retries + 1))                 # 1.2s → 2.4s → 3.6s → 4.8s",
            "    response = self.detect(path)",
            "    retries += 1",
            "",
            "return min(10, max(1, int(beauty // 10) + 1))       # 分数钳制，防止越界",
        ],
    )
    add_bullets(
        slide,
        [
            "讲解点 1：Base64 上传 + face_field 按需拉取字段，减少无效数据。",
            "讲解点 2：错误码 18 不再报错终止，而是自动退避重试，20 张图全程不中断。",
            "讲解点 3：请求间隔放宽到 1.1 秒，主动适配免费额度的 QPS 限制。",
        ],
        top=5.35, height=1.5, size=15,
    )
    add_footer(slide, "② 关键代码讲解 · face_insight/face_analysis.py")

    slide = add_slide(prs, "关键代码讲解 3：数据库设计与除零修复")
    add_code_panel(
        slide,
        [
            "def calculate_average(score_counts):",
            "    face_count = sum(score_counts[1:])",
            "    if face_count == 0:",
            "        return None                      # 课堂笔记里的除零 bug 在这里修复",
            "    total = sum(score * count for score, count in enumerate(score_counts))",
            "    return round(total / face_count, 2)",
            "",
            "INSERT INTO beauty_analysis(...) VALUES(?, ?, ...)   # 参数化 SQL",
        ],
    )
    add_bullets(
        slide,
        [
            "表结构：keyword、count_has_face、count_no_face、num_one-num_ten、beauty_avg。",
            "平均分只按有人脸图片计算；全无人脸时存 NULL，图表显示“无有效人脸”。",
            "pytest 覆盖分数聚合与除零分支，三个用例全部通过。",
        ],
        top=5.35, height=1.5, size=15,
    )
    add_footer(slide, "② 关键代码讲解 · face_insight/storage.py")

    slide = add_slide(prs, "关键代码讲解 4：多维可视化与界面线程")
    add_code_panel(
        slide,
        [
            "Gauge().add('颜值指数', [('得分', value)], min_=0, max_=10)",
            "Pie().add('占比', data, radius=['38%', '68%'])",
            "Line().add_yaxis('平均分', values, areastyle_opts=渐变面积)",
            "Radar().add_schema(schema=indicators)",
            "Page(layout=Page.DraggablePageLayout).render('人脸检测历史数据大屏.html')",
            "",
            "threading.Thread(target=self._analysis_worker, daemon=True).start()",
            "self.after(120, self._poll_worker_events)      # queue 消息驱动 UI 刷新",
        ],
    )
    add_bullets(
        slide,
        [
            "报告页三联组合：仪表盘 + 彩色柱状 + 环形占比；大屏五类图表自由拖拽。",
            "Tkinter 主线程只画界面，爬取与检测放子线程，queue + after 轮询保证不卡死。",
        ],
        top=5.35, height=1.5, size=15,
    )
    add_footer(slide, "② 关键代码讲解 · face_insight/charts.py · app.py")

    slide = add_slide(prs, "问题排查与思路：从报错到修复")
    add_card(slide, 0.92, 1.6, 5.6, 2.4, "除零崩溃（课堂已知 bug）",
             ["定位：有人脸数量为 0 时 total/count 直接除零。", "方案：calculate_average 返回 None，数据库存 NULL。",
              "验证：pytest 用例 test_average_with_no_face 通过。"], YELLOW)
    add_card(slide, 6.82, 1.6, 5.6, 2.4, "QPS 限流（错误码 18）",
             ["定位：0.35s/张 超出免费额度每秒 1 次限制。", "方案：间隔放宽 1.1s + 递增退避重试 4 次。",
              "验证：20 张图连续分析不再弹错。"], ORANGE)
    add_card(slide, 0.92, 4.2, 5.6, 2.4, "IAM 认证失败（错误码 14）",
             ["定位：三码失效或人脸服务未开通。", "方案：控制台核对三码，在程序 UI 内保存并验证。",
              "验证：状态变为“三码已配置”后可直接分析。"], BLUE)
    add_card(slide, 6.82, 4.2, 5.6, 2.4, "界面卡死与脏数据",
             ["定位：爬取阻塞主线程；旧图混入统计。", "方案：子线程 + queue 消息队列；下载前清空目录。",
              "附加：10MB 超限拦截、四种格式白名单。"], ACCENT)
    add_footer(slide, "③ 问题排查与思路")

    slide = add_slide(prs, "感谢致辞")
    add_bullets(
        slide,
        [
            "感谢老师在课堂上的细致讲解，让我们把一串陌生的库串成了完整作品。",
            "感谢小组成员分工协作，从爬虫被限流到除零修复，每个问题都是一起啃下来的。",
            "感谢百度智能云和开源社区提供的文档与示例，让课堂知识有了落地的抓手。",
            "这个项目教会我们：数据产品不只是“能跑”，还要稳得住、看得清、可复盘。",
            "我们会带着这份好奇心继续往前走，欢迎各位老师同学提问！",
        ],
        size=20,
    )
    add_footer(slide, "④ 感谢致辞")

    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)


if __name__ == "__main__":
    build(Path("PPT/人脸颜值数据分析系统-答辩.pptx"))
