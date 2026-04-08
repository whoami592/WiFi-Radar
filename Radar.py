# =====================================================
# PYTHON WIFI RADAR SCANNER + GUI
# Coded by Mr. Sabaz Ali Khan - Pakistan Cyber Security Engineer
# Works on Windows (netsh) and Linux (nmcli)
# =====================================================

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform
import threading
import time
import math
import random


class WiFiRadarScanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Python WiFi Radar Scanner - Mr. Sabaz Ali Khan")
        self.root.geometry("1280x720")
        self.root.configure(bg="#000000")
        self.root.resizable(True, True)

        self.scanning = False
        self.networks = []
        self.os_name = platform.system()

        self.create_gui()

    def create_gui(self):
        # Header
        header = tk.Frame(self.root, bg="#001100", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="🚀 PYTHON WIFI RADAR SCANNER 🚀", 
                 font=("Press Start 2P", 18, "bold"), fg="#00ff00", bg="#001100").pack(pady=8)
        tk.Label(header, text="Coded by Mr. Sabaz Ali Khan • Pakistan Cyber Security Engineer", 
                 font=("Arial", 10), fg="#00cc00", bg="#001100").pack()

        # Main container
        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Left: Radar
        radar_frame = tk.Frame(main_frame, bg="#111111", relief="ridge", bd=5)
        radar_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(radar_frame, width=520, height=520, bg="#000800", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.draw_radar_base()

        # Right: Controls + Table
        right_frame = tk.Frame(main_frame, bg="#000000")
        right_frame.pack(side="right", fill="both", expand=True)

        # Controls
        ctrl_frame = tk.Frame(right_frame, bg="#001100")
        ctrl_frame.pack(fill="x", pady=8)

        tk.Button(ctrl_frame, text="▶ START RADAR SCAN", command=self.start_scan,
                  bg="#00ff00", fg="#000", font=("Press Start 2P", 11, "bold"), height=2).pack(side="left", padx=5, fill="x", expand=True)
        
        tk.Button(ctrl_frame, text="⏹ STOP SCAN", command=self.stop_scan,
                  bg="#ff4444", fg="#fff", font=("Press Start 2P", 11, "bold"), height=2).pack(side="left", padx=5, fill="x", expand=True)
        
        tk.Button(ctrl_frame, text="🗑 CLEAR", command=self.clear_data,
                  bg="#555555", fg="#fff", font=("Press Start 2P", 10), height=2).pack(side="left", padx=5)

        # Status
        self.status_var = tk.StringVar(value="READY - PRESS START TO ACTIVATE RADAR")
        status_label = tk.Label(right_frame, textvariable=self.status_var, fg="#00ff00", 
                               bg="#000000", font=("Press Start 2P", 11))
        status_label.pack(pady=8)

        # Table
        columns = ("SSID", "BSSID", "CH", "SIGNAL", "ENCRYPTION")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=18)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#111111", foreground="#00ff00", fieldbackground="#111111")
        style.configure("Treeview.Heading", background="#002200", foreground="#00ff00")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def draw_radar_base(self):
        c = self.canvas
        cx, cy = 260, 260
        r = 230

        c.delete("all")

        # Concentric circles
        for i in range(1, 5):
            radius = r * i / 4
            c.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, 
                         outline="#003300", width=2)

        # Cross lines
        c.create_line(cx - r, cy, cx + r, cy, fill="#00ff00", width=2)
        c.create_line(cx, cy - r, cx, cy + r, fill="#00ff00", width=2)

        # Center
        c.create_oval(cx-12, cy-12, cx+12, cy+12, fill="#00ff00", outline="#00ff00")

        # Labels
        c.create_text(cx, cy - r - 15, text="100%", fill="#00ff00", font=("Arial", 9))
        c.create_text(cx, cy - r//2 - 10, text="50%", fill="#00ff00", font=("Arial", 9))

    def plot_networks_on_radar(self):
        self.draw_radar_base()
        cx, cy = 260, 260
        max_r = 220

        for net in self.networks:
            # Angle based on BSSID hash
            try:
                hash_val = int(net['bssid'].replace(":", ""), 16)
                angle = (hash_val % 360) * math.pi / 180
            except:
                angle = random.uniform(0, 2 * math.pi)

            # Stronger signal = closer to center
            distance = max_r * (1 - (net['signal'] / 100))

            x = cx + math.cos(angle) * distance
            y = cy + math.sin(angle) * distance

            # Color by signal
            if net['signal'] >= 75:
                color = "#00ff00"
            elif net['signal'] >= 50:
                color = "#ffff00"
            else:
                color = "#ff8800"

            # Dot
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=color, outline="#ffffff", width=2)
            
            # SSID label
            self.canvas.create_text(x, y-18, text=net['ssid'][:10], fill="white", font=("Arial", 8))

    def scan_windows(self):
        try:
            result = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"], 
                                           shell=True, text=True, timeout=8)
            networks = []
            current = {}

            for line in result.splitlines():
                line = line.strip()
                if line.startswith("SSID"):
                    if current and 'ssid' in current:
                        networks.append(current)
                    current = {"ssid": line.split(":", 1)[1].strip()}
                elif line.startswith("BSSID"):
                    current["bssid"] = line.split(":", 1)[1].strip()
                elif line.startswith("Signal"):
                    sig = line.split(":", 1)[1].strip().replace("%", "")
                    current["signal"] = int(sig)
                elif line.startswith("Channel"):
                    current["channel"] = line.split(":", 1)[1].strip()
                elif line.startswith("Authentication"):
                    current["encryption"] = line.split(":", 1)[1].strip()

            if current and 'ssid' in current:
                networks.append(current)

            return networks
        except Exception as e:
            print("Windows scan error:", e)
            return []

    def scan_linux(self):
        try:
            result = subprocess.check_output(["nmcli", "-t", "-f", "SSID,BSSID,SIGNAL,CHAN,SECURITY", 
                                            "dev", "wifi", "list"], shell=True, text=True)
            networks = []
            for line in result.splitlines():
                if not line.strip():
                    continue
                parts = line.split(":")
                if len(parts) >= 5:
                    networks.append({
                        "ssid": parts[0] if parts[0] else "Hidden",
                        "bssid": parts[1],
                        "signal": int(parts[2]),
                        "channel": parts[3],
                        "encryption": parts[4] if parts[4] else "OPEN"
                    })
            return networks
        except Exception as e:
            print("Linux scan error:", e)
            return []

    def live_scan(self):
        while self.scanning:
            if self.os_name == "Windows":
                self.networks = self.scan_windows()
            else:
                self.networks = self.scan_linux()

            # Update GUI safely
            self.root.after(0, self.update_gui)
            time.sleep(4)  # Scan every 4 seconds

    def update_gui(self):
        # Update radar
        self.plot_networks_on_radar()

        # Update table
        for item in self.tree.get_children():
            self.tree.delete(item)

        for net in self.networks:
            signal_text = f"{net['signal']}%"
            self.tree.insert("", "end", values=(
                net.get('ssid', 'N/A'),
                net.get('bssid', 'N/A'),
                net.get('channel', 'N/A'),
                signal_text,
                net.get('encryption', 'N/A')
            ))

        self.status_var.set(f"SCANNING... {len(self.networks)} NETWORKS DETECTED")

    def start_scan(self):
        if self.scanning:
            return
        self.scanning = True
        self.status_var.set("🔴 LIVE SCANNING... (Admin/Sudo Required)")
        threading.Thread(target=self.live_scan, daemon=True).start()

    def stop_scan(self):
        self.scanning = False
        self.status_var.set("🟢 SCAN PAUSED - READY")

    def clear_data(self):
        self.stop_scan()
        self.networks = []
        self.draw_radar_base()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("CLEARED - PRESS START TO SCAN")

    def on_close(self):
        self.scanning = False
        self.root.destroy()


if __name__ == "__main__":
    print("🔥 WiFi Radar Scanner Starting...")
    print("   Coded by Mr. Sabaz Ali Khan - Pakistan Cyber Security Engineer")
    print("   Run as Administrator (Windows) or with sudo (Linux)")

    try:
        app = WiFiRadarScanner()
    except Exception as e:
        print("Error:", e)
        input("Press Enter to exit...")