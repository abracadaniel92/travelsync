# Raspberry Pi Boot Fix: SD Card to SSD Migration

## Problem
Your Pi won't boot after moving everything from SD card to SSD. This is usually because:
1. The bootloader is still configured to boot from SD card first
2. USB boot mode isn't enabled
3. The SD card is interfering with boot order

## Solution: Fix Boot Configuration (No Reflash Needed!)

### Option 1: Quick Fix - Remove SD Card and Enable USB Boot

**If you can still access your Pi (via SSH or with SD card temporarily):**

1. **SSH into your Pi** (or boot with SD card temporarily):
   ```bash
   ssh pi@your-pi-ip
   ```

2. **Enable USB boot mode:**
   ```bash
   # Check current boot order
   vcgencmd boot_order
   
   # Enable USB boot (Pi 4/400/CM4)
   echo program_usb_boot_mode=1 | sudo tee -a /boot/config.txt
   
   # For Pi 5, use:
   # echo boot_order=0xf41 | sudo tee -a /boot/config.txt
   
   # Reboot
   sudo reboot
   ```

3. **After reboot, remove the SD card** and the Pi should boot from SSD.

### Option 2: Manual Boot Configuration Fix

**If you can't access the Pi, you'll need to modify the boot files:**

1. **Mount your SSD on another computer** (or use the SD card temporarily)

2. **Edit `/boot/config.txt`** (on the SSD):
   ```bash
   # Add these lines to enable USB boot:
   program_usb_boot_mode=1
   
   # For Pi 5, also add:
   # boot_order=0xf41
   ```

3. **Edit `/boot/cmdline.txt`** (on the SSD):
   ```bash
   # Make sure root partition points to your SSD, not SD card
   # Should look like: root=PARTUUID=xxxx-xxxx (your SSD's PARTUUID)
   ```

4. **Find your SSD's PARTUUID:**
   ```bash
   # On Linux/Mac:
   sudo blkid
   
   # On Windows (PowerShell):
   Get-Disk | Get-Partition | Format-List
   ```

### Option 3: Update Bootloader (Pi 4/400)

**If USB boot still doesn't work, update the bootloader:**

1. **Boot with SD card temporarily** (or access via another method)

2. **Update bootloader:**
   ```bash
   sudo apt update
   sudo apt install -y rpi-eeprom
   sudo rpi-eeprom-update -a
   sudo reboot
   ```

3. **After reboot, remove SD card** and boot from SSD.

### Option 4: Complete Boot Configuration Reset

**If nothing else works, reset boot configuration:**

1. **Boot with SD card** (temporarily)

2. **Backup your data:**
   ```bash
   sudo rsync -avxHAX --progress / /mnt/ssd/
   ```

3. **Update `/boot/config.txt` on SSD:**
   ```bash
   sudo nano /mnt/ssd/boot/config.txt
   ```
   
   Add:
   ```
   program_usb_boot_mode=1
   ```

4. **Update `/boot/cmdline.txt` on SSD:**
   ```bash
   sudo nano /mnt/ssd/boot/cmdline.txt
   ```
   
   Update root partition to point to SSD (use `blkid` to find PARTUUID)

5. **Remove SD card and reboot**

## Troubleshooting Steps

### Check Boot Order
```bash
# Check current boot order
vcgencmd boot_order

# Expected output for USB boot:
# boot_order=0xf41 (Pi 5)
# or USB should be in the list (Pi 4)
```

### Verify SSD is Detected
```bash
# Check if SSD is recognized
lsblk
sudo fdisk -l

# Check USB devices
lsusb
```

### Check Boot Logs
```bash
# View boot messages
dmesg | grep -i usb
dmesg | grep -i boot

# Check system logs
journalctl -b | grep -i boot
```

### Verify Boot Files on SSD
```bash
# Mount SSD and check boot partition
sudo mount /dev/sda1 /mnt
ls -la /mnt/
cat /mnt/config.txt | grep -i boot
```

## Common Issues and Fixes

### Issue: Pi still tries to boot from SD card
**Fix:** Remove SD card completely, or disable SD card boot:
```bash
# In /boot/config.txt, add:
boot_order=0xf41  # Pi 5 (USB first)
# or ensure USB is before SD in boot order
```

### Issue: SSD not recognized
**Fix:** 
- Check USB cable/connection
- Try different USB port
- Verify SSD is formatted correctly (ext4 for root, FAT32 for boot)
- Check power supply (SSD needs more power than SD card)

### Issue: Boot loops or kernel panics
**Fix:**
- Verify `/boot/cmdline.txt` has correct root partition UUID
- Check `/etc/fstab` doesn't reference SD card partitions
- Ensure all files were copied correctly

### Issue: "No bootable device" error
**Fix:**
- Verify boot partition is FAT32
- Check that `/boot` contains: `config.txt`, `cmdline.txt`, kernel files
- Ensure bootloader is updated: `sudo rpi-eeprom-update -a`

## Verification

After fixing, verify boot from SSD:

```bash
# Check root filesystem
df -h | grep /dev/root

# Should show your SSD, not SD card

# Check boot device
lsblk

# Verify boot order
vcgencmd boot_order
```

## When to Reflash

**Only reflash if:**
- Bootloader is corrupted
- You can't access the Pi at all
- All troubleshooting steps failed
- You want a fresh start

**To reflash:**
1. Use Raspberry Pi Imager
2. Select your SSD as target
3. Choose your OS (Raspberry Pi OS)
4. Configure settings before writing
5. After first boot, restore your data

## Quick Reference Commands

```bash
# Enable USB boot (Pi 4)
echo program_usb_boot_mode=1 | sudo tee -a /boot/config.txt

# Check boot order
vcgencmd boot_order

# Update bootloader
sudo rpi-eeprom-update -a

# Find disk UUIDs
sudo blkid

# Check mounted filesystems
df -h

# View boot messages
dmesg | tail -50
```

## Need Help?

If none of these work:
1. Check your Pi model (Pi 4, Pi 5, etc.) - commands differ
2. Verify SSD compatibility
3. Check power supply (SSD needs stable power)
4. Try booting with SD card to verify Pi still works
5. Consider reflashing as last resort





