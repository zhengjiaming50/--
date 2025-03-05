import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

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
        
        # Console output
        console_frame = ttk.LabelFrame(main_frame, text="运行日志")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.console = tk.Text(console_frame, height=10, wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to console
        scrollbar = ttk.Scrollbar(self.console, command=self.console.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=scrollbar.set)
        
        # Redirect stdout to the console
        sys.stdout = TextRedirector(self.console)
        
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
    
    def run_script(self, script_name):
        def execute():
            try:
                self.console.insert(tk.END, f"正在运行 {script_name}...\n")
                process = subprocess.Popen([sys.executable, script_name], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          universal_newlines=True)
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.console.insert(tk.END, output)
                        self.console.see(tk.END)
                        self.root.update()
                
                rc = process.poll()
                self.console.insert(tk.END, f"{script_name} 执行完毕，返回代码: {rc}\n")
                
            except Exception as e:
                self.console.insert(tk.END, f"错误: {str(e)}\n")
        
        threading.Thread(target=execute).start()
    
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
                
                self.console.insert(tk.END, f"正在运行: {' '.join(cmd)}\n")
                process = subprocess.Popen(cmd, 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          universal_newlines=True)
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.console.insert(tk.END, output)
                        self.console.see(tk.END)
                        self.root.update()
                
                rc = process.poll()
                self.console.insert(tk.END, f"合并文件执行完毕，返回代码: {rc}\n")
                
            except Exception as e:
                self.console.insert(tk.END, f"错误: {str(e)}\n")
        
        threading.Thread(target=execute).start()

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update()

    def flush(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptManagerApp(root)
    root.mainloop() 