import tkinter as tk
from tkinter import ttk

# 自动完成输入框类
class AutocompleteEntry(ttk.Entry):
    def __init__(self, parent, completevalues=[], history_limit=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.completevalues = completevalues
        self.history_limit = history_limit
        self.var = tk.StringVar()
        self.configure(textvariable=self.var)

        # 绑定事件
        self.var.trace_add('write', self.on_change)
        self.bind('<Key-Up>', self.on_up)
        self.bind('<Key-Down>', self.on_down)
        self.bind('<Return>', self.on_select)
        self.bind('<FocusOut>', self.on_focus_out)

        # 弹出窗口组件
        self.popup = tk.Toplevel(self.winfo_toplevel())
        self.popup.withdraw()
        self.popup.overrideredirect(True)

        self.listbox = tk.Listbox(self.popup, height=5)
        self.listbox.pack()
        self.listbox.bind('<Double-Button-1>', self.on_select)
        self.listbox.bind('<Return>', self.on_select)

        self.selected_index = 0

    def on_change(self, *args):
        #输入变化时触发
        current = self.var.get()
        if current:
            matches = [v for v in self.completevalues if current.lower() in v.lower()]
            self.update_listbox(matches[:self.history_limit])
            self.show_popup()
        else:
            self.hide_popup()

    def update_listbox(self, matches):
        #更新建议列表
        self.listbox.delete(0, tk.END)
        for word in matches:
            self.listbox.insert(tk.END, word)
        self.selected_index = 0
        if matches:
            self.listbox.selection_set(0)

    def show_popup(self):
        #显示建议弹窗
        if self.listbox.size() == 0:
            self.hide_popup()
            return

        # 定位弹窗位置
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.popup.geometry(f'+{x}+{y}')
        self.popup.deiconify()
        self.popup.lift()

    def hide_popup(self, event=None):
        #隐藏建议弹窗
        self.popup.withdraw()

    def on_up(self, event):
        #向上选择
        if self.listbox.size() > 0:
            self.selected_index = max(0, self.selected_index - 1)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.selected_index)
        return "break"

    def on_down(self, event):
        #向下选择
        if self.listbox.size() > 0:
            self.selected_index = min(self.listbox.size() - 1, self.selected_index + 1)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.selected_index)
        return "break"

    def on_select(self, event=None):
        #选择条目
        if self.listbox.size() > 0:
            selected = self.listbox.get(self.selected_index)
            self.var.set(selected)
            self.hide_popup()

        return "break"

    def on_focus_out(self, event):
        #失去焦点时隐藏弹窗
        self.after(100, self.hide_popup)
