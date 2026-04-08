# ================================================
# WiFi Network Visualizer - Radar UI
# Coded by Mr. Sabaz Ali Khan (Ethical Hacking Series)
# Python + Pygame - Real-time Radar Visualization
# ================================================

import pygame
import subprocess
import sys
import time
import math
import random
import platform

pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WiFi Radar Visualizer - Coded by Mr. Sabaz Ali Khan")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 18)
big_font = pygame.font.SysFont("consolas", 28)

# Colors (classic radar green)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 80, 0)
BG = (0, 10, 0)

networks = []
last_scan = 0
SCAN_INTERVAL = 3000  # 3 seconds

def scan_wifi():
    """Cross-platform WiFi scan"""
    global networks
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                stderr=subprocess.STDOUT
            ).decode("utf-8", errors="ignore")
            
            current = {}
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("SSID"):
                    if current and current.get("ssid"):
                        networks.append(current)
                    current = {"ssid": line.split(":", 1)[1].strip()}
                elif "Signal" in line:
                    try:
                        current["signal"] = int(line.split(":")[1].strip().replace("%", ""))
                    except:
                        current["signal"] = 50
                elif "Channel" in line:
                    current["channel"] = line.split(":")[1].strip()
                elif "BSSID" in line:
                    current["bssid"] = line.split(":")[1].strip()
            if current and current.get("ssid"):
                networks.append(current)
        
        elif platform.system() == "Linux":
            # Try nmcli (most user-friendly)
            try:
                output = subprocess.check_output(["nmcli", "-t", "-f", "SSID,SIGNAL,CHAN,BSSID", "dev", "wifi", "list"]).decode()
                for line in output.splitlines():
                    if line and not line.startswith("SSID"):
                        parts = line.split(":")
                        if len(parts) >= 3:
                            networks.append({
                                "ssid": parts[0] or "Hidden",
                                "signal": int(parts[1]) if parts[1].isdigit() else 50,
                                "channel": parts[2],
                                "bssid": parts[3] if len(parts)>3 else "??"
                            })
            except:
                print("Linux: Install nmcli for best results")
        
        # Remove duplicates
        seen = set()
        networks = [n for n in networks if n.get("ssid") and (n["ssid"] not in seen or seen.add(n["ssid"]))]
        
    except Exception as e:
        print("Scan error:", e)
        # Demo data if scan fails
        networks = [{"ssid": f"DemoNet{i}", "signal": random.randint(40,95), "channel": random.randint(1,13), "bssid": "00:00:00:00:00:00"} for i in range(8)]

def get_angle(bssid):
    """Consistent angle for same network"""
    return hash(bssid) % 360

def draw_radar():
    cx, cy = WIDTH//2, HEIGHT//2
    max_r = 320
    
    screen.fill(BG)
    
    # Concentric circles + signal rings
    for r in range(40, max_r+1, 55):
        pygame.draw.circle(screen, DARK_GREEN, (cx, cy), r, 2)
        percent = int((1 - r / max_r) * 100)
        text = font.render(f"{percent}%", True, GREEN)
        screen.blit(text, (cx + 15, cy - r + 5))
    
    # Crosshairs
    pygame.draw.line(screen, GREEN, (cx - max_r, cy), (cx + max_r, cy), 1)
    pygame.draw.line(screen, GREEN, (cx, cy - max_r), (cx, cy + max_r), 1)
    
    # Networks as blips
    for net in networks:
        if not net.get("signal"): continue
        angle = math.radians(get_angle(net.get("bssid", "unknown")))
        # Stronger signal = closer to center
        radius = max_r * (1 - net["signal"] / 100)
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        
        # Blip
        pygame.draw.circle(screen, GREEN, (int(x), int(y)), 10)
        pygame.draw.circle(screen, (255,255,255), (int(x), int(y)), 4)
        
        # Label
        label = font.render(f"{net['ssid']} {net['signal']}%", True, GREEN)
        screen.blit(label, (x + 18, y - 8))
    
    # Rotating sweep line
    sweep = (time.time() * 2) % (math.pi * 2)
    end_x = cx + math.cos(sweep) * (max_r + 30)
    end_y = cy + math.sin(sweep) * (max_r + 30)
    pygame.draw.line(screen, GREEN, (cx, cy), (end_x, end_y), 4)
    
    # Center
    pygame.draw.circle(screen, GREEN, (cx, cy), 18)
    pygame.draw.circle(screen, BG, (cx, cy), 9)
    
    # Title
    title = big_font.render("WiFi RADAR", True, GREEN)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
    
    # Legend
    legend = font.render("Stronger Signal = Closer to Center", True, (0, 200, 0))
    screen.blit(legend, (20, HEIGHT - 40))

# ====================== MAIN LOOP ======================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    current_time = pygame.time.get_ticks()
    if current_time - last_scan > SCAN_INTERVAL:
        networks.clear()
        scan_wifi()
        last_scan = current_time
    
    draw_radar()
    
    # Live count
    count_text = font.render(f"Networks: {len(networks)}", True, GREEN)
    screen.blit(count_text, (WIDTH - 180, 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()