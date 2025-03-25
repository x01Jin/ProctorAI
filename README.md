# ProctorAI

An AI-powered proctoring system for monitoring and detecting potential academic misconduct.

## Initial Setup

When the application is first started, it will prompt you to configure required settings before proceeding:

1. **Roboflow API credentials**
   - API key for model access
   - Project identifier
   - Model version

2. **Model Class Definitions**
   - Default classes: "cheating" and "normal"
   - These define what the AI model detects

3. **Database Settings**
   - Connection parameters
   - XAMPP MySQL credentials

Note: The application cannot start without these settings being properly configured. A settings dialog will appear automatically to guide you through this setup process.

## How to Use

### Camera Controls

- Toggle camera on/off
- Real-time video feed display
- Camera status monitoring

### Detection System

- Start/Stop detection
- Filter detections by class
- Real-time detection overlays
- Detection count tracking in status bar

### Report Management

- View captured violation images
- Generate PDF reports of detected incidents
- Manage and review past detections

### Additional Features

- Status bar showing detection statistics
- Toolbar for quick access to common functions
- Theme customization options
- Real-time monitoring and alerts
