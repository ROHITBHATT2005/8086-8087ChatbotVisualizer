import tkinter as tk
from tkinter import ttk, scrolledtext
from chatbot import ChatBot

def get_multiline_input(parent, title="Enter 8086 Assembly Program"):
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("700x550")
    dialog.configure(bg="#f5f5f5")
    dialog.transient(parent)
    dialog.grab_set()
    
    dialog.lift()
    dialog.focus_force()

    header = tk.Frame(dialog, bg="#f5f5f5", height=40)
    header.pack(fill=tk.X, padx=20, pady=(15, 5))
    tk.Label(header, text=title, font=("Segoe UI", 13, "bold"),
             fg="#333333", bg="#f5f5f5").pack(side=tk.LEFT)

    editor_frame = tk.Frame(dialog, bg="#f5f5f5", bd=1, relief=tk.SOLID)
    editor_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
    
    text_widget = scrolledtext.ScrolledText(
        editor_frame,
        font=("Cascadia Code", 11),
        bg="#ffffff",
        fg="#333333",
        insertbackground="#0078d4",
        wrap=tk.WORD,
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0
    )
    text_widget.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    text_widget.focus()

    hint = tk.Label(dialog, text="Write one instruction per line. Use ; for comments. Labels like 'LOOP_START:' are supported.",
                    font=("Segoe UI", 9), fg="#666666", bg="#f5f5f5")
    hint.pack(pady=(5, 10))

    result = []

    def submit():
        content = text_widget.get("1.0", tk.END).strip()
        if content:
            result.append(content)
        dialog.destroy()

    def cancel():
        dialog.destroy()

    btn_frame = tk.Frame(dialog, bg="#f5f5f5")
    btn_frame.pack(pady=(0, 20))
    
    execute_btn = tk.Button(
        btn_frame, 
        text="▶ EXECUTE", 
        command=submit,
        bg="#0078d4", 
        fg="#ffffff", 
        font=("Segoe UI", 11, "bold"),
        padx=30, 
        pady=10, 
        relief=tk.RAISED,
        borderwidth=2,
        cursor="hand2"
    )
    execute_btn.pack(side=tk.LEFT, padx=10)
    
    cancel_btn = tk.Button(
        btn_frame, 
        text="Cancel", 
        command=cancel,
        bg="#e0e0e0", 
        fg="#333333", 
        font=("Segoe UI", 11),
        padx=25, 
        pady=10, 
        relief=tk.RAISED,
        borderwidth=2,
        cursor="hand2"
    )
    cancel_btn.pack(side=tk.LEFT, padx=10)

    text_widget.bind("<Control-Return>", lambda e: submit())

    parent.wait_window(dialog)
    return result[0] if result else ""

