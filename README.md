# ProctorAI

## Group Name: Croissants

## Thesis Title: ProctorAI

### Overview
ProctorAI is an innovative application developed as part of a thesis project at Universidad de Dagupan (UDD). The app leverages AI technology to detect suspicious behavior during exams, providing real-time monitoring and reporting capabilities.

### Requirements
This project requires several Python packages to function correctly. A `requirements.txt` file is included in the project directory to facilitate the installation of these dependencies.

### Installation Instructions

1. **Clone the Repository**
    - if you have Git installed open ide terminal and do this:
    ```bash
    git clone https://github.com/x01Jin/ProctorAI
    cd ProctorAI
    ```
    - if you do not have git installed Just download the Code (go at the top of this page and find the green "Code" button click it and "Download ZIP")

2. **Set Up a Virtual Environment (Optional but Recommended)**
    Using venv:
    ```bash
    python -m venv .venv
    # On Windows use:
    venv\Scripts\activate
    ```
3. **Install Required Packages Use the following command to install all required packages listed in requirements.txt:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Database Setup**
    - install and setup "XAMPP"
    - open XAMPP Control Panel
    - start "Apache" and "MySQL"
    - click Admin of MySQL
    - find and click Import tab once in phpMyAdmin
    - click "Choose File" and use "proctorai.sql" which is included when cloning/downloaded the repository
    - click "Import" at the very bottom
    - after that the database is ready

### Usage Instructions

1. **Run the Application**

2. **Using the App**

  - Click on "Use Camera" to start the camera feed.
  - Adjust the confidence threshold using the slider.
  - Select the display mode (labels or confidence) from the dropdown menu.
  - Choose the label filter (cheating or not cheating) from the dropdown menu.
  - Click "Start Detection" to begin monitoring.
  - If cheating is detected, images will be saved in the tempcaptures folder.
  - Use "Generate PDF" to create a report of captured images.
  - Click "Clear Temp Images" to delete all temporary captures.
  
### License
This project is for educational purposes only and is not intended for commercial use.

