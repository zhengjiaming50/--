import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os

class AppGUI:
    def __init__(self, master):
        self.master = master
        master.title("林地报告生成系统")
        master.geometry("400x300")
        
        # 样式配置
        self.style = ttk.Style()
        self.style.configure('TButton', font=('微软雅黑', 12), padding=6)
        self.style.configure('Title.TLabel', font=('微软雅黑', 16, 'bold'))

        # 界面布局
        header = ttk.Frame(master)
        content = ttk.Frame(master)
        footer = ttk.Frame(master)
        
        header.pack(pady=10)
        content.pack(expand=True, fill='both')
        footer.pack(pady=10)

        # 标题
        ttk.Label(header, style='Title.TLabel', 
                text="林地报告生成系统").pack()

        # 功能按钮
        buttons = [
            ("安装运行环境", self.run_install),
            ("处理PDF文件", self.run_pdf),
            ("处理Excel文件", self.run_excel),
            ("合成文本文件", self.run_merge),
            ("一键全自动运行", self.run_all)
        ]
        
        for text, cmd in buttons:
            btn = ttk.Button(content, text=text, command=cmd)
            btn.pack(fill='x', padx=20, pady=3)

        # 状态栏
        self.status = ttk.Label(footer, text="就绪")
        self.status.pack()

    def run_command(self, command):
        try:
            self.status.config(text="执行中...")
            result = subprocess.run(
                command,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                check=True
            )
            messagebox.showinfo("完成", "操作执行成功！")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", 
                f"执行失败，请查看CMD窗口的错误信息")
        finally:
            self.status.config(text="就绪")

    def run_install(self):
        self.run_command("一键安装所有环境.bat")

    def run_pdf(self):
        self.run_command("处理pdf.bat")

    def run_excel(self):
        self.run_command("处理excel.bat")

    def run_merge(self):
        self.run_command("合成文本.bat")

    def run_all(self):
        if messagebox.askyesno("确认", "将按顺序执行所有操作，是否继续？"):
            steps = [
                "一键安装所有环境.bat",
                "处理pdf.bat",
                "处理excel.bat",
                "合成文本.bat"
            ]
            for step in steps:
                self.run_command(step)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop() 