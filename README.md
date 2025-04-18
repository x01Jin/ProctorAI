# ProctorAI

An AI-powered proctoring system assistant for proctors in monitoring and detecting potential academic misconduct. This is a thesis grad project for the Computer Science group "CROISSANTS"

## Initial Setup

When the application is first started, it will prompt you to configure required settings before proceeding:

1. **Roboflow API credentials**
   - API key for model access
   - Project identifier
   - Model version

2. **Model Class Definitions**
   - Check your Roboflow model's classes and put them in settings separated by commas"," without spaces
   - These define what the AI model detects

3. **Database Settings**
   - This application relies on using XAMPP MySQL for the database so you should have it set up first
   - Connection parameters
   - XAMPP MySQL credentials and database name

Note: The application cannot start without these settings being properly configured. A settings dialog will appear automatically to guide you through this setup process.

## Features

### Initialization checking Feature

- When opening the application, a splash screen will appear with a log display
- The log display shows the checking of dependencies in order for the application to run properly
- when initializing the application for the first time the configuration file is generated which also opens the initial configuration settings
- the after successful checking the application will open properly

### Logging Feature

- A "logs" folder is generated on the application directory when the application is launched for the first time
- The folder contains the logs for camera, database, detection, report, and roboflow logs
- While the protorai.log contains all logs that happened in "order" for further information

### Camera Features

- Toggle camera on/off toggle
- Real-time video feed display

### Detection System Features

- Start/Stop detection toggle
- Real-time detection overlays
- Filter Bounding boxes seen in camera preview
- You can select on what class/label you want for the application to capture (e.g. cheating)
- Adjustable Confidence Threshold for the consideration of the examination environment
- Detection count tracking in status bar

### Report Management Feature

- View captured images, by right clicking the images a context menu will popup on wether you want to delete the image because the content is not relevant or a mistake(it is AI after all) OR tag the image of it's proper context (e.g. name)
- Generate PDF reports of proctor verified captured images

### Additional Features

- Toolbar for quick access to common functions like toggling of docks visibility and settings
- Theme customization options in settings (for now just dark and light themes)
