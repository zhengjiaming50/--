import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging
import datetime
from io import StringIO

class ConsoleHandler(logging.Handler):
    """Custom logging handler that outputs to a Tkinter Text widget"""
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget
        
        # Configure formatter with timestamp and level
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                     datefmt='%Y-%m-%d %H:%M:%S')
        self.setFormatter(formatter)
    
    def emit(self, record):
        msg = self.format(record)
        
        # Colorize different log levels
        tag = None
        if record.levelno >= logging.ERROR:
            tag = "error"
        elif record.levelno >= logging.WARNING:
            tag = "warning"
        elif record.levelno >= logging.INFO:
            tag = "info"
        elif record.levelno >= logging.DEBUG:
            tag = "debug"
        
        def _insert():
            if tag:
                self.text_widget.insert(tk.END, msg + "\n", tag)
            else:
                self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
        
        # Schedule in the main thread
        self.text_widget.after(0, _insert)

class ScriptManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("林业报告处理工具")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create tabs
        self.pdf_tab = ttk.Frame(self.notebook)
        self.excel_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)
        self.merge_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.pdf_tab, text="PDF处理")
        self.notebook.add(self.excel_tab, text="Excel处理")
        self.notebook.add(self.report_tab, text="报告生成")
        self.notebook.add(self.merge_tab, text="合并文件")
        
        # Setup each tab
        self.setup_pdf_tab()
        self.setup_excel_tab()
        self.setup_report_tab()
        self.setup_merge_tab()
        
        # Setup console with advanced logging
        console_frame = ttk.LabelFrame(main_frame, text="运行日志")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create a Text widget with scrollbar for console output
        self.console = tk.Text(console_frame, height=15, wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to console
        scrollbar = ttk.Scrollbar(self.console, command=self.console.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=scrollbar.set)
        
        # Configure text tags for different log levels
        self.console.tag_configure("error", foreground="red")
        self.console.tag_configure("warning", foreground="orange")
        self.console.tag_configure("info", foreground="black")
        self.console.tag_configure("debug", foreground="gray")
        
        # Set up logging
        self.setup_logging()
        
    def setup_pdf_tab(self):
        # PDF processing tab
        ttk.Label(self.pdf_tab, text="PDF文件处理").pack(pady=10)
        
        input_frame = ttk.Frame(self.pdf_tab)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="PDF文件夹:").pack(side=tk.LEFT, padx=5)
        self.pdf_folder = tk.StringVar(value="pdf")
        pdf_entry = ttk.Entry(input_frame, textvariable=self.pdf_folder, width=50)
        pdf_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(input_frame, text="浏览...", 
                               command=lambda: self.browse_folder(self.pdf_folder))
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        run_btn = ttk.Button(self.pdf_tab, text="开始PDF转换", 
                            command=lambda: self.run_script("combined_pdf_to_txt.py"))
        run_btn.pack(pady=10)
    
    def setup_excel_tab(self):
        # Excel processing tab
        ttk.Label(self.excel_tab, text="Excel文件处理").pack(pady=10)
        
        input_frame = ttk.Frame(self.excel_tab)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Excel文件夹:").pack(side=tk.LEFT, padx=5)
        self.excel_folder = tk.StringVar(value="excel_files")
        excel_entry = ttk.Entry(input_frame, textvariable=self.excel_folder, width=50)
        excel_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(input_frame, text="浏览...", 
                               command=lambda: self.browse_folder(self.excel_folder))
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        run_btn = ttk.Button(self.excel_tab, text="开始Excel转换", 
                            command=lambda: self.run_script("excel.py"))
        run_btn.pack(pady=10)
    
    def setup_report_tab(self):
        # Report generation tab
        ttk.Label(self.report_tab, text="报告生成").pack(pady=10)
        
        # Create a listbox with scrollbar for displaying available report scripts
        list_frame = ttk.Frame(self.report_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.report_listbox = tk.Listbox(list_frame, height=15, selectmode=tk.SINGLE)
        self.report_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, command=self.report_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate the listbox with scripts from the code directory
        self.load_report_scripts()
        
        run_btn = ttk.Button(self.report_tab, text="运行选中的报告脚本", 
                            command=self.run_selected_report)
        run_btn.pack(pady=10)
        
        refresh_btn = ttk.Button(self.report_tab, text="刷新脚本列表", 
                                command=self.load_report_scripts)
        refresh_btn.pack(pady=5)
    
    def setup_merge_tab(self):
        # File merge tab
        ttk.Label(self.merge_tab, text="合并文本文件").pack(pady=10)
        
        input_frame = ttk.Frame(self.merge_tab)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="输入文件夹:").pack(side=tk.LEFT, padx=5)
        self.input_folder = tk.StringVar(value="output_reports")
        input_entry = ttk.Entry(input_frame, textvariable=self.input_folder, width=50)
        input_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(input_frame, text="浏览...", 
                               command=lambda: self.browse_folder(self.input_folder))
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        output_frame = ttk.Frame(self.merge_tab)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(output_frame, text="输出文件:").pack(side=tk.LEFT, padx=5)
        self.output_file = tk.StringVar(value="报告.txt")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_file, width=50)
        output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        options_frame = ttk.Frame(self.merge_tab)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.add_filename = tk.BooleanVar(value=False)
        add_filename_check = ttk.Checkbutton(options_frame, text="在合并文件中添加原文件名", 
                                            variable=self.add_filename)
        add_filename_check.pack(side=tk.LEFT, padx=5)
        
        encoding_frame = ttk.Frame(self.merge_tab)
        encoding_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(encoding_frame, text="文件编码:").pack(side=tk.LEFT, padx=5)
        self.encoding = tk.StringVar(value="utf-8")
        encoding_combo = ttk.Combobox(encoding_frame, textvariable=self.encoding, 
                                     values=["utf-8", "gbk", "gb2312", "iso-8859-1"])
        encoding_combo.pack(side=tk.LEFT, padx=5)
        
        run_btn = ttk.Button(self.merge_tab, text="开始合并", command=self.run_merge)
        run_btn.pack(pady=10)
    
    def load_report_scripts(self):
        # Clear the listbox
        self.report_listbox.delete(0, tk.END)
        
        # Load scripts from the code directory
        code_dir = "code"
        if os.path.exists(code_dir):
            scripts = [f for f in os.listdir(code_dir) if f.endswith(".py")]
            scripts.sort()
            for script in scripts:
                self.report_listbox.insert(tk.END, script)
        else:
            messagebox.showwarning("警告", f"目录 '{code_dir}' 不存在!")
    
    def browse_folder(self, string_var):
        folder = filedialog.askdirectory()
        if folder:
            string_var.set(folder)
    
    def setup_logging(self):
        """Set up the logging system"""
        # Create logger
        self.logger = logging.getLogger('ScriptManager')
        self.logger.setLevel(logging.DEBUG)
        
        # Create console handler and set level
        console_handler = ConsoleHandler(self.console)
        console_handler.setLevel(logging.DEBUG)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
        
        # Optionally add file handler to save logs to file
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"log_{timestamp}.txt")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(file_handler)
        
        self.logger.info("===== 应用程序启动 =====")
        self.logger.info(f"日志文件: {log_file}")
    
    def run_script(self, script_name):
        """Run a Python script and capture detailed output"""
        def execute():
            self.logger.info(f"开始执行脚本: {script_name}")
            
            try:
                process = subprocess.Popen(
                    [sys.executable, script_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Create reader threads for stdout and stderr
                def read_stdout():
                    for line in iter(process.stdout.readline, ''):
                        self.logger.info(f"[输出] {line.rstrip()}")
                
                def read_stderr():
                    for line in iter(process.stderr.readline, ''):
                        self.logger.error(f"[错误] {line.rstrip()}")
                
                # Start reader threads
                stdout_thread = threading.Thread(target=read_stdout, daemon=True)
                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                stdout_thread.start()
                stderr_thread.start()
                
                # Wait for completion
                stdout_thread.join()
                stderr_thread.join()
                
                return_code = process.wait()
                if return_code == 0:
                    self.logger.info(f"脚本 {script_name} 执行成功 (返回代码: {return_code})")
                else:
                    self.logger.warning(f"脚本 {script_name} 执行结束，但返回代码非零 (返回代码: {return_code})")
                    
            except Exception as e:
                self.logger.error(f"执行脚本 {script_name} 时发生错误: {str(e)}")
        
        threading.Thread(target=execute, daemon=True).start()
    
    def run_selected_report(self):
        selection = self.report_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个报告脚本")
            return
        
        script_name = self.report_listbox.get(selection[0])
        script_path = os.path.join("code", script_name)
        
        if not os.path.exists(script_path):
            messagebox.showerror("错误", f"脚本 '{script_path}' 不存在!")
            return
        
        self.run_script(script_path)
    
    def run_merge(self):
        """Run the merge script with command-line arguments"""
        def execute():
            try:
                cmd = [
                    sys.executable, 
                    "merge_txt_files.py",
                    "-i", self.input_folder.get(),
                    "-o", self.output_file.get(),
                    "--encoding", self.encoding.get()
                ]
                
                if self.add_filename.get():
                    cmd.append("--add-filename")
                
                self.logger.info(f"开始执行合并命令: {' '.join(cmd)}")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Create reader threads for stdout and stderr
                def read_stdout():
                    for line in iter(process.stdout.readline, ''):
                        self.logger.info(f"[输出] {line.rstrip()}")
                
                def read_stderr():
                    for line in iter(process.stderr.readline, ''):
                        self.logger.error(f"[错误] {line.rstrip()}")
                
                # Start reader threads
                stdout_thread = threading.Thread(target=read_stdout, daemon=True)
                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                stdout_thread.start()
                stderr_thread.start()
                
                # Wait for completion
                stdout_thread.join()
                stderr_thread.join()
                
                return_code = process.wait()
                if return_code == 0:
                    self.logger.info(f"合并文件执行成功 (返回代码: {return_code})")
                else:
                    self.logger.warning(f"合并文件执行结束，但返回代码非零 (返回代码: {return_code})")
                    
            except Exception as e:
                self.logger.error(f"执行合并命令时发生错误: {str(e)}")
        
        threading.Thread(target=execute, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptManagerApp(root)
    root.mainloop() 