import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext

from UI.rfm95api import *
import logging

logger = logging.getLogger(__name__)

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        trans = Trans(self.root)
        self.root.title("Balloon Control Interface")
        
    def run(self):
        try:
            self.root.geometry("{}x{}+0+0". format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
            self.root.mainloop()
        except KeyboardInterrupt:
            print()
            logger.debug("Exiting Ground Station GUI")
            print("Exiting Ground Station GUI")
            exit(0)

class Trans:
    #------------------------------------------------------UI-----------------------------------------------------------#
    def __init__(self, root):
        self.root = root
        self.rfm95 = RFM95Wrapper().construct()
        logger.debug("RFM95 Constructed")
        self.cmd = Commands.DEFAULT.value
        self.seq = 0
        self.RFMtimeout = 5

        # cutdown, idle, close, and entry
        self.cutdown_button = tk.Button(root, text="Cutdown", width=12, height=6, bg='red', font=("Arial", 20), command=self.check_cutdown)
        self.cutdown_button.grid(row=1, column=3, padx=5, pady=5)

        self.idle_button = tk.Button(root, text="Idle", width=12, height=6, font=("Arial", 20), command=self.check_idle)
        self.idle_button.grid(row=2, column=3, padx=5, pady=5)

        self.close_button = tk.Button(root, text="Close", width=12, height=6, font=("Arial", 20), command=self.check_close)
        self.close_button.grid(row=3, column=3, padx=5, pady=5)

        self.set_button = tk.Button(root, text="Set Timeout", width=12, height=6, font=("Arial", 20), command=self.set_timeout)
        self.set_button.grid(row=4, column=3, padx=5, pady=5)

        self.entry = tk.Entry(root, width=40, font=("Arial", 20), justify="center")
        self.entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # create buttons
        self.buttons = [
            "1", "2", "3",
            "4", "5", "6",
            "7", "8", "9",
            "Clear", "0", "Open"
        ]
        
        self.create_buttons()

        # create label
        self.result_label = tk.Label(root, text="", font=("Arial", 20))
        self.result_label.grid(row=5, column=0, columnspan=4, pady=10)

        self.log_box = scrolledtext.ScrolledText(root, width=65, height=30, font=("Courier", 20), state='disabled', wrap='word')
        self.log_box.grid(row=0, column=4, rowspan=5, padx=10, pady=10)

        self.setup_log_tags()

    def create_buttons(self):
        row_val, col_val = 1, 0
        for button in self.buttons:
            if button.isdigit():
                cmd = lambda b=button: self.button_click(b)
            elif button == "Clear":
                cmd = self.clear_entry
            elif button == "Open":
                cmd = self.check_send

            tk.Button(self.root, text=button, width=12, height=6, font=("Arial", 20), command=cmd).grid(
                row=row_val, column=col_val, padx=5, pady=5
            )

            col_val += 1
            if col_val > 2:
                col_val = 0
                row_val += 1

    def button_click(self, number):
        current = self.entry.get()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, current + str(number))

    def clear_entry(self):
        self.result_label.config(text= f"Cleared", fg="green")
        self.entry.delete(0, tk.END)
        self.log("Entry cleared")

    #---------------------------------------------COMMANDS------------------------------------------------------#
    def check_send(self):
        time_val = self.entry.get()
        # check if there is a valid entry
        if not time_val.isdigit():
            self.result_label.config(text="Please enter a valid number", fg="red")
            self.log("Invalid entry: not a number", tag="error")
            return
        self.entry.delete(0, tk.END)
        time_unit = self.ask(purpose="TimeUnit", message=None)
    
        pTime = time_val if time_unit == "minutes" else time_val
        time_val = time_val*60 if time_unit == "minutes" else time_val
        self.cmd = Commands.OPEN.value
        
        # confirmation
        self.lockoutstart()
        if self.ask(purpose="Confirmation", message =f"Are you sure you want to open for {pTime} {time_unit}?" ) == "OK":
            self.result_label.config(text= f"Opening for {pTime} {time_unit}", fg="black")
            self.log(f"Opening for {time_val} {time_unit}",tag='info')
            self.printout(int(time_val))
        else:
            self.result_label.config(text="Canceled OPEN command", fg="black")
            self.log("User canceled OPEN command", tag="info")  
        self.lockoutend()
        
    def check_cutdown(self):
        self.cmd = Commands.CUTDOWN.value
        self.lockoutstart()
        if self.ask(purpose="Confirmation", message ="Are you sure you want to cutdown?" ) == "OK":
            self.log("Sending CUTDOWN command",tag='info')
            self.printout()
        else:
            self.log("User canceled CUTDOWN command", tag="info")
            self.result_label.config(text= f'Canceled CUTDOWN command',fg='black')

        self.lockoutend()

    def check_close(self):
        self.cmd = Commands.CLOSE.value
        self.lockoutstart()
        if self.ask(purpose="Confirmation", message ="Are you sure you want to closes the vent?" ) == "OK":
            self.log("Sending CLOSE command",tag='info')
            self.printout()
        else:
            self.log("User canceled CLOSE command", tag="info")
            self.result_label.config(text= f'Canceled CLOSE command',fg='black')
        self.lockoutend()

    def check_idle(self):
        self.cmd = Commands.IDLE.value
        self.lockoutstart()
        self.log("Sending IDLE command",tag="info")
        self.printout()
        self.lockoutend()
        
    def printout(self, arg = b''):
        #pass
        assert self.cmd != Commands.DEFAULT.value, "Invalid command"
        num_bytes, payload = 0, b''
        if type(arg) is int:
            num_bytes, payload = self.byte_w_len(arg)

        self.rfm95.send(payload, seq=self.seq, ack=0, CMD=self.cmd, length=num_bytes)
        self.seq = (self.seq+1)%256
        response = self.rfm95.receive(timeout=self.RFMtimeout)

        if response:
            seq, ack, cmd, length, data = self.rfm95.extractHeaders(response)
            if cmd == Commands.BUSY.value:
                self.log("Motor is busy\n")
                self.flash_screen("yellow")
            else:
                self.flash_screen()
            self.result_label.config(text= f"ACK received", fg='green')
            self.log(f"Recieved Headers: {seq} {ack} {cmd} {length}")
            self.log(f"Data: {data}")
            self.log(f"\tSignal Strength: {self.rfm95.last_rssi}")
            self.log(f"\tSNR: {self.rfm95.last_snr}")

        else:
            self.result_label.config(text= f"Timeout Waiting", fg='red')
            self.log("Timeout waiting for ACK", tag="error")

    #---------------------------------------HELPERS-----------------------------------------#   
    def ask(self, purpose, message):
        selected = tk.StringVar()

        def choose(unit):
            selected.set(unit)
            popup.destroy()
        popup = tk.Toplevel(self.root)
        popup.grab_set() 
        if purpose == "TimeUnit":
            title ="Select Time Unit"
            text = "Choose time unit:"
            left_text = "seconds"
            right_text = "minutes"
            label = tk.Label(popup, text=text ,font=("Arial", 20))
            
        elif purpose == "Confirmation":
            title = purpose
            text = message
            left_text = "Cancel"
            right_text = "OK"
            label = tk.Label(popup, text=text ,font=("Arial", 15))

        # Create popup window
        
        popup.title(title)
        popup.geometry("500x200")
        popup.resizable(False, False)
        label.pack(pady=10)
        btn_seconds = tk.Button(popup, text=left_text, width=10,font=("Arial", 20), command=lambda: choose(left_text))
        btn_seconds.pack(side="left", padx=20, pady=10)
        btn_minutes = tk.Button(popup, text=right_text, width=10,font=("Arial", 20), command=lambda: choose(right_text))
        btn_minutes.pack(side="right", padx=20, pady=10)

        popup.wait_window() 
        return selected.get()

    def lockoutstart(self):
        self.idle_button.config(state='disabled')
        self.entry.config(state='disabled')
        self.cutdown_button.config(state='disabled')
        self.close_button.config(state='disabled')
        self.set_button.config(state='disabled')
        
    def lockoutend(self):
        self.root.after(1500, lambda: self.idle_button.config(state='normal'))
        self.root.after(1500, lambda: self.entry.config(state='normal'))
        self.root.after(1500, lambda: self.cutdown_button.config(state='normal'))
        self.root.after(1500, lambda: self.close_button.config(state='normal'))
        self.root.after(1500, lambda: self.set_button.config(state='normal'))

    def setup_log_tags(self):
        self.log_box.tag_config('info', foreground='black')
        self.log_box.tag_config('warning', foreground='orange')
        self.log_box.tag_config('error', foreground='red')

    def log(self, message, tag='info'):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, f"{message}\n", tag)
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')

    def byte_w_len(self, i:int):
        assert isinstance(i, int), "Argument in byte_w_len() must be a string"
        num_bytes = (i.bit_length() + 7) // 8
        return num_bytes, i.to_bytes(num_bytes, byteorder='big')
    
    def flash_screen(self, color="green", duration=100):
        original_color = self.root["bg"]
        self.root.configure(bg=color)
        self.root.after(duration, lambda: self.root.configure(bg=original_color))

    def set_timeout(self):
        time_val = self.entry.get()
        if not time_val.isdigit():
            self.result_label.config(text="Please enter a valid number", fg="red")
            self.log("Invalid entry: not a number", tag="error")
            return
        time_val = int(time_val)
        if time_val > 30 or time_val < 0:
            self.result_label.config(text="Please enter a valid number", fg="red")
            self.log("Timeout can only be between 0 and 30 seconds", tag="error")
            return
        self.entry.delete(0, tk.END)
        
        self.lockoutstart()
        if self.ask(purpose="Confirmation", message= f"Are you sure you want to set the timeout to {time_val}?") == "OK":
            self.result_label.config(text= f"Set timeout to {time_val} seconds", fg="black")
            self.log(f"Set timeout to {time_val} seconds",tag='info')
            self.RFMtimeout = time_val
        else:
            self.log("User canceled setting timout", tag="info")
            self.result_label.config(text= f'Canceled setting timout',fg='black')
        self.lockoutend()


# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    trans = Trans(root)
    root.title("Balloon Control Interface")
   
    root.geometry("{}x{}+0+0". format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.mainloop()
