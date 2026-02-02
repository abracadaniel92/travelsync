# Reflash Raspberry Pi OS Bookworm - Step by Step Guide

## Prerequisites
- SD card (8GB minimum, 16GB+ recommended)
- SD card reader
- Windows computer
- Raspberry Pi Imager (download link below)

## Step 1: Download Raspberry Pi Imager

1. **Download Raspberry Pi Imager:**
   - Go to: https://www.raspberrypi.com/software/
   - Download "Raspberry Pi Imager for Windows"
   - Install it (run the downloaded .exe file)

## Step 2: Prepare SD Card

1. **Insert SD card** into your computer's SD card reader
2. **Backup any important data** from the SD card (if needed)
3. **Note:** This will erase everything on the SD card!

## Step 3: Flash Raspberry Pi OS Bookworm

1. **Open Raspberry Pi Imager**

2. **Click "Choose OS"**
   - Select: **"Raspberry Pi OS (other)"**
   - Then select: **"Raspberry Pi OS (64-bit)"** or **"Raspberry Pi OS (Legacy)"**
   - For Bookworm specifically, choose the latest version (Bookworm is the default now)

3. **Click "Choose Storage"**
   - Select your SD card
   - ⚠️ **Double-check** you selected the correct drive!

4. **Click the gear icon** (⚙️) to configure settings:
   
   **General Settings:**
   - ✅ **Enable SSH** (check this box)
   - **Set username:** `pi` (or your preferred username)
   - **Set password:** (choose a secure password)
   - **Configure wireless LAN:** (optional, if you want WiFi)
     - SSID: Your WiFi network name
     - Password: Your WiFi password
     - Country: Your country code (e.g., US, GB, etc.)
   
   **Services:**
   - ✅ **Enable SSH** (should already be checked)
   - ✅ **Enable public key authentication only** (optional, more secure)
   
   **Advanced Options:**
   - **Set locale settings:** (optional)
   - **Set timezone:** (optional)

5. **Click "Save"** to save settings

6. **Click "Write"**
   - Confirm you want to erase the SD card
   - Wait for the process to complete (5-15 minutes depending on SD card speed)

7. **Click "Continue"** when done

## Step 4: Eject and Insert SD Card

1. **Safely eject** the SD card from your computer
2. **Insert SD card** into your Raspberry Pi
3. **Remove any USB SSD** (if attached) for now
4. **Power on** your Raspberry Pi

## Step 5: First Boot Setup

### Option A: Headless (No Monitor) - SSH Access

1. **Find your Pi's IP address:**
   ```powershell
   # On Windows PowerShell, scan your network:
   # Or check your router's admin page for connected devices
   ```

2. **SSH into your Pi:**
   ```powershell
   ssh pi@your-pi-ip-address
   # Password: (the one you set in Imager)
   ```

3. **Run initial setup:**
   ```bash
   # Update system
   sudo apt update
   sudo apt upgrade -y
   
   # Expand filesystem (if needed)
   sudo raspi-config
   # Navigate to: Advanced Options > Expand Filesystem
   ```

### Option B: With Monitor/Keyboard

1. **Connect monitor, keyboard, and mouse**
2. **Boot the Pi** - it will show the desktop or setup wizard
3. **Follow on-screen instructions** to complete setup

## Step 6: Post-Installation Setup

After first boot, run these commands:

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget vim

# Set up SSH (if not already enabled)
sudo systemctl enable ssh
sudo systemctl start ssh

# Check IP address
hostname -I

# Optional: Install Docker (for your DocumentsToCalendar app)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi

# Log out and back in for Docker group to take effect
exit
# SSH back in
```

## Step 7: Restore Your Application

If you want to restore your DocumentsToCalendar app:

```bash
# Clone repository
cd ~
git clone https://github.com/abracadaniel92/DocumentsToCalendar.git
cd DocumentsToCalendar

# Run deployment script
chmod +x deploy_pi.sh
./deploy_pi.sh

# Or follow the manual setup in RASPBERRY_PI_DEPLOYMENT.md
```

## Quick Reference: Raspberry Pi Imager Settings

**Recommended Settings for Headless Setup:**
```
✅ Enable SSH
Username: pi
Password: [your secure password]
✅ Configure wireless LAN (if using WiFi)
SSID: [your WiFi name]
Password: [your WiFi password]
Country: [your country]
```

## Troubleshooting

### Pi won't boot
- Check SD card is properly inserted
- Verify you flashed the correct OS for your Pi model
- Try a different SD card
- Check power supply (use official Pi power supply)

### Can't SSH into Pi
- Verify SSH is enabled in Imager settings
- Check Pi and computer are on same network
- Find Pi's IP: Check router admin page or use network scanner
- Try: `ssh pi@raspberrypi.local` (if mDNS works)

### WiFi not connecting
- Double-check SSID and password in Imager settings
- Verify country code is correct
- Check WiFi is 2.4GHz (Pi doesn't support 5GHz on older models)

### SD card not detected
- Try different SD card reader
- Format SD card as FAT32 first (in Windows Disk Management)
- Use a different SD card

## Next Steps

After successful boot:
1. ✅ Update system: `sudo apt update && sudo apt upgrade -y`
2. ✅ Install Docker (if needed for your apps)
3. ✅ Restore your applications
4. ✅ Set up auto-start services
5. ✅ Configure firewall: `sudo ufw enable`

## Windows PowerShell Commands

**Find Pi on network:**
```powershell
# Scan local network (replace 192.168.1 with your network)
1..254 | ForEach-Object { 
    $ip = "192.168.1.$_"
    if (Test-Connection -ComputerName $ip -Count 1 -Quiet) {
        Write-Host "$ip is up"
    }
}
```

**SSH from Windows:**
```powershell
# If SSH client not available, install OpenSSH:
# Settings > Apps > Optional Features > Add OpenSSH Client

ssh pi@192.168.1.XXX
```

**Copy files to Pi:**
```powershell
# Using SCP (if OpenSSH installed)
scp file.txt pi@192.168.1.XXX:/home/pi/
```

## Alternative: Manual Flash (Advanced)

If Raspberry Pi Imager doesn't work:

1. **Download Raspberry Pi OS image:**
   - https://www.raspberrypi.com/software/operating-systems/
   - Download "Raspberry Pi OS (64-bit)" - Bookworm

2. **Extract the .img file** (it's in a .zip)

3. **Flash using balenaEtcher or Win32DiskImager:**
   - balenaEtcher: https://etcher.balena.io/
   - Win32DiskImager: https://sourceforge.net/projects/win32diskimager/

4. **Enable SSH manually:**
   - After flashing, create empty file named `ssh` (no extension) in the boot partition
   - Create `wpa_supplicant.conf` for WiFi (if needed)

## Notes

- **Bookworm** is the current default Raspberry Pi OS version
- **64-bit** is recommended for Pi 4 and newer
- **Legacy** (32-bit) is for older Pi models
- Always use the official Raspberry Pi power supply for stable operation





