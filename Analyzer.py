# main.py
#Author minkit
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from datetime import datetime, timedelta

import pytz
from AutocompleteEntry import AutocompleteEntry

class LogAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web日志分析工具")
        self.log_lines = []
        self.last_result = ""  # 存储最后一次分析结果
        self.current_log_prefix = ""  # 新增：当前日志文件前缀
        self.current_date = ""  # 新增：当前日期
        self.history_file = "search_history.txt"  # 新增： 查询关键词历史
        self.search_history = self.load_history()

        self.create_widgets()
        self.setup_autocomplete()
        self.setup_default_time()
        self.setup_text_tags()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_text_tags(self):
        # 配置文本标签样式
        self.text_result.tag_configure("bold", font=('TkDefaultFont', 10, 'bold'))

    def create_widgets(self):
        # 文件上传区域
        self.frame_upload = ttk.LabelFrame(self.root, text="日志文件上传")
        self.btn_upload = ttk.Button(self.frame_upload, text="上传日志文件", command=self.upload_log)
        self.lbl_upload_status = ttk.Label(self.frame_upload, text="", foreground="green")
        self.btn_upload.pack(side=tk.LEFT, padx=5)
        self.lbl_upload_status.pack(side=tk.LEFT)
        self.frame_upload.pack(fill=tk.X, padx=10, pady=5)

        # 条件配置区域
        self.frame_conditions = ttk.LabelFrame(self.root, text="分析条件")

        # 控件定义
        self.lbl_keyword = ttk.Label(self.frame_conditions, text="精确关键词（多个用,分隔）:")

        self.lbl_exclude = ttk.Label(self.frame_conditions, text="排除路径类型（如 .js/.css/.png）:")
        self.entry_exclude = ttk.Entry(self.frame_conditions)

        self.lbl_keyword1 = ttk.Label(self.frame_conditions, text="排除关键词（多个用,分隔）:")

        self.lbl_ip = ttk.Label(self.frame_conditions, text="访问IP地址:")
        self.entry_ip = ttk.Entry(self.frame_conditions)

        self.lbl_backend_ports = ttk.Label(self.frame_conditions, text="后端端口（多个用,分隔）:")
        self.entry_backend_ports = ttk.Entry(self.frame_conditions)

        self.lbl_status = ttk.Label(self.frame_conditions, text="状态码（如 200,404）:")
        self.entry_status = ttk.Entry(self.frame_conditions)

        # 时间范围分为开始和结束时间
        self.lbl_time_start = ttk.Label(self.frame_conditions, text="开始时间（YYYY-MM-DD HH:MM:SS）:")
        self.entry_time_start = ttk.Entry(self.frame_conditions)
        self.lbl_time_end = ttk.Label(self.frame_conditions, text="结束时间（YYYY-MM-DD HH:MM:SS）:")
        self.entry_time_end = ttk.Entry(self.frame_conditions)

        self.lbl_range = ttk.Label(self.frame_conditions, text="行数范围（如 1-1000）:")
        self.entry_range = ttk.Entry(self.frame_conditions)

        self.btn_analyze = ttk.Button(self.frame_conditions, text="开始分析", command=self.analyze_log)

        # 网格布局
        rows = [
            (self.lbl_keyword, None),
            (self.lbl_exclude, self.entry_exclude),
            (self.lbl_keyword1, None),
            (self.lbl_ip, self.entry_ip),
            (self.lbl_backend_ports, self.entry_backend_ports),
            (self.lbl_status, self.entry_status),
            (self.lbl_time_start, self.entry_time_start),
            (self.lbl_time_end, self.entry_time_end),
            (self.lbl_range, self.entry_range),
        ]

        # 动态布局
        row_counter = 0
        for label, entry in rows:
            if label:
                label.grid(row=row_counter, column=0, sticky=tk.W, padx=5, pady=2)
            if entry:
                entry.grid(row=row_counter, column=1, sticky=tk.EW, padx=5, pady=2)
            row_counter += 1

        # 分析按钮位置
        self.btn_analyze.grid(row=row_counter, columnspan=2, pady=10)

        # 框架布局
        self.frame_conditions.grid_columnconfigure(1, weight=1)
        self.frame_conditions.pack(fill=tk.X, padx=10, pady=5)

        # 结果展示区域
        self.frame_result = ttk.LabelFrame(self.root, text="分析结果")
        self.text_result = tk.Text(self.frame_result, height=15)
        self.scrollbar = ttk.Scrollbar(self.frame_result, command=self.text_result.yview)
        self.text_result.configure(yscrollcommand=self.scrollbar.set)
        self.text_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def upload_log(self):
        #文件上传功能
        filetypes = [("日志文件", "*.txt *.log")]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            try:
                # 新增：提取文件名前缀和日期
                filename = os.path.basename(filepath)
                self.current_log_prefix = filename.split('.')[0]  # 去除扩展名
                self.current_date = datetime.now().strftime("%Y%m%d")

                with open(filepath, 'r', encoding='utf-8') as f:
                    self.log_lines = f.readlines()
                status_msg = f"已加载: {filename} → 将生成 {self.current_log_prefix}_{self.current_date}.txt"
                self.lbl_upload_status.config(text=status_msg, foreground="green")
            except Exception as e:
                self.lbl_upload_status.config(text=f"加载失败: {str(e)}", foreground="red")

    def setup_autocomplete(self):
        # 配置自动完成输入框
        # 包含关键词输入框
        self.entry_keyword = AutocompleteEntry(
            self.frame_conditions,
            completevalues=self.search_history,  # 传入历史数据
            history_limit=15
        )
        self.entry_keyword.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        # 排除关键词输入框
        self.entry_keyword1 = AutocompleteEntry(
            self.frame_conditions,
            completevalues=self.search_history,  # 传入历史数据
            history_limit=15
        )
        self.entry_keyword1.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

    def load_history(self):
        #加载查询关键词历史记录
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return list(set(f.read().splitlines()))  # 去重
            return []
        except:
            return []

    def save_history(self):
        #保存历史记录
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.search_history[-100:]))  # 最多保留100条
        except:
            pass

    def setup_default_time(self):
        # 设置默认时间范围（最近24小时）
        now = datetime.now()
        start_time = (now - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.entry_time_start.insert(0, start_time)
        self.entry_time_end.insert(0, end_time)

    def analyze_log(self):
        # 获取过滤条件
        keyword = self.entry_keyword.get().strip()
        exclude = self.entry_exclude.get().strip()
        exclude_keyword = self.entry_keyword1.get().strip()
        line_range = self.entry_range.get().strip()
        ip = self.entry_ip.get().strip()
        backend_ports_input = self.entry_backend_ports.get().strip()
        status = self.entry_status.get().strip()
        start_time_str = self.entry_time_start.get().strip()
        end_time_str = self.entry_time_end.get().strip()
        include_keywords = [k.strip() for k in re.split(r'[,，\s]+', self.entry_keyword.get().strip()) if k.strip()]
        exclude_keywords = [k.strip() for k in re.split(r'[,，\s]+', self.entry_keyword1.get().strip()) if k.strip()]

        # 处理行数范围
        start_line, end_line = 1, len(self.log_lines)
        if line_range:
            try:
                start, end = map(int, line_range.split('-'))
                start_line = max(1, start)
                end_line = min(len(self.log_lines), end)
            except:
                messagebox.showerror("错误", "行数范围格式无效（示例：1-1000）")
                return

        # 处理排除扩展名
        exclude_exts = [ext.strip().lstrip('.').lower() for ext in re.split(r'[/,，\s]+', exclude) if
                        ext.strip()] if exclude else []

        # 处理端口号
        backend_ports = []
        if backend_ports_input:
            try:
                backend_ports = [p.strip() for p in re.split(r'[,，\s]+', backend_ports_input)]
            except ValueError:
                messagebox.showerror("错误", "端口号必须为数字")
                return

        # 处理状态码
        statuses = [s.strip() for s in status.split(',')] if status else []

        # 处理时间范围
        start_time = end_time = None
        if start_time_str or end_time_str:
            if not (start_time_str and end_time_str):
                messagebox.showerror("错误", "必须同时填写开始和结束时间")
                return
            try:
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                messagebox.showerror("错误", f"时间格式错误: {str(e)}")
                return

        # 日志解析正则表达式（适配nginx拓展格式）
        log_pattern = re.compile(
            r'^(\S+)\s+\S+\s+\[([^]]+)\]\s+(\d+)\s+\d+\.\d+\s+\d+\s+(\S+)\s+(\S+)\s+(\S+):(\d+)\s+(\d+)\s+".*?"\s+\d+\.\d+$'
        )
        #    r'^(?P<client_ip>\S+)\s+\S+\s+\[(?P<timestamp>[^]]+)\]\s+'
        #    r'(?P<front_status>\d+)\s+\d+\.\d+\s+\d+\s+'
        #   r'(?P<path>\S+)\s+(?P<source_ip>\S+)\s+\S+:\d+\s+'
        #   r'(?P<backend_status>\d+)\s+".*?"\s+\d+\.\d+$'

        # 执行分析逻辑
        filtered_lines = []
        for i in range(start_line - 1, end_line):
            line = self.log_lines[i].strip()
            match = log_pattern.match(line)
            if not match:
                continue

            # 提取日志字段
            time_log_str = match.group(2)
            status_log = match.group(3)  # 状态码
            url_log = match.group(4)  # 请求路径
            ip_log = match.group(5)  # 访问IP
            port = match.group(7)  # 端口号

            # 条件判断
            # 关键词判断
            include_condition = True
            if include_keywords:
                include_condition = all(
                    re.search(r'\b{}\b'.format(re.escape(keyword)), line, re.IGNORECASE)
                    for keyword in include_keywords
                )
            # 排除后缀类型判断
            exclude_match = False
            if exclude_exts:
                path_part = url_log.split('?')[0].split('#')[0]
                filename = path_part.split('/')[-1]
                extension = filename.split('.')[-1].lower() if '.' in filename else None
                exclude_match = extension in exclude_exts
            # 排除关键词判断
            exclude_condition = False
            if exclude_keywords:
                exclude_condition = any(
                    re.search(r'\b{}\b'.format(re.escape(keyword)), line, re.IGNORECASE)
                    for keyword in exclude_keywords
                )
            # 访问IP判断
            ip_condition = (ip_log == ip) if ip else True
            # 状态码判断
            status_condition = (status_log in statuses) if statuses else True
            # 端口条件判断（新增）
            port_condition = True
            if backend_ports:
                port_condition = port in backend_ports
            # 时间条件处理
            time_condition = True
            if start_time and end_time:
                try:
                    log_time = datetime.strptime(time_log_str, "%d/%b/%Y:%H:%M:%S %z")
                    log_time_naive = log_time.astimezone(pytz.utc).replace(tzinfo=None)
                    time_condition = start_time <= log_time_naive <= end_time
                except Exception as e:
                    time_condition = False

            # 综合条件判断
            if all([
                include_condition,
                not exclude_match,
                not exclude_condition,
                ip_condition,
                status_condition,
                port_condition,
                time_condition
            ]):
                filtered_lines.append(line)

        # 显示结果
        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, f"找到 {len(filtered_lines)} 条匹配记录:\n\n")

        # 存储结果并更新文件
        result_header = f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        result_header += f"原始文件: {self.current_log_prefix}.log\n"
        result_header += f"匹配记录: {len(filtered_lines)} 条\n\n"
        self.last_result = result_header + '\n'.join(filtered_lines)
        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, self.last_result)

        # 全局高亮关键词
        if include_keywords:
            self.highlight_multiple_keywords(include_keywords)

        # 执行分析逻辑后，更新历史记录
        new_keywords = include_keywords + exclude_keywords
        for kw in new_keywords:
            if kw and kw not in self.search_history:
                self.search_history.append(kw)

        # 去重并保留顺序（Python3.7+有序字典）
        self.search_history = list(dict.fromkeys(self.search_history))

        # 保留最多100条记录
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]

        # 保存更新后的历史记录
        self.save_history()

        # 自动写入文件
        self.save_result()

    def highlight_multiple_keywords(self, keywords):
        """高亮多个关键词"""
        self.text_result.tag_remove("bold", "1.0", tk.END)
        for keyword in keywords:
            start_idx = "1.0"
            while True:
                pos = self.text_result.search(
                    r'\y{}\y'.format(re.escape(keyword)),  # 使用单词边界
                    start_idx,
                    stopindex=tk.END,
                    nocase=True,
                    regexp=True
                )
                if not pos:
                    break
                end_pos = f"{pos}+{len(keyword)}c"
                self.text_result.tag_add("bold", pos, end_pos)
                start_idx = end_pos

    def save_result(self, on_exit=False):
        # 动态生成结果文件
        if self.last_result and self.current_log_prefix:
            try:
                # 生成带日期戳的文件名
                filename = f"{self.current_log_prefix}_{self.current_date}.txt"
                with open(filename, "w", encoding="gbk") as f:
                    f.write(self.last_result)

                if not on_exit:
                    status = f"结果已保存到: {os.path.abspath(filename)}"
                    self.lbl_upload_status.config(text=status, foreground="blue")
            except Exception as e:
                error_msg = f"保存失败: {str(e)}" if not on_exit else ""
                self.lbl_upload_status.config(text=error_msg, foreground="red")

    def on_close(self):
        # 关闭时自动保存
        if self.last_result:
            self.save_result(on_exit=True)
        self.root.destroy()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = LogAnalyzerApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("致命错误", f"程序异常终止: {str(e)}")
