# main.py
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from datetime import datetime, timedelta
import pytz
from AutocompleteEntry import AutocompleteEntry
from log_parser import LogParser

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
        self.log_parser = LogParser()  # 新增日志解析器

        self.create_widgets()
        self.setup_autocomplete()
        self.setup_default_time()
        self.setup_text_tags()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_text_tags(self):
        # 配置文本标签样式
        self.text_result.tag_configure("bold", font=('TkDefaultFont', 10, 'bold'))

    def upload_log(self):
        filetypes = [
            ("所有日志文件", "*.log;*.txt"),
            ("Nginx日志", "*.log"),
            ("Apache日志", "*.log"),
            ("IIS日志", "*.log"),
            ("文本文件", "*.txt"),
        ]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            try:
                filename = os.path.basename(filepath)
                self.current_log_prefix = filename.split('.')[0]
                self.current_date = datetime.now().strftime("%Y%m%d")
                
                # 使用生成器逐行读取，减少内存占用
                self.log_lines = []
                total_lines = 0
                
                # 创建进度条
                progress = ttk.Progressbar(self.frame_upload, mode='determinate')
                progress.pack(fill=tk.X, padx=5, pady=5)
                
                # 首次扫描获取总行数
                with open(filepath, 'r', encoding='utf-8') as f:
                    for _ in f:
                        total_lines += 1
                
                # 读取文件并更新进度条
                with open(filepath, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        self.log_lines.append(line)
                        progress['value'] = (i + 1) / total_lines * 100
                        self.root.update_idletasks()
                
                # 自动识别日志格式
                log_format = self.log_parser.detect_format(self.log_lines[:10])
                
                status_msg = (f"已加载: {filename} ({log_format}) → "
                            f"将生成 {self.current_log_prefix}_{self.current_date}.txt")
                self.lbl_upload_status.config(text=status_msg, foreground="green")
                
                # 移除进度条
                progress.destroy()
                
                
            except Exception as e:
                self.lbl_upload_status.config(text=f"加载失败: {str(e)}", foreground="red")

                
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

        self.lbl_backend_ports = ttk.Label(self.frame_conditions, text="端口（多个用,分隔）:")
        self.entry_backend_ports = ttk.Entry(self.frame_conditions)

        self.lbl_status = ttk.Label(self.frame_conditions, text="状态码（如 200,404）:")
        self.entry_status = ttk.Entry(self.frame_conditions)

        # 时间范围分为开始和结束时间
        self.lbl_time_start = ttk.Label(self.frame_conditions, text="开始时间（格式：YYYY-MM-DD HH:MM:SS）:")
        self.entry_time_start = ttk.Entry(self.frame_conditions)
        self.lbl_time_end = ttk.Label(self.frame_conditions, text="结束时间（当前为UTC时间，北京时间需减8小时）:")
        self.entry_time_end = ttk.Entry(self.frame_conditions)

        self.lbl_range = ttk.Label(self.frame_conditions, text="行数范围（如 1-1000）:")
        self.entry_range = ttk.Entry(self.frame_conditions)

        # 修改按钮布局部分
        self.btn_frame = ttk.Frame(self.frame_conditions)  # 新增按钮容器

        self.btn_analyze = ttk.Button(self.btn_frame, text="开始分析", command=self.analyze_log)
        self.btn_analyze.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        # 新增IP汇总按钮
        self.btn_ip_summary = ttk.Button(self.btn_frame,text="开始汇总IP",command=self.summarize_ips  # 绑定新方法
        )
        self.btn_ip_summary.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
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

        # 分析按钮位置(单个分析按钮布局已废弃)
        #self.btn_analyze.grid(row=row_counter, columnspan=2, pady=10)

        # 将按钮容器放置到网格布局
        self.btn_frame.grid(row=row_counter, columnspan=2, pady=10, sticky=tk.EW)



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

    def summarize_ips(self):
       # 新增IP汇总按钮
        if not self.log_lines:
            messagebox.showwarning("警告", "请先上传日志文件")
            return

        # 使用集合自动去重
        unique_ips = set()
        log_pattern = re.compile(
            r'^(\S+)\s+\S+\s+\[([^]]+)\]\s+(\d+)\s+\d+\.\d+\s+\d+\s+(\S+)\s+(\S+)\s+(\S+):(\d+)\s+(\d+)\s+".*?"\s+\d+\.\d+$'
        )

        for line in self.log_lines:
            match = log_pattern.match(line.strip())
            if match:
                ip = match.group(5)  # 第5组为访问IP
                unique_ips.add(ip)

        if not unique_ips:
            self.text_result.delete(1.0, tk.END)
            self.text_result.insert(tk.END, "未找到有效IP地址")
            return

        # 对IP进行排序（简单字符串排序）
        sorted_ips = sorted(unique_ips, key=lambda ip: [int(part) for part in ip.split('.')])

        # 构建结果字符串
        result = f"发现 {len(sorted_ips)} 个IP地址：\n\n"
        result += "\n".join(sorted_ips)

        # 更新界面显示
        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, result)

        # 生成IP.txt文件
        try:
            ip_filename = "IP.txt"
            with open(ip_filename, "w", encoding="utf-8") as f:
                f.write("\n".join(sorted_ips))

            # 更新状态显示
            self.lbl_upload_status.config(
                text=f"IP列表已保存到：{os.path.abspath(ip_filename)}",
                foreground="blue"
            )
        except Exception as e:
            messagebox.showerror("保存失败", f"无法写入IP.txt文件：{str(e)}")

    def setup_default_time(self):
        # 设置默认时间范围（最近24小时）
        now = datetime.now()
        start_time = (now - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.entry_time_start.insert(0, start_time)
        self.entry_time_end.insert(0, end_time)

    def analyze_log(self):
        if not self.log_lines:
            messagebox.showwarning("警告", "请先上传日志文件")
            return

        # 获取输入值
        include_keywords = [kw.strip() for kw in self.entry_keyword.get().split(',') if kw.strip()]
        exclude_exts = [ext.strip().lower() for ext in self.entry_exclude.get().split(',') if ext.strip()]
        exclude_keywords = [kw.strip() for kw in self.entry_keyword1.get().split(',') if kw.strip()]
        ip = self.entry_ip.get().strip()
        backend_ports = [port.strip() for port in self.entry_backend_ports.get().split(',') if port.strip()]
        statuses = [status.strip() for status in self.entry_status.get().split(',') if status.strip()]

        # 处理时间范围
        start_time = None
        end_time = None
        try:
            if self.entry_time_start.get().strip():
                start_time = datetime.strptime(self.entry_time_start.get().strip(), "%Y-%m-%d %H:%M:%S")
                start_time = pytz.UTC.localize(start_time)  # 添加 UTC 时区信息
            if self.entry_time_end.get().strip():
                end_time = datetime.strptime(self.entry_time_end.get().strip(), "%Y-%m-%d %H:%M:%S")
                end_time = pytz.UTC.localize(end_time)  # 添加 UTC 时区信息
        except ValueError as e:
            messagebox.showerror("错误", f"时间格式错误: {str(e)}")
            return

        # 处理行数范围
        try:
            range_str = self.entry_range.get().strip()
            if range_str:
                start_line, end_line = map(int, range_str.split('-'))
                end_line = min(end_line, len(self.log_lines))
            else:
                start_line, end_line = 1, len(self.log_lines)
        except ValueError:
            messagebox.showerror("错误", "行数范围格式错误，请使用如 1-1000 的格式")
            return

        # 执行分析逻辑
        filtered_lines = []
        for i in range(start_line - 1, end_line):
            line = self.log_lines[i].strip()
            parsed_log = self.log_parser.parse_line(line)
            
            if not parsed_log:
                continue

            # 提取日志字段
            time_log = parsed_log.get('timestamp')
            status_log = parsed_log.get('status')
            url_log = parsed_log.get('url')
            ip_log = parsed_log.get('ip')

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
            if exclude_exts and url_log:
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

            # 时间条件处理
            time_condition = True
            if start_time and end_time and time_log:
                try:
                    # 确保 time_log 是 offset-aware datetime
                    if time_log.tzinfo is None:
                        time_log = pytz.UTC.localize(time_log)
                    time_condition = start_time <= time_log <= end_time
                except Exception:
                    time_condition = False

            # 综合条件判断
            if all([
                include_condition,
                not exclude_match,
                not exclude_condition,
                ip_condition,
                status_condition,
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
