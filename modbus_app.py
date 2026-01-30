import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pymodbus.client import ModbusTcpClient
import struct
import json
import csv
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO)

import loginui
import sfisapi

class ModbusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BGA ICT Client")
        self.root.geometry("600x550")

        # Modbus Client
        self.client = None
        self.is_connected = False
        self.auto_running = False
        self.auto_thread = None
        self.modbus_lock = threading.Lock()

        # GUI Variables
        self.ip_var = tk.StringVar(value="192.168.10.20")
        self.port_var = tk.StringVar(value="502")
        self.status_var = tk.StringVar(value="Disconnected")

        # SFIS API
        self.sfis_status = ModbusApp.loadJson("config.json")["SFIS_STATUS"]
        self.web_url = ModbusApp.loadJson("config.json")["WEB_URL"]
        self.device = ModbusApp.loadJson("config.json")["DEVICE"]
        self.station_name = ModbusApp.loadJson("config.json")["STATION_NAME"]
        self.sfis = sfisapi.SFISApi(self.web_url, self.device, self.station_name)

        self.create_widgets()

    def create_widgets(self):
        # Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection Settings")
        conn_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(conn_frame, text="IP:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(conn_frame, textvariable=self.ip_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        ttk.Entry(conn_frame, textvariable=self.port_var, width=10).grid(row=0, column=3, padx=5, pady=5)

        self.btn_connect = ttk.Button(conn_frame, text="Connect", command=self.connect_modbus)
        self.btn_connect.grid(row=0, column=4, padx=5, pady=5)

        self.btn_disconnect = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_modbus, state="disabled")
        self.btn_disconnect.grid(row=0, column=5, padx=5, pady=5)

        # Row 1: Status Display
        # Modbus Status (Left)
        ttk.Label(conn_frame, text="Modbus:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.lbl_modbus_status = tk.Label(conn_frame, text="Disconnected", fg="red", font=("Arial", 10, "bold"))
        self.lbl_modbus_status.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # SFIS Status (Right)
        if self.sfis_status == "True":
            sfis_text = "Online"
            sfis_color = "green"
        else:
            sfis_text = "Offline"
            sfis_color = "red"
            
        ttk.Label(conn_frame, text="SFIS:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.lbl_sfis_status = tk.Label(conn_frame, text=sfis_text, fg=sfis_color, font=("Arial", 10, "bold"))
        self.lbl_sfis_status.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Auto Process Frame
        auto_frame = ttk.LabelFrame(self.root, text="Auto Process")
        auto_frame.pack(padx=10, pady=5, fill="x")

        self.btn_start = ttk.Button(auto_frame, text="Start Auto Process", command=self.start_auto_process, state="disabled")
        self.btn_start.pack(side="left", padx=5, pady=5)

        self.btn_stop = ttk.Button(auto_frame, text="Stop Auto Process", command=self.stop_auto_process, state="disabled")
        self.btn_stop.pack(side="left", padx=5, pady=5)

        # Test Results Frame
        result_frame = ttk.LabelFrame(self.root, text="Results")
        result_frame.pack(padx=10, pady=5, fill="x")

        # Headers
        ttk.Label(result_frame, text="Serial Number", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(result_frame, text="Test Result", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(result_frame, text="SFIS Result", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=2)

        # Result Labels
        # Row 1
        self.sn1 = tk.Label(result_frame, text="<sn1>", width=30, anchor="center")
        self.sn1.grid(row=1, column=0, padx=5, pady=2)
        
        self.sn1_test_result = tk.Label(result_frame, text="", width=8, anchor="center", font=("Arial", 10, "bold"))
        self.sn1_test_result.grid(row=1, column=1, padx=5, pady=2)
        
        self.sn1_sfis_result = tk.Label(result_frame, text="", width=8, anchor="center", font=("Arial", 10, "bold"))
        self.sn1_sfis_result.grid(row=1, column=2, padx=5, pady=2)

        # Row 2
        self.sn2 = tk.Label(result_frame, text="<sn2>", width=30, anchor="center")
        self.sn2.grid(row=2, column=0, padx=5, pady=2)
        
        self.sn2_test_result = tk.Label(result_frame, text="", width=8, anchor="center", font=("Arial", 10, "bold"))
        self.sn2_test_result.grid(row=2, column=1, padx=5, pady=2)
        
        self.sn2_sfis_result = tk.Label(result_frame, text="", width=8, anchor="center", font=("Arial", 10, "bold"))
        self.sn2_sfis_result.grid(row=2, column=2, padx=5, pady=2)

        # Row 3
        self.sn3 = tk.Label(result_frame, text="<sn3>", width=30, anchor="center")
        self.sn3.grid(row=3, column=0, padx=5, pady=2)
        
        self.sn3_test_result = tk.Label(result_frame, text="", width=8, anchor="center", font=("Arial", 10, "bold"))
        self.sn3_test_result.grid(row=3, column=1, padx=5, pady=2)
        
        self.sn3_sfis_result = tk.Label(result_frame, text="", width=8, anchor="center", font=("Arial", 10, "bold"))
        self.sn3_sfis_result.grid(row=3, column=2, padx=5, pady=2)

        # Row 4
        self.sn4 = tk.Label(result_frame, text="<sn4>", width=30, anchor="center")
        self.sn4.grid(row=4, column=0, padx=5, pady=2)
        
        self.sn4_test_result = tk.Label(result_frame, text="", width=8, anchor="center", font=("Arial", 10, "bold"))
        self.sn4_test_result.grid(row=4, column=1, padx=5, pady=2)
        
        self.sn4_sfis_result = tk.Label(result_frame, text="", width=8, anchor="center", font=("Arial", 10, "bold"))
        self.sn4_sfis_result.grid(row=4, column=2, padx=5, pady=2)

        # Log Area
        log_frame = ttk.LabelFrame(self.root, text="Log / Status")
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.log_text = tk.Text(log_frame, state="disabled", height=10)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        # self.log_text['yscrollcommand'] = scrollbar.set # Basic scroll config

        # Time Display (Bottom Right)
        self.lbl_time = tk.Label(self.root, text="", font=("Arial", 10))
        self.lbl_time.pack(side="bottom", anchor="e", padx=10, pady=5)
        self.update_clock()

    def update_clock(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.lbl_time.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        
        # GUI
        self.log_text.config(state="normal")
        self.log_text.insert("end", log_msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        
        # File
        try:
            date_filename = "console_log/" + time.strftime("%Y%m%d") + ".txt"
            with open(date_filename, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
        except Exception as e:
            print(f"Log file error: {e}")

    def connect_modbus(self):
        ip = self.ip_var.get()
        try:
            port = int(self.port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Port must be an integer")
            return

        self.log(f"Connecting to {ip}:{port}...")
        self.client = ModbusTcpClient(ip, port=port)
        
        if self.client.connect():
            with self.modbus_lock:
                self.is_connected = True
            self.status_var.set("Connected")
            self.lbl_modbus_status.config(text="Connected", fg="green")  # Update Status Label
            self.btn_connect.config(state="disabled")
            self.btn_disconnect.config(state="normal")
            self.btn_start.config(state="normal")
            self.log("Connected successfully.")
        else:
            self.log("Connection failed.")
            self.lbl_modbus_status.config(text="Disconnected", fg="red") # Ensure Disconnected
            messagebox.showerror("Error", "Could not connect to Modbus Server")

    def disconnect_modbus(self):
        if self.auto_running:
            self.stop_auto_process()
            # Wait a bit for thread to stop could be better, but simple stop signal is ok for now

        if self.client:
            with self.modbus_lock:
                self.client.close()
        
        with self.modbus_lock:
            self.is_connected = False
        self.status_var.set("Disconnected")
        self.lbl_modbus_status.config(text="Disconnected", fg="red") # Update Status Label
        self.btn_connect.config(state="normal")
        self.btn_disconnect.config(state="disabled")
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="disabled")
        self.log("Disconnected.")

    def start_auto_process(self):
        if not self.is_connected:
            messagebox.showwarning("Warning", "Not connected to Modbus Server")
            return
        
        self.auto_running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.auto_thread = threading.Thread(target=self.run_auto_process, daemon=True)
        self.auto_thread.start()
        
        self.heartbeat_thread = threading.Thread(target=self.heartbeat_worker, daemon=True)
        self.heartbeat_thread.start()

        self.log("Auto process started.")

    def stop_auto_process(self):
        self.auto_running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.log("Stopping auto process and heartbeat...")

    def heartbeat_worker(self):
        val = 0
        while self.auto_running:
            if self.is_connected and self.client:
                try:
                    with self.modbus_lock:
                        self.client.write_register(7000, val)
                    val = 1 if val == 0 else 0
                except Exception as e:
                    self.log(f"Heartbeat error: {e}")
            time.sleep(1)

    def run_auto_process(self):
        while self.auto_running:
            try:
                # Create csv file
                csv_filename = f"test_log_csv/{time.strftime('%Y%m%d')}.csv"
                self.create_csv(Path(csv_filename))

                # Map explicit labels to lists for iteration
                sn_labels = [self.sn1, self.sn2, self.sn3, self.sn4]
                test_result_labels = [self.sn1_test_result, self.sn2_test_result, self.sn3_test_result, self.sn4_test_result]
                sfis_result_labels = [self.sn1_sfis_result, self.sn2_sfis_result, self.sn3_sfis_result, self.sn4_sfis_result]

                # Clear previous results
                for i in range(4):
                    sn_labels[i].config(text="")
                    test_result_labels[i].config(text="")
                    sfis_result_labels[i].config(text="")
                
                # Step 1: Wait for 7001 == 1
                self.log("Step 1: Wait for 7001 == 1...")
                if not self.wait_for_value(7001, 1):
                    continue # Loop check auto_running
                
                self.log("7001 is 1. Reading barcodes...")
                
                # Read barcodes
                # Address mappings: 2100, 2120, 2140, 2160. Count 20 each.
                barcode_data = {}
                barcode_addrs = [2100, 2120, 2140, 2160]
                
                for i, addr in enumerate(barcode_addrs):
                    with self.modbus_lock:
                        rr = self.client.read_holding_registers(addr, count=20)
                    if rr.isError():
                        self.log(f"Error reading {addr}: {rr}")
                        continue
                    
                    raw_values = rr.registers
                    sn = self.process_barcode_data(raw_values)
                    barcode_data[addr] = sn
                    sn_labels[i].config(text=sn) # Update GUI
                    self.log(f"Read SN at {addr}: {sn}")

                # Step 2: Write 7001 = 0
                self.log("Step 2: Writing 7001 = 0")
                with self.modbus_lock:
                    self.client.write_register(7001, 0)
                
                # Step 3: Wait for 7001 == 3
                self.log("Step 3: Waiting for 7001 = 3...")
                if not self.wait_for_value(7001, 3):
                    continue

                self.log("Step 4: 7001 is 3. Reading results...")
                # Step 4: Read results: 2301, 2303, 2305, 2307
                result_addrs = [2301, 2303, 2305, 2307]
                results = {}
                for i, addr in enumerate(result_addrs):
                    with self.modbus_lock:
                        rr = self.client.read_holding_registers(addr, count=1)
                    if not rr.isError():
                        val = rr.registers[0]
                        results[addr] = val
                        # Update GUI
                        res_text = "PASS" if val == 1 else "FAIL" if val == 2 else "ERR"
                        res_color = "green" if val == 1 else "red"
                        test_result_labels[i].config(text=res_text, fg=res_color)
                        
                        self.log(f"Result at {addr}: {val}")
                
                # Step 5: Write 7001 = 0
                self.log("Step 5: Writing 7001 = 0")
                with self.modbus_lock:
                    self.client.write_register(7001, 0)

                # Step 6: Write SFIS results (2190-2193) = 1
                self.log("Step 6: Writing SFIS results...")
                sfis_addrs = [2190, 2191, 2192, 2193]
                if self.sfis_status == "True":
                    for i, (barcode_addr, result_addr, sfis_addr) in enumerate(zip(barcode_addrs, result_addrs, sfis_addrs)):
                        sfis_result, ret = self.sfis_upload(barcode_addr, result_addr)
                        with self.modbus_lock:
                            self.client.write_register(sfis_addr, sfis_result)
                        self.log(f"SFIS result at {sfis_addr}: {sfis_result}")
                        # Update GUI
                        sfis_result_labels[i].config(text="PASS" if sfis_result == 1 else "FAIL", fg="green" if sfis_result == 1 else "red")
                        
                        # Write txt log
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        with open(f"test_log_txt/{barcode_data[barcode_addr]}_{timestamp}.txt", "w") as f:
                            f.write(f"SFIS Status: Online\nSN: {barcode_data[barcode_addr]}\nTest Result: {'PASS' if results[result_addr] == 1 else 'FAIL'}\nSFIS Result: {'PASS' if sfis_result == 1 else 'FAIL'}\nSFIS Message: {ret}")
                        
                        # Write csv log
                        with open(csv_filename, "a", newline="", encoding="utf-8-sig") as f:
                            writer = csv.writer(f)
                            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), barcode_data[barcode_addr], "PASS" if results[result_addr] == 1 else "FAIL", "Online", "PASS" if sfis_result == 1 else "FAIL", ret])

                else:
                    for i, (barcode_addr, result_addr, sfis_addr) in enumerate(zip(barcode_addrs, result_addrs, sfis_addrs)):
                        with self.modbus_lock:
                            self.client.write_register(sfis_addr, 1)
                        self.log(f"SFIS result at {sfis_addr}: 1")
                        # Update GUI
                        sfis_result_labels[i].config(text="Bypass", fg="orange")
                        
                        # Write txt log
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        with open(f"test_log_txt/{barcode_data[barcode_addr]}_{timestamp}.txt", "w") as f:
                            f.write(f"SFIS Status: Offline\nSN: {barcode_data[barcode_addr]}\nTest Result: {'PASS' if results[result_addr] == 1 else 'FAIL'}")

                        # Write csv log
                        with open(csv_filename, "a", newline="", encoding="utf-8-sig") as f:
                            writer = csv.writer(f)
                            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), barcode_data[barcode_addr], "PASS" if results[result_addr] == 1 else "FAIL", "Offline", "", ""])

                # Step 7: Loop (Handled by while true)
                if not self.auto_running:
                     break
                
                time.sleep(10) # Slight delay to prevent aggressive looping

            except Exception as e:
                self.log(f"Exception in auto loop: {e}")
                self.stop_auto_process()
                break

    def wait_for_value(self, address, target_value):
        """Polls address until value matches target or auto_running is False"""
        while self.auto_running:
            try:
                with self.modbus_lock:
                    rr = self.client.read_holding_registers(address, count=1)
                if rr.isError():
                    self.log(f"Read error at {address}")
                    time.sleep(1)
                    continue
                
                if rr.registers[0] == target_value:
                    return True
                
                time.sleep(0.5) # Poll interval
            except Exception as e:
                self.log(f"Error polling {address}: {e}")
                time.sleep(1)
        return False

    def process_barcode_data(self, barcode_list):
        """
        Processes list of 20 registers into a string string according to user logic.
        """
        sn = ""
        try:
            for decimal_number in barcode_list:
                if decimal_number == 0:
                    continue

                hex_number = f"{decimal_number:X}"
                # Ensure even length for fromhex (e.g. if small number 0xA -> "A", need "0A")
                if len(hex_number) % 2 != 0:
                    hex_number = "0" + hex_number
                
                try:
                    ascii_string = bytes.fromhex(hex_number).decode('ascii')
                    reversed_string = ascii_string[::-1]
                    sn += reversed_string
                except ValueError:
                    # Conversion failed (e.g. invalid ascii), append placeholder or skip?
                    # For safety we log and skip or append raw hex?
                    # Stick to precise user logic.
                    pass
            return sn
        except Exception as e:
            self.log(f"Error decoding barcode: {e}")
            return ""

    @staticmethod
    def loadJson(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None

    def create_csv(self, filepath):
        if filepath.exists():
            self.log(f"{filepath} exists")
            return
        else:
            header = ["Time", "SN", "Test Result", "SFIS Status", "SFIS Result", "SFIS Message"]
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(header)
            self.log(f"created {filepath}")

    def sfis_upload(self, sn, test_result):
        if test_result[0] == 1:
            ret = self.sfis.result(sn, "", "ITEM,STATUS,VALUE,UPLIMIT,LOWLIMIT\n")
            if ret[0] == 1:
                sfis_result = 1
                self.log(f"{sn} sfis upload success, message: {ret}")
            else:
                sfis_result = 2
                self.log(f"{sn} sfis upload failed, message: {ret}")
        elif test_result[0] == 2:
            ret = self.sfis.result(sn, "N00AA000005", "ITEM,STATUS,VALUE,UPLIMIT,LOWLIMIT\n")
            if ret[0] == 1:
                sfis_result = 1
                self.log(f"{sn} sfis upload success, message: {ret}")
            else:
                sfis_result = 2
                self.log(f"{sn} sfis upload failed, message: {ret}")
        else:
            ret = None
            self.log(f"test_result of {sn} not defined")
            sfis_result = 2
        return sfis_result, ret

def sfis_login():
    loginform = loginui.LoginForm()
    if loginform.is_login == False:
        return
    else:
        op_id = loginform.OP_ID
        main()

def main():
    root = tk.Tk()
    app = ModbusApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Create the directory automatically
    # parents=True: If parent directories (like 'data' or 'logs') do not exist, create them as well.
    # exist_ok=True: If the directory already exists, do not raise an error (FileExistsError).
    folders_path = ["console_log", "test_log_csv", "test_log_txt"]
    for folder in folders_path:
        Path(folder).mkdir(parents=True, exist_ok=True)

    sfis_status = ModbusApp.loadJson("config.json")["SFIS_STATUS"]
    if sfis_status == "True":
        sfis_login()
    else:
        main()