class Application:
    def __init__(self, master):
        self.master = master
        master.title("Assistant 8086 – 8086/8087 Interactive Simulator")
        master.geometry("1050x750")
        master.minsize(900, 600)
        master.configure(bg="#f5f5f5")

        self.font_default = ("Segoe UI", 10)
        self.font_bold = ("Segoe UI", 10, "bold")
        self.font_code = ("Cascadia Code", 10)

        self.chatbot = ChatBot()
        self._setup_styles()
        self._create_widgets()
        self._display_welcome()
        master.after(100, self._force_focus)
        master.after(500, self._force_focus)
        master.bind("<Button-1>", lambda e: self.input_entry.focus_set())

    def _force_focus(self):
        self.input_entry.focus_set()
        self.input_entry.config(state=tk.NORMAL)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#f5f5f5", borderwidth=0)
        style.configure("TNotebook.Tab", background="#e0e0e0", foreground="#333333",
                        padding=[15, 5], font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#0078d4")],
                  foreground=[("selected", "#ffffff")])
        style.configure("TFrame", background="#f5f5f5")

    def _create_widgets(self):
        main_container = tk.Frame(self.master, bg="#f5f5f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.sidebar = tk.Frame(main_container, bg="#e8e8e8", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        right_area = tk.Frame(main_container, bg="#f5f5f5")
        right_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        chat_header = tk.Frame(right_area, bg="#f5f5f5", height=35)
        chat_header.pack(fill=tk.X, pady=(0, 5))
        tk.Label(chat_header, text="💬 Conversation", font=("Segoe UI", 11, "bold"),
                 fg="#333333", bg="#f5f5f5").pack(side=tk.LEFT)
        tk.Button(chat_header, text="Clear", command=self._clear_chat,
                  bg="#e0e0e0", fg="#333333", font=("Segoe UI", 9),
                  relief=tk.FLAT, cursor="hand2", padx=10).pack(side=tk.RIGHT)

        chat_frame = tk.Frame(right_area, bg="#f5f5f5")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=self.font_code,
            bg="#ffffff",
            fg="#333333",
            insertbackground="#0078d4",
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightcolor="#cccccc",
            highlightbackground="#cccccc",
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(right_area, bg="#f5f5f5", height=50)
        input_frame.pack(fill=tk.X, pady=(5, 10))
        input_frame.pack_propagate(False)

        self.input_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg="#ffffff",
            fg="#333333",
            insertbackground="#0078d4",
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightcolor="#0078d4",
            highlightbackground="#cccccc",
            state=tk.NORMAL
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", self._on_send)

        send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self._on_send,
            bg="#0078d4",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            relief=tk.FLAT,
            cursor="hand2"
        )
        send_btn.pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(right_area)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self._build_status_tabs()

        self.chat_display.tag_config("user", foreground="#0078d4", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("bot", foreground="#107c10", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("system", foreground="#c43e2c", font=("Segoe UI", 10, "bold"))

    def _build_sidebar(self):
        header = tk.Frame(self.sidebar, bg="#d0d0d0", height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="⚡ Quick Commands", font=("Segoe UI", 11, "bold"),
                 fg="#333333", bg="#d0d0d0").pack(expand=True)

        actions = [
            ("▶ Run Program", self._run_program, "Open multi-line editor"),
            ("🎓 Tutorial", self._start_tutorial, "Step-by-step assembly lesson"),
            ("📊 Show CPU", self._show_cpu, "Display register state"),
            ("💾 Show Memory", self._show_memory, "View first 64 bytes"),
            ("📚 Show FPU", self._show_fpu, "Display FPU stack"),
            ("🔄 Reset CPU", self._reset_cpu, "Clear registers & memory"),
            ("🔁 Reset FPU", self._reset_fpu, "Clear FPU stack"),
            ("❓ Help", self._show_help, "List all commands"),
        ]

        for text, cmd, tooltip in actions:
            btn = tk.Button(
                self.sidebar,
                text=text,
                command=cmd,
                bg="#e8e8e8",
                fg="#333333",
                font=("Segoe UI", 10),
                relief=tk.FLAT,
                anchor="w",
                padx=15,
                pady=8,
                cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=1)
            self._create_tooltip(btn, tooltip)

        tk.Frame(self.sidebar, bg="#cccccc", height=2).pack(fill=tk.X, pady=10)

        tk.Label(self.sidebar, text="📋 Try these:", font=("Segoe UI", 10, "bold"),
                 fg="#333333", bg="#e8e8e8").pack(anchor="w", padx=10, pady=(5, 5))

        examples = [
            "add 5 6",
            "multiply 7 by 8",
            "sqrt of 25",
            "MOV AX, 10",
            "store 1234 at 1000",
            "load from [1000]",
            "show stack"
        ]
        for ex in examples:
            tk.Label(self.sidebar, text=f"• {ex}", font=("Segoe UI", 9),
                     fg="#555555", bg="#e8e8e8", anchor="w").pack(anchor="w", padx=15, pady=2)

        tk.Frame(self.sidebar, bg="#e8e8e8", height=20).pack(fill=tk.X, expand=True)
        tk.Label(self.sidebar, text="MPMC Project v2.0", font=("Segoe UI", 8),
                 fg="#888888", bg="#e8e8e8").pack(side=tk.BOTTOM, pady=10)

    def _create_tooltip(self, widget, text):
        tooltip = None
        def enter(event):
            nonlocal tooltip
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + 25
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(tooltip, text=text, bg="#333333", fg="#ffffff",
                             font=("Segoe UI", 9), relief=tk.SOLID, borderwidth=1,
                             padx=8, pady=4)
            label.pack()
        def leave(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _build_status_tabs(self):
        cpu_frame = ttk.Frame(self.notebook)
        self.notebook.add(cpu_frame, text="8086 CPU")
        self.cpu_text = tk.Text(cpu_frame, font=self.font_code, bg="#ffffff", fg="#333333",
                                relief=tk.FLAT, borderwidth=0, padx=10, pady=10)
        self.cpu_text.pack(fill=tk.BOTH, expand=True)

        fpu_frame = ttk.Frame(self.notebook)
        self.notebook.add(fpu_frame, text="8087 FPU")
        self.fpu_text = tk.Text(fpu_frame, font=self.font_code, bg="#ffffff", fg="#333333",
                                relief=tk.FLAT, borderwidth=0, padx=10, pady=10)
        self.fpu_text.pack(fill=tk.BOTH, expand=True)

        mem_frame = ttk.Frame(self.notebook)
        self.notebook.add(mem_frame, text="Memory")
        mem_control = tk.Frame(mem_frame, bg="#f5f5f5")
        mem_control.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(mem_control, text="Address:", bg="#f5f5f5", fg="#333333").pack(side=tk.LEFT)
        self.mem_addr_entry = tk.Entry(mem_control, width=8, bg="#ffffff", fg="#333333",
                                       insertbackground="#0078d4", font=self.font_code)
        self.mem_addr_entry.pack(side=tk.LEFT, padx=5)
        self.mem_addr_entry.insert(0, "0000")
        tk.Button(mem_control, text="View", command=self._update_memory_dump,
                  bg="#0078d4", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, cursor="hand2", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(mem_control, text="Stack", command=lambda: self._update_memory_dump(stack=True),
                  bg="#e0e0e0", fg="#333333", font=("Segoe UI", 9),
                  relief=tk.FLAT, cursor="hand2", padx=10).pack(side=tk.LEFT, padx=5)
        self.mem_text = tk.Text(mem_frame, font=self.font_code, bg="#ffffff", fg="#333333",
                                relief=tk.FLAT, borderwidth=0, padx=10, pady=10)
        self.mem_text.pack(fill=tk.BOTH, expand=True)

    def _display_welcome(self):
        welcome = """Welcome to MPMC Assistant! 👋

I'm your interactive 8086/8087 simulator. You can:
• Perform arithmetic: "add 5 and 6", "multiply 7 by 8"
• Use assembly: "MOV AX, 5", "ADD AX, 3"
• Work with memory: "store 1234 at 1000", "load from [1000]"
• Explore FPU: "sqrt of 25", "fadd 3.14 2.86"

Type 'help' for a full command list, or click the sidebar buttons.
"""
        self.display_message("Bot", welcome)

    def _clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self._display_welcome()

    def _run_program(self):
        program = get_multiline_input(self.master)
        if program:
            response = self.chatbot._execute_program(program)
            self.display_message("Bot", response)
            self._update_status()
        else:
            self.display_message("Bot", "Program execution cancelled or empty.")

    def _start_tutorial(self):
        response = self.chatbot._start_tutorial()
        self.display_message("Bot", response)

    def _show_cpu(self):
        state = self.chatbot.cpu.get_state()
        self.display_message("Bot", f"📊 Current CPU State:\n{state}")
        self._update_status()

    def _show_memory(self):
        dump = self.chatbot.cpu.memory.dump(0, 64)
        self.display_message("Bot", f"💾 Memory Dump (first 64 bytes):\n{dump}")
        self._update_status()

    def _show_fpu(self):
        stack = self.chatbot.fpu.get_stack_state()
        self.display_message("Bot", f"📚 FPU Stack:\n{stack}")
        self._update_status()

    def _reset_cpu(self):
        self.chatbot.cpu.reset()
        self.chatbot.last_cpu_result = None
        self.display_message("Bot", "✅ CPU has been reset. All registers, flags, and memory cleared.")
        self._update_status()

    def _reset_fpu(self):
        self.chatbot.fpu.reset()
        self.chatbot.last_fpu_result = None
        self.display_message("Bot", "✅ FPU has been reset. Stack cleared.")
        self._update_status()

    def _show_help(self):
        response = self.chatbot._get_help()
        self.display_message("Bot", response)

    def _update_memory_dump(self, stack=False):
        if stack:
            sp = self.chatbot.cpu.sp
            addr = max(0, sp - 32)
        else:
            try:
                addr = int(self.mem_addr_entry.get(), 16) & 0xFFF0
            except:
                addr = 0
        dump = self.chatbot.cpu.memory.dump(addr, 64)
        self.mem_text.config(state=tk.NORMAL)
        self.mem_text.delete(1.0, tk.END)
        self.mem_text.insert(tk.END, f"Base: 0x{addr:04X}\n{dump}")
        self.mem_text.config(state=tk.DISABLED)

    def _update_status(self):
        self.cpu_text.config(state=tk.NORMAL)
        self.cpu_text.delete(1.0, tk.END)
        self.cpu_text.insert(tk.END, self.chatbot.cpu.get_state())
        self.cpu_text.config(state=tk.DISABLED)

        self.fpu_text.config(state=tk.NORMAL)
        self.fpu_text.delete(1.0, tk.END)
        self.fpu_text.insert(tk.END, self.chatbot.fpu.get_stack_state())
        self.fpu_text.config(state=tk.DISABLED)

        self._update_memory_dump()

    def display_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        tag = "user" if sender == "You" else "bot" if sender == "Bot" else "system"
        self.chat_display.insert(tk.END, f"\n{sender}: ", tag)
        self.chat_display.insert(tk.END, f"{message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _on_send(self, event=None):
        user_text = self.input_entry.get().strip()
        if not user_text:
            return

        self.display_message("You", user_text)
        self.input_entry.delete(0, tk.END)

        if user_text.lower() == "run program":
            self._run_program()
            return
        if user_text.lower() == "tutorial":
            self._start_tutorial()
            return

        response = self.chatbot.process_input(user_text)
        self.display_message("Bot", response)
        self._update_status()

        if user_text.lower() in ['bye', 'goodbye', 'exit', 'quit']:
            self.master.after(1500, self.master.destroy)
        else:
            self.input_entry.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()