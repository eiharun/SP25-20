import tkinter as tk
from tkinter import messagebox
import rfm95api
import digitalio
import board
import busio
import adafruit_rfm9x
#rfm95 = RFM95Wrapper(SCK:DigitalInOut,
 #                MOSI:DigitalInOut, 
  #               MISO:DigitalInOut,
   #              CS:DigitalInOut,
   #              RESET:DigitalInOut,
    #             FREQ:float)
    #rfm95.construct()
    ### examples: rfm95.send("hi")
    #find these pins

# RFM95_INT = 0
# RADIO_FREQ_MHZ = 915.0
# CS = digitalio.DigitalInOut(board.D26)
# RESET = digitalio.DigitalInOut(board.D19)
# #TX_LED = A5
# #RX_LED = A6
# spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
# rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ, high_power=True)

class CutOff:
    def __init__(self, root):
        self.root = root

        self.side_button = tk.Button(root, text="Cutoff", width=7, height=4, bg='red', font=("Arial", 12), command=self.confirm_cutoff)
        self.side_button.grid(row=0, column=3, rowspan=4, padx=10, pady=10)  # Placed on the side

    def confirm_cutoff(self):
        if messagebox.askokcancel("Cutoff Confirmation", "Are you sure you want to cutoff?"):
            print("Action confirmed!")
            # Send pin out for cut off
        else:
            print("Action cancelled.")
            # Place the code to execute after cancellation here

class Idle:
    def __init__(self, root):
        self.root = root

        self.side_button = tk.Button(root, text="Idle", width=7, height=4, font=("Arial", 12), command=self.idle)
        self.side_button.grid(row=3, column=3, rowspan=4, padx=10, pady=10)  # Placed on the side

    def idle(self):
        if messagebox.askokcancel("idle Confirmation", "Are you sure you want to cutoff?"):
            print("Action confirmed!")
            # Send pin out for cut off
        else:
            print("Action cancelled.")
            # Place the code to execute after cancellation here

class PinPad:
    def __init__(self, root):
        self.root = root
        
        # Entry Field
        self.entry = tk.Entry(root, width=20, font=("Arial", 16), justify="center")
        self.entry.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        
        # Buttons
        self.buttons = [
            "1", "2", "3",
            "4", "5", "6",
            "7", "8", "9",
            "Clear", "0", "Enter"
        ]
        
        self.create_buttons()
        
        # Side Button
        
        
        # Result Label
        self.result_label = tk.Label(root, text="", font=("Arial", 12))
        self.result_label.grid(row=5, column=0, columnspan=3, pady=10)

    def create_buttons(self):
        """Creates the number pad buttons."""
        row_val, col_val = 1, 0
        for button in self.buttons:
            if button.isdigit():
                cmd = lambda b=button: self.button_click(b)
            elif button == "Clear":
                cmd = self.clear_entry
            elif button == "Enter":
                cmd = self.check_pin

            tk.Button(self.root, text=button, width=6, height=3, font=("Arial", 14), command=cmd).grid(
                row=row_val, column=col_val, padx=5, pady=5
            )

            col_val += 1
            if col_val > 2:
                col_val = 0
                row_val += 1

    def button_click(self, number):
        """Handles button clicks for numbers."""
        current = self.entry.get()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, current + str(number))

    def clear_entry(self):
        self.result_label.config(text= f"Cleared", fg="green")
        self.entry.delete(0, tk.END)

    def check_pin(self):
        entered_pin = self.entry.get()
        if messagebox.askokcancel("Open Confirmation", f"Are you sure you want to open for {entered_pin} seconds?"):
            self.result_label.config(text= f"Opening for {entered_pin} seconds", fg="green")
            # Send pin out for 
        else:
            self.result_label.config(text="Canceling command", fg="red")
            # Place the code to execute after cancellation here

        self.entry.delete(0, tk.END)


# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    pin = PinPad(root)
    cut = CutOff(root)
    idle = Idle(root)
    root.title("Balloon Control Interface")
    root.geometry('500x500')
    root.mainloop()
