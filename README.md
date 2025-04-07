# ContractIQ

ContractIQ is an automated notification system for managing digital contracts. The system extracts key contract details (such as effective dates and term durations), calculates termination dates, schedules email notifications, and sends timely alerts using an SMTP server. It leverages the Gemini API for data extraction and integrates with Firebase for database operations.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [API Usage](#api-usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Questions & Support](#questions--support)

---

## Features

- **Automated Data Extraction:**  
  Uses the Gemini API to extract structured contract details (effective dates, term durations, parties, etc.) from digital contract files.

- **Termination Date Calculation:**  
  Parses various date formats and computes termination dates based on contract term durations.

- **Notification Scheduling:**  
  Schedules email notifications (e.g., 1, 3, 5 days before termination) and flags contracts that have already terminated.

- **Email Alerts:**  
  Sends automated, tailored email notifications using Gmail’s SMTP server with App Password authentication.

- **Robust Logging & Error Handling:**  
  Provides comprehensive logging for monitoring and debugging.

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/nikhil-r0/contractiq-backend.git
   cd contractiq-backend
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY='your_secret_key'
GEMINI_API='your_gemini_api_key'
NOTIFICATION_EMAIL='your_notification_email@gmail.com'
NOTIFICATION_PASSWORD='your_app_password'
```

- **SECRET_KEY:** Used by Flask for session management.
- **GEMINI_API:** API key for accessing the Gemini model for contract extraction.
- **NOTIFICATION_EMAIL:** The email address from which notifications will be sent.
- **NOTIFICATION_PASSWORD:** A Google App Password used for SMTP authentication.  

  **How to Generate a Google App Password:**
  1. Enable 2-Step Verification in your Google account.
  2. Visit [Google App Passwords](https://myaccount.google.com/apppasswords).
  3. Select "Mail" as the app and your device, then click "Generate".
  4. Copy the generated password into your `.env` file.

---

## Running Locally

After configuring the environment, run the application with:

```bash
python app.py
```

The Flask development server will start, and the app will be available on your local machine.

---

## API Usage

### Notifications Endpoint

The notification scheduling and email alert feature is under development. To manually trigger notifications, send a GET request to the `/notifications123` endpoint.

#### Example Route in `app.py`:

```python
@app.route('/notifications123', methods=["GET"])
@cross_origin()  # Allow cross-origin requests
def notifications():
    try:
        process_all_users_contracts()
        obj = ContractNotificationManager()
        obj.send_scheduled_notifications()
        return jsonify({"message": "Notifications processed successfully", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"Error processing notifications: {str(e)}", "status": "error"}), 500
```

#### Sample cURL Command

```bash
curl -X GET "https://contractiq-backend.onrender.com/notifications123" -H "Content-Type: application/json"
```

---

## Project Structure

```
contractiq-backend/
├── app.py                           # Main application entry point
├── CUAD_v1.json                     
├── DIGITAL LICENSING AGREEMENT.pdf   # Sample contract file
├── firebase_credentials.json        # Firebase credentials (do not commit sensitive info)
├── instance/                        
│   └── users.db
├── old/                             # Archive of older scripts and versions
│   ├── app.py
│   ├── extract.py
│   └── process.py
├── README.md                        # This documentation file
├── requirements.txt                 # List of dependencies
├── routes/                          # Flask route modules
│   ├── auth_routes.py               # Authentication routes
│   ├── dashboard_routes.py          # Dashboard and notification routes
│   └── __pycache__
├── services/                        # Service modules
│   ├── extract_service.py           # Contract extraction via Gemini API
│   ├── firebase_service.py          # Firebase initialization and Firestore client
│   ├── gemini_service.py            # Gemini service integration
│   └── __pycache__
├── features/                        # Feature modules
│   ├── email_notification.py        # ContractNotificationManager and email functionality
│   └── send_email_to_users.py       # Additional email scripts, if any
├── static/                          # Static files (JS, CSS, images, etc.)
│   ├── background.mp4
│   ├── dashboard.js
│   ├── docx.png
│   ├── file.png
│   ├── LazyMonks-WB.png
│   ├── logout.png
│   ├── pdf.png
│   ├── style.css
│   ├── txt.png
│   └── upload.png
├── templates/                       # HTML templates
│   ├── base.html                    # Base template
│   ├── dashboard.html               # Dashboard page
│   ├── login.html                   # Login page
│   └── register.html                # Registration page
└── uploads/                         # Uploaded contract files
```
---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes with clear commit messages.
4. Push your branch to your fork and open a pull request.
5. Ensure tests pass and follow the code style guidelines.

---


## Questions & Support

If you have any questions or need support, please open an issue in this repository or contact [nikilrrvk@gmail.com](mailto:nikilrrvk@gmail.com).

---