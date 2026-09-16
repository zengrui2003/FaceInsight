from __future__ import annotations

import csv
import os
import queue
import threading
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .charts import save_history_screen, save_score_chart
from .config import load_baidu_config
from .crawler import crawl_images, list_images
from .face_analysis import FaceAnalyzer, aggregate_scores
from .storage import calculate_average, connect, create_table, fetch_history, save_analysis


BG = "#0d1220"
PANEL = "#151d30"
PANEL_LIGHT = "#1d2842"
BORDER = "#263352"
ACCENT = "#00e5c3"
ACCENT_HOVER = "#4dffd9"
ACCENT_PRESS = "#00c2a0"
TEXT = "#e8eef6"
MUTED = "#8fa1b8"
DANGER = "#ff7043"
SUCCESS = "#66bb6a"


def open_local_file(path: Path):
    """Windows 下交给系统默认程序打开，避免浏览器把本地文件当新标签处理。"""
    target = path.resolve()
    if not target.exists():
        raise FileNotFoundError(f"文件不存在：{target}")
    os.startfile(str(target))


class FaceInsightApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FaceInsight · 人脸颜值数据洞察")
        self.geometry("1000x740")
        self.minsize(840, 640)
        self.configure(background=BG)

        self.worker: threading.Thread | None = None
        self.events: queue.Queue[dict] = queue.Queue()
        self.latest_chart: Path | None = None
        self.history_screen: Path | None = None
        self.local_folder_var = tk.StringVar()
        self.source_var = tk.StringVar(value="Bing 爬虫")

        self._setup_style()
        self._build_ui()
        self.after(120, self._poll_worker_events)

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        base = ("Microsoft YaHei UI", 10)

        style.configure(".", background=BG, foreground=TEXT, font=base)
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=base)
        style.configure("Card.TLabel", background=PANEL, foreground=TEXT, font=base)
        style.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=base)
        style.configure("Brand.TLabel", background=BG, foreground=TEXT, font=("Microsoft YaHei UI", 24, "bold"))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Microsoft YaHei UI", 10))
        style.configure("CardTitle.TLabel", background=PANEL, foreground=ACCENT, font=("Microsoft YaHei UI", 11, "bold"))

        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground="#04231c",
            font=("Microsoft YaHei UI", 10, "bold"),
            borderwidth=0,
            focusthickness=0,
            padding=(18, 9),
        )
        style.map(
            "Accent.TButton",
            background=[("pressed", ACCENT_PRESS), ("active", ACCENT_HOVER), ("disabled", "#1f3a35")],
            foreground=[("disabled", "#6b8a83")],
        )
        style.configure(
            "Ghost.TButton",
            background=PANEL_LIGHT,
            foreground=TEXT,
            borderwidth=1,
            focusthickness=0,
            padding=(14, 8),
        )
        style.map(
            "Ghost.TButton",
            background=[("pressed", PANEL), ("active", "#243154"), ("disabled", "#161e30")],
            foreground=[("disabled", MUTED)],
        )

        style.configure(
            "TEntry",
            fieldbackground=PANEL_LIGHT,
            background=PANEL_LIGHT,
            foreground=TEXT,
            insertcolor=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=6,
        )
        style.map("TEntry", bordercolor=[("focus", ACCENT)])
        style.configure(
            "TSpinbox",
            fieldbackground=PANEL_LIGHT,
            background=PANEL_LIGHT,
            foreground=TEXT,
            insertcolor=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            arrowsize=12,
            padding=4,
        )
        style.configure(
            "TCombobox",
            fieldbackground=PANEL_LIGHT,
            background=PANEL_LIGHT,
            foreground=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            arrowcolor=TEXT,
            padding=6,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", PANEL_LIGHT)],
            bordercolor=[("focus", ACCENT)],
        )

        style.configure(
            "Horizontal.TProgressbar",
            background=ACCENT,
            troughcolor=PANEL_LIGHT,
            bordercolor=BG,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
            thickness=10,
        )
        style.configure(
            "Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=TEXT,
            rowheight=30,
            bordercolor=BORDER,
            font=base,
        )
        style.configure(
            "Treeview.Heading",
            background=PANEL_LIGHT,
            foreground=MUTED,
            font=("Microsoft YaHei UI", 9, "bold"),
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", "#24405e")],
            foreground=[("selected", TEXT)],
        )
        style.map("Treeview.Heading", background=[("active", "#243154")])

        style.configure(
            "ChipIdle.TLabel",
            background=PANEL_LIGHT,
            foreground=ACCENT,
            font=("Microsoft YaHei UI", 9, "bold"),
            padding=(10, 4),
        )
        style.configure(
            "ChipBusy.TLabel",
            background=PANEL_LIGHT,
            foreground="#ffd54f",
            font=("Microsoft YaHei UI", 9, "bold"),
            padding=(10, 4),
        )

    def _build_ui(self):
        container = ttk.Frame(self, padding=(28, 22, 28, 18))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x")
        header.columnconfigure(0, weight=1)
        brand = ttk.Frame(header)
        brand.grid(row=0, column=0, sticky="w")
        ttk.Label(brand, text="FaceInsight", style="Brand.TLabel").pack(anchor="w")
        ttk.Label(
            brand,
            text="icrawler 爬取 · 百度人脸检测 · SQLite 留存 · pyecharts 可视化",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(2, 0))
        self.status_chip = ttk.Label(header, text="● 就绪", style="ChipIdle.TLabel")
        self.status_chip.grid(row=0, column=1, sticky="ne", padx=(12, 0))

        input_card = ttk.Frame(container, style="Card.TFrame", padding=18)
        input_card.pack(fill="x", pady=(18, 0))
        input_card.columnconfigure(1, weight=1)

        ttk.Label(input_card, text="分析配置", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=5, sticky="w", pady=(0, 10)
        )

        ttk.Label(input_card, text="数据来源", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        source_select = ttk.Combobox(
            input_card,
            textvariable=self.source_var,
            values=["Bing 爬虫", "本地文件夹"],
            state="readonly",
            width=14,
        )
        source_select.grid(row=1, column=1, columnspan=2, sticky="w")
        source_select.bind("<<ComboboxSelected>>", lambda _event: self._toggle_source_mode())

        ttk.Label(input_card, text="关键词", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        self.keyword_var = tk.StringVar(value="大学生")
        ttk.Entry(input_card, textvariable=self.keyword_var).grid(row=2, column=1, sticky="ew")
        ttk.Label(input_card, text="计划数量", style="Card.TLabel").grid(row=2, column=2, sticky="w", padx=(16, 8))
        self.count_var = tk.IntVar(value=20)
        self.count_spin = ttk.Spinbox(input_card, from_=1, to=100, width=8, textvariable=self.count_var)
        self.count_spin.grid(row=2, column=3, sticky="w")

        ttk.Label(input_card, text="本地文件夹", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        self.local_entry = ttk.Entry(input_card, textvariable=self.local_folder_var, state="disabled")
        self.local_entry.grid(row=3, column=1, columnspan=2, sticky="ew")
        self.browse_button = ttk.Button(
            input_card, text="浏览", style="Ghost.TButton", state="disabled", command=self.choose_local_folder
        )
        self.browse_button.grid(row=3, column=3, sticky="w", padx=(8, 0))

        actions = ttk.Frame(container)
        actions.pack(fill="x", pady=16)
        self.start_button = ttk.Button(actions, text="开始分析", style="Accent.TButton", command=self.start_analysis)
        self.start_button.pack(side="left")
        self.chart_button = ttk.Button(
            actions, text="查看最新报告", style="Ghost.TButton", state="disabled", command=self.open_latest_chart
        )
        self.chart_button.pack(side="left", padx=10)
        self.history_button = ttk.Button(
            actions, text="生成数据大屏", style="Ghost.TButton", command=self.generate_history_screen
        )
        self.history_button.pack(side="left")
        ttk.Button(actions, text="导出历史CSV", style="Ghost.TButton", command=self.export_history_csv).pack(
            side="left", padx=10
        )

        progress_card = ttk.Frame(container, style="Card.TFrame", padding=(18, 14))
        progress_card.pack(fill="x")
        self.status_var = tk.StringVar(value="等待分析")
        ttk.Label(progress_card, textvariable=self.status_var, style="Card.TLabel").pack(anchor="w")
        self.progress = ttk.Progressbar(progress_card, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(10, 0))

        history_card = ttk.Frame(container, style="Card.TFrame", padding=(18, 12))
        history_card.pack(fill="x", pady=(14, 0))
        ttk.Label(history_card, text="历史记录", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        columns = ("id", "keyword", "face", "no_face", "avg")
        self.history_tree = ttk.Treeview(history_card, columns=columns, show="headings", height=4)
        self.history_tree.heading("id", text="ID")
        self.history_tree.heading("keyword", text="关键词")
        self.history_tree.heading("face", text="有人脸")
        self.history_tree.heading("no_face", text="无人脸")
        self.history_tree.heading("avg", text="平均分")
        self.history_tree.column("id", width=50, anchor="center")
        self.history_tree.column("keyword", width=220)
        self.history_tree.column("face", width=80, anchor="center")
        self.history_tree.column("no_face", width=80, anchor="center")
        self.history_tree.column("avg", width=80, anchor="center")
        self.history_tree.pack(fill="x")

        log_card = ttk.Frame(container, style="Card.TFrame", padding=(18, 12))
        log_card.pack(fill="both", expand=True, pady=(14, 0))
        ttk.Label(log_card, text="运行日志", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.log_text = tk.Text(
            log_card,
            height=7,
            wrap="word",
            state="disabled",
            background=PANEL,
            foreground=TEXT,
            insertbackground=ACCENT,
            selectbackground="#24405e",
            relief="flat",
            padx=12,
            pady=10,
            font=("Microsoft YaHei UI", 10),
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_configure("success", foreground=SUCCESS)
        self.log_text.tag_configure("error", foreground=DANGER)
        self.log_text.tag_configure("muted", foreground=MUTED)

        self.refresh_history()

    def log(self, message: str, tag: str | None = None):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n", tag or ())
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def set_running(self, running: bool):
        state = "disabled" if running else "normal"
        self.start_button.configure(state=state)
        self.history_button.configure(state=state)
        if running:
            self.progress.configure(value=0)
            self.status_chip.configure(text="● 分析中", style="ChipBusy.TLabel")
        else:
            self.status_chip.configure(text="● 就绪", style="ChipIdle.TLabel")

    def _toggle_source_mode(self):
        is_local = self.source_var.get() == "本地文件夹"
        self.count_spin.configure(state="disabled" if is_local else "normal")
        self.local_entry.configure(state="normal" if is_local else "disabled")
        self.browse_button.configure(state="normal" if is_local else "disabled")

    def choose_local_folder(self):
        folder = filedialog.askdirectory(title="选择待检测图片文件夹")
        if folder:
            self.local_folder_var.set(folder)

    def start_analysis(self):
        if self.worker and self.worker.is_alive():
            return
        try:
            keyword = self.keyword_var.get().strip()
            count = self.count_var.get()
            source = self.source_var.get()
            local_folder = self.local_folder_var.get().strip()
            folder_path: Path | None = None
            if not keyword:
                raise ValueError("请先输入关键词或记录标签。")
            if source == "本地文件夹":
                if not local_folder:
                    raise ValueError("请选择本地图片文件夹。")
                folder_path = Path(local_folder)
                if not folder_path.exists():
                    raise ValueError("本地图片文件夹不存在。")
            if not 1 <= count <= 100:
                raise ValueError("计划数量应在 1 到 100 之间。")
        except (ValueError, tk.TclError) as exc:
            messagebox.showwarning("输入有误", str(exc))
            return

        self.set_running(True)
        self.status_var.set("正在执行分析")
        self.log(f"任务开始：关键词「{keyword}」，计划 {count} 张。")
        self.worker = threading.Thread(
            target=self._analysis_worker,
            args=(source, keyword, count, folder_path),
            daemon=True,
        )
        self.worker.start()

    def _analysis_worker(self, source: str, keyword: str, count: int, local_folder: Path | None):
        try:
            config = load_baidu_config()
            analyzer = FaceAnalyzer(config)

            if source == "本地文件夹":
                self.events.put({"type": "progress", "value": 10, "status": "读取本地图片"})
                paths = list_images(local_folder)
            else:
                self.events.put({"type": "progress", "value": 8, "status": "正在爬取图片"})
                folder = crawl_images(keyword, count, Path("downloads"))
                paths = list_images(folder)
            if not paths:
                raise RuntimeError("没有找到可分析的图片文件。")
            self.events.put({"type": "log", "message": f"共获得 {len(paths)} 张待检测图片。"})

            def report_progress(current: int, total: int, path: Path):
                value = 20 + int(current / total * 70)
                self.events.put(
                    {
                        "type": "progress",
                        "value": value,
                        "status": f"百度检测中 {current}/{total}",
                        "log": f"{path.name} 检测完成",
                    }
                )

            scores = analyzer.analyze_images(paths, report_progress)
            score_counts = aggregate_scores(scores)
            average = calculate_average(score_counts)

            self.events.put({"type": "progress", "value": 94, "status": "保存数据库"})
            with connect() as conn:
                create_table(conn)
                record_id = save_analysis(conn, keyword, score_counts, average)

            self.events.put({"type": "progress", "value": 97, "status": "生成可视化报告"})
            output = Path("exports") / f"{record_id}_{keyword}_分析报告.html"
            output.parent.mkdir(parents=True, exist_ok=True)
            save_score_chart(keyword, score_counts, average, output)

            self.events.put(
                {
                    "type": "success",
                    "value": 100,
                    "status": "分析完成",
                    "message": f"检测完成：有人脸 {sum(score_counts[1:])} 张，无人脸 {score_counts[0]} 张，平均分 {average if average is not None else '—'}",
                    "chart": output,
                }
            )
        except Exception as exc:
            self.events.put({"type": "error", "message": str(exc)})

    def _poll_worker_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                event_type = event["type"]
                if event_type == "log":
                    self.log(event["message"])
                elif event_type == "progress":
                    self.progress.configure(value=event["value"])
                    self.status_var.set(event["status"])
                    if event.get("log"):
                        self.log(event["log"], "muted")
                elif event_type == "success":
                    self.progress.configure(value=event["value"])
                    self.status_var.set(event["status"])
                    self.log(event["message"], "success")
                    self.latest_chart = Path(event["chart"])
                    self.chart_button.configure(state="normal")
                    open_local_file(self.latest_chart)
                    self.refresh_history()
                elif event_type == "error":
                    self.progress.configure(value=0)
                    self.status_var.set("分析失败")
                    self.log(event["message"], "error")
                    messagebox.showerror("运行失败", event["message"])
        except queue.Empty:
            pass
        finally:
            if not self.worker or not self.worker.is_alive():
                self.set_running(False)
        self.after(120, self._poll_worker_events)

    def open_latest_chart(self):
        if self.latest_chart:
            open_local_file(self.latest_chart)

    def generate_history_screen(self):
        try:
            with connect() as conn:
                create_table(conn)
                records = fetch_history(conn)
            if not records:
                messagebox.showinfo("暂无数据", "还没有历史记录，请先完成一次分析。")
                return

            self.history_screen = Path("exports") / "人脸检测历史数据大屏.html"
            self.history_screen.parent.mkdir(parents=True, exist_ok=True)
            save_history_screen(records, self.history_screen)
            open_local_file(self.history_screen)
            self.log(f"历史大屏已生成，共展示 {len(records)} 条记录。", "success")
        except Exception as exc:
            messagebox.showerror("生成失败", str(exc))

    def refresh_history(self):
        try:
            with connect() as conn:
                create_table(conn)
                records = fetch_history(conn)
        except Exception:
            return

        self.history_tree.delete(*self.history_tree.get_children())
        for record in records:
            face_count = sum(record.score_counts[1:])
            avg_text = f"{record.beauty_avg:.2f}" if record.beauty_avg is not None else "—"
            self.history_tree.insert(
                "",
                "end",
                values=(
                    record.record_id,
                    record.keyword,
                    face_count,
                    record.score_counts[0],
                    avg_text,
                ),
            )

    def export_history_csv(self):
        try:
            with connect() as conn:
                create_table(conn)
                records = fetch_history(conn)
            if not records:
                messagebox.showinfo("暂无数据", "还没有历史记录可以导出。")
                return

            exports = Path("exports")
            exports.mkdir(parents=True, exist_ok=True)
            output = exports / "人脸检测历史数据.csv"
            with output.open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        "ID", "关键词", "有人脸", "无人脸",
                        "1分", "2分", "3分", "4分", "5分", "6分", "7分", "8分", "9分", "10分",
                        "平均分",
                    ]
                )
                for record in records:
                    face_count = sum(record.score_counts[1:])
                    writer.writerow(
                        [
                            record.record_id,
                            record.keyword,
                            face_count,
                            record.score_counts[0],
                            *record.score_counts[1:],
                            record.beauty_avg if record.beauty_avg is not None else "",
                        ]
                    )
            open_local_file(output)
            self.log(f"历史数据已导出：{output}", "success")
        except Exception as exc:
            messagebox.showerror("导出失败", str(exc))


def main():
    app = FaceInsightApp()
    app.mainloop()
