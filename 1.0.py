import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu
import urllib.request
import urllib.error
import ssl
from threading import Thread
import webbrowser

class WebSourceSnap:
    def __init__(self, root):
        self.root = root
        self.language = "zh_CN"  # 默认语言为中文
        self.init_ui()
        
        # 创建菜单栏
        self.create_menu()
        
    def init_ui(self):
        """初始化用户界面"""
        self.root.title("源码快捕 (WebSourceSnap)" if self.language == "zh_CN" else "WebSourceSnap")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # 添加名称横幅
        name_frame = tk.Frame(self.root, bg="#2c3e50", height=40)
        name_frame.pack(fill="x", pady=(0,10))
        self.banner_label = tk.Label(name_frame, 
                 text="源码快捕 · WebSourceSnap" if self.language == "zh_CN" else "WebSourceSnap", 
                 fg="white", bg="#2c3e50",
                 font=("微软雅黑", 14, "bold") if self.language == "zh_CN" else ("Arial", 14, "bold"))
        self.banner_label.pack(pady=8)
        
        # 创建法律声明
        self.legal_frame = tk.LabelFrame(self.root, 
                                        text=self.get_text("terms_title"), 
                                        padx=5, pady=5)
        self.legal_frame.pack(fill="x", padx=10, pady=5)
        
        legal_text = self.get_text("terms_content")
        self.legal_label = tk.Label(self.legal_frame, text=legal_text, justify="left", fg="red")
        self.legal_label.pack(anchor="w")
        
        # 创建URL输入区域
        url_frame = tk.Frame(self.root)
        url_frame.pack(fill="x", padx=10, pady=10)
        
        self.url_label = tk.Label(url_frame, text=self.get_text("target_url"))
        self.url_label.pack(side="left")
        self.url_entry = tk.Entry(url_frame, width=60)
        self.url_entry.pack(side="left", padx=5)
        self.url_entry.insert(0, "https://")
        
        # 创建按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        self.fetch_button = tk.Button(button_frame, text=self.get_text("fetch_source"), 
                                    command=self.start_fetch_thread)
        self.fetch_button.pack(side="left", padx=5)
        
        self.clear_button = tk.Button(button_frame, text=self.get_text("clear_results"), 
                                    command=self.clear_results)
        self.clear_button.pack(side="left", padx=5)
        
        # 添加复制按钮
        self.copy_button = tk.Button(button_frame, text=self.get_text("copy_source"), 
                                   command=self.copy_to_clipboard)
        self.copy_button.pack(side="left", padx=5)
        self.copy_button.config(state="disabled")  # 初始禁用
        
        self.exit_button = tk.Button(button_frame, text=self.get_text("exit"), 
                                   command=self.root.quit)
        self.exit_button.pack(side="left", padx=5)
        
        # 创建结果显示区域
        self.result_frame = tk.LabelFrame(self.root, text=self.get_text("source_code"), 
                                        padx=5, pady=5)
        self.result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.result_area = scrolledtext.ScrolledText(self.result_frame, wrap="word")
        self.result_area.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 创建状态栏
        self.status_var = tk.StringVar()
        self.status_var.set(self.get_text("ready"))
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             bd=1, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = Menu(self.root)
        
        # 文件菜单
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.get_text("exit"), command=self.root.quit)
        menubar.add_cascade(label=self.get_text("file_menu"), menu=file_menu)
        
        # 语言菜单
        language_menu = Menu(menubar, tearoff=0)
        language_menu.add_command(label="中文", command=lambda: self.set_language("zh_CN"))
        language_menu.add_command(label="English", command=lambda: self.set_language("en_US"))
        menubar.add_cascade(label=self.get_text("language_menu"), menu=language_menu)
        
        # 帮助菜单
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.get_text("about"), command=self.show_about)
        help_menu.add_command(label=self.get_text("repo_link"), command=self.open_repo)
        help_menu.add_command(label=self.get_text("author_link"), command=self.open_author)
        menubar.add_cascade(label=self.get_text("help_menu"), menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def get_text(self, key):
        """获取当前语言的文本"""
        translations = {
            "zh_CN": {
                "terms_title": "使用条款",
                "terms_content": "本工具仅用于教育目的，禁止用于以下行为：\n"
                                "1. 未经授权的网站数据爬取\n"
                                "2. 侵犯他人隐私或知识产权\n"
                                "3. 对目标服务器造成过大负载\n"
                                "4. 违反目标网站robots.txt协议\n\n"
                                "使用本工具即表示您同意承担所有相关责任。",
                "target_url": "目标URL:",
                "fetch_source": "获取源码",
                "clear_results": "清空结果",
                "copy_source": "复制源码",
                "exit": "退出",
                "source_code": "网页源码",
                "ready": "就绪",
                "file_menu": "文件",
                "language_menu": "语言",
                "help_menu": "帮助",
                "about": "关于",
                "repo_link": "仓库地址",
                "author_link": "作者主页",
                "connecting": "正在连接服务器...",
                "success": "成功获取: {} {}",
                "http_error": "HTTP错误: {} {}",
                "url_error": "URL错误: {}",
                "error": "错误: {}",
                "copied": "源码已复制到剪贴板",
                "copy_success": "网页源码已成功复制到剪贴板！",
                "copy_warning": "结果区域为空，没有内容可复制",
                "cleared": "已清空结果",
                "about_title": "关于源码快捕",
                "about_content": "源码快捕 (WebSourceSnap)\n版本: 1.0\n\n一个简单易用的网页源码获取工具",
                "invalid_url": "URL必须以http://或https://开头"
            },
            "en_US": {
                "terms_title": "Terms of Use",
                "terms_content": "This tool is for educational purposes only. Prohibited uses include:\n"
                                "1. Unauthorized web scraping\n"
                                "2. Violating privacy or intellectual property rights\n"
                                "3. Overloading target servers\n"
                                "4. Violating robots.txt protocols\n\n"
                                "By using this tool, you agree to take full responsibility for your actions.",
                "target_url": "Target URL:",
                "fetch_source": "Fetch Source",
                "clear_results": "Clear Results",
                "copy_source": "Copy Source",
                "exit": "Exit",
                "source_code": "Webpage Source Code",
                "ready": "Ready",
                "file_menu": "File",
                "language_menu": "Language",
                "help_menu": "Help",
                "about": "About",
                "repo_link": "Repository",
                "author_link": "Author's Page",
                "connecting": "Connecting to server...",
                "success": "Success: {} {}",
                "http_error": "HTTP Error: {} {}",
                "url_error": "URL Error: {}",
                "error": "Error: {}",
                "copied": "Source code copied to clipboard",
                "copy_success": "Webpage source code copied to clipboard!",
                "copy_warning": "Result area is empty, nothing to copy",
                "cleared": "Results cleared",
                "about_title": "About WebSourceSnap",
                "about_content": "WebSourceSnap\nVersion: 1.0\n\nA simple tool for fetching webpage source code",
                "invalid_url": "URL must start with http:// or https://"
            }
        }
        return translations[self.language].get(key, key)
    
    def set_language(self, lang_code):
        """设置界面语言"""
        self.language = lang_code
        # 重新加载界面
        self.reload_ui()
    
    def reload_ui(self):
        """重新加载界面以应用新语言"""
        # 销毁所有子组件
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 重新初始化界面
        self.init_ui()
        
        # 重新创建菜单
        self.create_menu()
        
        # 恢复状态栏消息
        self.set_status(self.get_text("ready"))
    
    def start_fetch_thread(self):
        """启动新线程获取网页内容"""
        Thread(target=self.fetch_website, daemon=True).start()
    
    def fetch_website(self):
        """获取网页源码"""
        url = self.url_entry.get().strip()
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror(self.get_text("error"), self.get_text("invalid_url"))
            return
        
        self.set_status(self.get_text("connecting"))
        self.fetch_button.config(state="disabled")
        self.copy_button.config(state="disabled")  # 获取过程中禁用复制按钮
        
        try:
            # 创建SSL上下文绕过证书验证（仅用于教育目的）
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # 设置浏览器头部信息
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, context=context, timeout=10) as response:
                charset = response.headers.get_content_charset() or 'utf-8'
                html_content = response.read().decode(charset, errors='replace')
                
                self.result_area.delete(1.0, tk.END)
                self.result_area.insert(tk.END, html_content)
                self.set_status(self.get_text("success").format(response.status, response.reason))
                
                # 启用复制按钮
                self.copy_button.config(state="normal")
                
        except urllib.error.HTTPError as e:
            self.set_status(self.get_text("http_error").format(e.code, e.reason))
            messagebox.showerror(self.get_text("error"), 
                               f"{self.get_text('http_error')}: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            self.set_status(self.get_text("url_error").format(str(e.reason)))
            messagebox.showerror(self.get_text("error"), 
                               f"{self.get_text('url_error')}: {e.reason}")
        except Exception as e:
            self.set_status(self.get_text("error").format(str(e)))
            messagebox.showerror(self.get_text("error"), 
                               f"{self.get_text('error')}: {str(e)}")
        finally:
            self.fetch_button.config(state="normal")
    
    def copy_to_clipboard(self):
        """将源码复制到剪贴板"""
        content = self.result_area.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning(self.get_text("copy_warning"), 
                                  self.get_text("copy_warning"))
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.set_status(self.get_text("copied"))
        messagebox.showinfo(self.get_text("copy_success"), 
                           self.get_text("copy_success"))
    
    def clear_results(self):
        """清空结果区域"""
        self.result_area.delete(1.0, tk.END)
        self.copy_button.config(state="disabled")  # 清空后禁用复制按钮
        self.set_status(self.get_text("cleared"))
    
    def set_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_about(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title(self.get_text("about_title"))
        about_window.geometry("300x200")
        about_window.resizable(False, False)
        
        # 添加关于信息
        tk.Label(about_window, text=self.get_text("about_content"), 
               justify="left", padx=10, pady=10).pack(fill="both", expand=True)
        
        # 添加关闭按钮
        tk.Button(about_window, text="OK", command=about_window.destroy).pack(pady=10)
    
    def open_repo(self):
        """打开仓库地址"""
        repo_url = "https://github.com/xiaoboCN567/WebSourceSnap/tree/78f84f94b760661ffd5a29e2766ec3c05ee80f78"
        webbrowser.open(repo_url)
    
    def open_author(self):
        """打开作者主页"""
        author_url = "https://github.com/xiaoboCN567"
        webbrowser.open(author_url)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebSourceSnap(root)
    root.mainloop()
