# Moonlight Setup Guide for Raspberry Pi

This guide will help you set up Moonlight on your Raspberry Pi to stream games from your NVIDIA PC.

## Prerequisites

### On your NVIDIA PC:

1. **Supported Hardware**:
   - NVIDIA GeForce GTX/RTX 600+ series GPU, or NVIDIA Quadro GPU (Kepler series or later)
   - Windows 10 or 11 (Windows 7 and 8 may be supported but not recommended)

2. **Required Software**:
   - NVIDIA GeForce Experience (GFE) 2.1.1 or higher, or NVIDIA Quadro Experience
   - OR Sunshine (an open-source alternative to NVIDIA GameStream)

3. **Display Requirements**:
   - 720p or higher display (or headless display dongle) connected to the NVIDIA GPU

4. **Network Requirements**:
   - Wired Ethernet connection recommended
   - 5 Mbps or higher upload speed (for streaming outside your home network)

### On your Raspberry Pi:

1. **Hardware**:
   - Raspberry Pi 4 or newer recommended for best performance
   - Wired Ethernet connection recommended

2. **Software**:
   - Raspberry Pi OS (Bullseye or newer)
   - Moonlight-Qt installed

## Setup Instructions

### Step 1: Set up your NVIDIA PC

#### If using NVIDIA GeForce Experience:

1. Install the [GeForce Experience software](https://www.nvidia.com/en-us/geforce/geforce-experience/) from NVIDIA.
2. Open GeForce Experience and log in with your NVIDIA account.
3. Click on the **Settings (gear) icon** in the top-right corner.
4. Select the **SHIELD** tab from the left sidebar.
5. Make sure the GameStream switch is in the **ON position** (should be green).
6. If you're using Windows 11, you need to disable Hardware-accelerated GPU Scheduling:
   - Open "Graphics Settings" from the Start Menu
   - Click "Change default graphics settings"
   - Set "Hardware-accelerated GPU scheduling" to Off

#### If using Sunshine (alternative):

1. Download and install Sunshine from [their GitHub page](https://github.com/LizardByte/Sunshine/releases).
2. Follow the setup instructions to configure Sunshine.
3. Make sure to set up a username and password for the web interface.
4. Add your games and applications through the Sunshine web interface.

### Step 2: Set up Moonlight on your Raspberry Pi

1. Install Moonlight-Qt if you haven't already:
   ```bash
   sudo apt update
   sudo apt install moonlight-qt
   ```

2. Run our setup script to guide you through the pairing process:
   ```bash
   python3 scripts/moonlight_setup.py
   ```

3. Follow the on-screen instructions to:
   - Enter your NVIDIA PC's IP address
   - Verify connectivity
   - Complete the pairing process
   - Test streaming

### Step 3: Pairing Process

The pairing process establishes a secure connection between your Raspberry Pi and your NVIDIA PC:

1. When you run the pairing command, a PIN code will be displayed on your Raspberry Pi.
2. A dialog will appear on your NVIDIA PC asking you to enter this PIN.
3. Enter the PIN on your PC to complete the pairing.
4. If successful, your Raspberry Pi will now be authorized to stream from your PC.

### Step 4: Streaming

Once paired, you can start streaming:

1. Launch Moonlight from the desktop or menu.
2. Select your PC from the list of available hosts.
3. Choose a game or application to stream.
4. Use a gamepad, keyboard, or mouse to control the stream.

## Troubleshooting

### Common Issues:

1. **PC not found**:
   - Make sure both devices are on the same network
   - Check that GameStream is enabled in GeForce Experience
   - Verify that your firewall isn't blocking the connection

2. **Pairing fails**:
   - Make sure you're entering the correct PIN
   - Check that the pairing dialog is visible on your PC
   - Restart GeForce Experience and try again

3. **Poor streaming quality**:
   - Use a wired connection if possible
   - Lower the streaming resolution and bitrate
   - Close other bandwidth-intensive applications

4. **Input lag**:
   - Use a wired connection for both devices
   - Try the "Optimize game settings" option in GeForce Experience
   - Reduce the streaming resolution

## Advanced Configuration

### Streaming Over the Internet

To stream over the internet, you'll need to:

1. Set up port forwarding on your router for the following ports:
   - TCP: 47984, 47989, 48010
   - UDP: 47998, 47999, 48000, 48002, 48010

2. Use a dynamic DNS service if your home IP address changes.

3. Connect to your public IP address or dynamic DNS hostname from Moonlight.

### Adding Custom Applications

If your game or application isn't automatically detected:

1. In GeForce Experience:
   - Click Settings > SHIELD
   - Click "Add" under the Games section
   - Browse to the application's .exe file
   - Give it a name and click OK

2. In Sunshine:
   - Open the web interface
   - Go to the Applications tab
   - Click "Add Application"
   - Fill in the details and save

### Streaming Your Desktop

To stream your entire desktop:

1. In GeForce Experience, add `C:\Windows\System32\mstsc.exe` as a custom application.
2. Name it "Desktop" or similar.
3. Select this application in Moonlight to stream your entire desktop.

## Command Line Reference

Moonlight-Qt supports several command-line options:

```
moonlight-qt                  # Launch the Moonlight GUI
moonlight-qt stream HOST APP  # Stream a specific app
moonlight-qt quit HOST        # Quit the current streaming session
moonlight-qt list HOST        # List available apps
moonlight-qt pair HOST        # Pair with a host
```

## Additional Resources

- [Moonlight GitHub Repository](https://github.com/moonlight-stream/moonlight-qt)
- [Sunshine GitHub Repository](https://github.com/LizardByte/Sunshine)
- [NVIDIA GameStream Documentation](https://www.nvidia.com/en-us/shield/support/shield-tv/gamestream/)
- [Moonlight Discord Server](https://moonlight-stream.org/discord)

## Feedback and Support

If you encounter any issues with this setup script or guide, please:
1. Check the troubleshooting section above
2. Visit the Moonlight Discord server for community support
3. File an issue on our GitHub repository
