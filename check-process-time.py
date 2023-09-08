import time
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import win32gui, win32process, psutil
import threading

class MonitorThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.window_title = None
        self.paused = True
        self.active_time = 0

    def run(self):
        last_time_string = "00:00"

        while True:
            current_window_title = get_active_window_title()
            
            if not self.paused and current_window_title == self.window_title:
                self.active_time += 1
                
                minutes, seconds = divmod(self.active_time, 60)
                time_string = "{:02d}:{:02d}".format(minutes, seconds)
                
                usage_string.set(time_string)
                
                last_time_string = time_string
                
            elif current_window_title != self.window_title: 
                usage_string.set(last_time_string)
                
            root.update_idletasks()
            
            time.sleep(1)

def get_active_window_title():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name() # returns the process name instead of the window title 
    except Exception:
        return None

def select_process():
    messagebox.showinfo("Info", "확인을 누르고 3초 이내에 창을 선택해주세요.\nPlease select a window within 3 seconds after closing this dialog.")
    
    root.after(3000, update_process) # Wait for 5 seconds to let user select a window 

def update_process():
    monitor_thread.paused=True # Pause the previous monitoring 
    monitor_thread.window_title=get_active_window_title() # Update to monitor the new window 
    app_name_label.config(text=monitor_thread.window_title) # Update label text with new app name 
    monitor_thread.active_time=0 # Reset active time when a new process is selected.
    
    usage_string.set("00:00")  
    monitor_thread.paused=False # Start monitoring 

def toggle_on_top():
    root.attributes('-topmost', not root.attributes('-topmost'))

# Function for creating tooltip.
def create_tooltip(widget, text):
    tooltipwindow=None

    def show_tooltip(event=None):
        nonlocal tooltipwindow
        
        x,y,cx,cy=widget.bbox("insert")
        x+=widget.winfo_rootx()+25
        y+=widget.winfo_rooty()+25
        
        tooltipwindow=tk.Toplevel(widget)
        tooltipwindow.wm_overrideredirect(True)
        
        tooltipwindow.wm_geometry(f"+{x}+{y}")
            
        label=tk.Label(tooltipwindow,text=text,bg="white",relief="solid",borderwidth=1)
        label.pack()

    def hide_tooltip(event=None):
        nonlocal tooltipwindow
        
        if tooltipwindow is not None:
            tooltipwindow.destroy()
            tooltipwindow=None

    widget.bind("<Enter>",show_tooltip)
    widget.bind("<Leave>",hide_tooltip)

def toggle_on_top():
    # Toggle the 'topmost' attribute
    root.attributes('-topmost', not root.attributes('-topmost'))

    # Update the button text based on the new 'topmost' status
    if root.attributes('-topmost'):
        always_on_top_button.config(text='고정 해제')
    else:
        always_on_top_button.config(text='상단 고정')

class MyApp(ThemedTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('check-process-time')
        try:
            self.iconbitmap('timer.ico')
        except tk.TclError:
            pass  # Ignore if icon file is not available

if __name__=="__main__":
    
    root=MyApp(theme="arc")

    select_button=ttk.Button(root,text='창 선택',command=select_process)
    select_button.grid(row=0,column=0)

always_on_top_button=ttk.Button(root,text='상단 고정',command=lambda: toggle_on_top())
always_on_top_button.grid(row=1,column=0)

# Call 'toggle_on_top' function to set 'Always on Top' as default.
toggle_on_top()

usage_string=tk.StringVar()
usage_string.set("00:00")  # Initialize with 00:00
usage_label_newwindow=tk.Label(root,textvariable=usage_string)
usage_label_newwindow.grid(row=0,column=1)

app_name_label=tk.Label(root,text='측정을 원하는 창을 선택해주세요.')
app_name_label.grid(row=1,column=1)  # Columnspan set to span across two columns.

monitor_thread = MonitorThread()
monitor_thread.start()  # Start the thread immediately

# Add tooltips to buttons.
create_tooltip(select_button, "Click to select a process")
create_tooltip(always_on_top_button, "Click to toggle always on top")

root.mainloop()