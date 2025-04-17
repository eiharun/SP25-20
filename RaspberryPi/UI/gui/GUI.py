import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext

from rfm95api import *
import logging
import time

# also log everything
logger = logging.getLogger(__name__)

class GUI:
    def __init__(self):
        root = tk.Tk()
        trans = Trans(root)
        root.title("Balloon Control Interface")
        
    def run(self):
        try:
            root.mainloop()
        except KeyboardInterrupt:
            print()
            logger.debug("Exiting Ground Station GUI")
            print("Exiting Ground Station GUI")
            exit(0)

class Trans:
    def __init__(self, root):
        self.root = root
        self.rfm95 = RFM95Wrapper().construct()
        logger.debug("RFM95 Constructed")
        self.cmd = Commands.DEFAULT.value
        self.seq = 0

        # cutdown, idle, and entry
        self.cutdown_button = tk.Button(root, text="Cutdown", width=10, height=2, bg='red', font=("Arial", 12), command=self.check_cutdown)
        self.cutdown_button.grid(row=6, column=0, columnspan=1, padx=5, pady=5)

        self.idle_button = tk.Button(root, text="Idle", width=10, height=2, font=("Arial", 12), command=self.check_idle)
        self.idle_button.grid(row=6, column=2, columnspan=1, padx=5, pady=5)

        self.entry = tk.Entry(root, width=20, font=("Arial", 16), justify="center")
        self.entry.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # create buttons
        self.buttons = [
            "1", "2", "3",
            "4", "5", "6",
            "7", "8", "9",
            "Clear", "0", "Enter"
        ]
        
        self.create_buttons()

        # create label
        self.result_label = tk.Label(root, text="", font=("Arial", 12))
        self.result_label.grid(row=5, column=0, columnspan=3, pady=10)

        self.log_box = scrolledtext.ScrolledText(root, width=50, height=10, font=("Courier", 10), state='disabled', wrap='word')
        self.log_box.grid(row=7, column=0, columnspan=4, padx=10, pady=10)

        self.setup_log_tags()


    # create buttons layout
    def create_buttons(self):
        row_val, col_val = 1, 0
        for button in self.buttons:
            if button.isdigit():
                cmd = lambda b=button: self.button_click(b)
            elif button == "Clear":
                cmd = self.clear_entry
            elif button == "Enter":
                cmd = self.check_send

            tk.Button(self.root, text=button, width=6, height=3, font=("Arial", 14), command=cmd).grid(
                row=row_val, column=col_val, padx=5, pady=5
            )

            col_val += 1
            if col_val > 2:
                col_val = 0
                row_val += 1

    # Button click logic
    def button_click(self, number):
        current = self.entry.get()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, current + str(number))

    def clear_entry(self):
        self.result_label.config(text= f"Cleared", fg="green")
        self.entry.delete(0, tk.END)
        self.log("Entry cleared")

    # send commands, confirmation
    def check_send(self):
        
        time_val = self.entry.get()
        # check if there is a valid entry
        if not time_val.isdigit():
            self.result_label.config(text="Please enter a valid number", fg="red")
            self.log("Invalid entry: not a number", tag="error")
            return
        self.entry.delete(0, tk.END)
        # ask for time unit
        self.lockoutstart()
        time_unit = self.ask_time_unit()
        if time_unit == "seconds":
            #commands = 'OPENs'
            self.cmd = Commands.OPENs.value
        else:
            #commands = 'OPENm'
            self.cmd = Commands.OPENm.value
        # confirmation
        if messagebox.askokcancel("Open Confirmation", f"Are you sure you want to open for {time_val} {time_unit}?"):
            self.result_label.config(text= f"Opening for {time_val} {time_unit}", fg="black")
            self.log(f"Opening for {time_val} {time_unit}",tag='info')
            #self.printout(commands)
            self.printout(int(time_val))
        else:
            self.result_label.config(text="Canceling command", fg="orange")
            self.log("User canceled OPEN command", tag="warning")
            
        # re-enable
        self.lockoutend()
        

    # cutdown, confirmation
    def check_cutdown(self):
        self.lockoutstart()
        self.cmd = Commands.CUTDOWN.value
        if messagebox.askokcancel("Cutdown Confirmation", "Are you sure you want to cutdown?"):
            self.log("Sending CUTDOWN command",tag='info')
            #self.printout('CUTDOWN')
            self.printout(b'')
            
        else:
            self.log("User canceled CUTDOWN command", tag="warning")
            self.result_label.config(text= f'Cancel sending cutdown',fg='orange')

        # re-enable 1.5 seconds
        self.lockoutend()

    # idle, no comfirmation text box
    def check_idle(self):
        self.lockoutstart()
        self.cmd = Commands.IDLE.value
        if messagebox.askokcancel("Idle Confirmation", "Are you sure you want to send idle?"):
            self.log("Sending IDLE command",tag="info")
            #self.printout('IDLE')
            self.printout(b'')
        else:
            self.result_label.config(text= f'Cancel sending idle',fg='orange')
            self.log("Canceling IDLE command",tag="warning")
        self.lockoutend()
        
    # sending and receving
    #def printout(self, message):
    def printout(self, arg):
        
        # no need to encode, send the cmd and ack,
        #encode_message = message.encode('utf-8')
        assert self.cmd != Commands.DEFAULT.value
        num_bytes = 0
        payload = b''
        if type(arg) is int:
            num_bytes, payload = self.byte_w_len(arg)
        self.rfm95.send(payload, seq=self.seq, ack=0, CMD=self.cmd, length=num_bytes)
        self.seq = (self.seq+1)%256
        response = self.rfm95.receive(timeout=5.0)  # Wait up to 5 seconds
        if response:
            seq, ack, cmd, length, data = self.rfm95.extractHeaders(response)
            if ack == 1:  # or whatever you use for ACK flag
                self.result_label.config(text= f"ACK received: {ack}", fg='green')
                self.log(f"ACK received, Data: {data}", tag="info")
                self.log(f"Recieved Headers: {seq} {ack} {cmd} {length}")
                self.log(f"Recieved Ack: {data}")
                self.log(f"\tSignal Strength: {self.rfm95.last_rssi}")
                self.log(f"\tSNR: {self.rfm95.last_snr}")

            else:
                self.result_label.config(text= f"Received response, not ACK: {response}",fg='orange')
                self.log(f"Response received (no ACK): {response}", tag="warning")
        else:
            self.result_label.config(text= f"Timeout Waiting", fg='red')
            self.log("Timeout waiting for ACK", tag="error")

    def byte_w_len(self, i:int):
        """
        Returns the number of bytes and the byte array of the given String.
        """
        assert isinstance(i, int), "Argument in byte_w_len() must be a string"
        num_bytes = (i.bit_length() + 7) // 8
        return num_bytes, i.to_bytes(num_bytes, byteorder='big')
    
    def ask_time_unit(self):
        selected_unit = tk.StringVar()

        def choose(unit):
            selected_unit.set(unit)
            popup.destroy()

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Select Time Unit")
        popup.geometry("250x100")
        popup.resizable(False, False)
        popup.grab_set()  # Block interactions with main window until closed

        label = tk.Label(popup, text="Choose time unit:")
        label.pack(pady=10)

        btn_seconds = tk.Button(popup, text="Seconds", width=10, command=lambda: choose("seconds"))
        btn_seconds.pack(side="left", padx=20, pady=10)

        btn_minutes = tk.Button(popup, text="Minutes", width=10, command=lambda: choose("minutes"))
        btn_minutes.pack(side="right", padx=20, pady=10)

        popup.wait_window()  # Wait until popup is closed
        return selected_unit.get()

    #disable every button after send/idle/cutdown
    def lockoutstart(self):
        self.idle_button.config(state='disabled')
        self.entry.config(state='disabled')
        self.cutdown_button.config(state='disabled')
        
    def lockoutend(self):
        self.root.after(1000, lambda: self.idle_button.config(state='normal'))
        self.root.after(1000, lambda: self.entry.config(state='normal'))
        self.root.after(1000, lambda: self.cutdown_button.config(state='normal'))

    def setup_log_tags(self):
        self.log_box.tag_config('info', foreground='black')
        self.log_box.tag_config('warning', foreground='orange')
        self.log_box.tag_config('error', foreground='red')

    def log(self, message, tag='info'):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, f"{message}\n", tag)
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')

# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    trans = Trans(root)
    
    root.title("Balloon Control Interface")

    root.mainloop()
