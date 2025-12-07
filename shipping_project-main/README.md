# Kam's Ground Shipping 📦

A Flask-based web application for managing shipping operations with a cute pink & brown theme designed for dropshipping businesses.

## Features

- **Price Calculator** - Calculate shipping costs based on weight and speed
- **Package Tracking** - Track packages by tracking number
- **Delivery Rescheduling** - Reschedule delivery dates
- **Shipment Management** - View and manage all shipments
- **Customer Inquiries** - Handle customer questions and support
- **Employee Directory** - Manage employee information
- **Customer Database** - Track customer records

## Tech Stack

- **Backend**: Flask 3.1.2
- **Frontend**: HTML, CSS (custom pink & brown theme)
- **Font**: Google Fonts (Nunito)

## Installation

### Prerequisites

- Python 3.8+ installed
- Git installed

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd shipping_project
   ```

2. **Create a virtual environment**
   
   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
   .\venv\Scripts\Activate.ps1
   ```
   
   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the app**
   
   Open your browser and navigate to: `http://127.0.0.1:5000`

## Project Structure

```
shipping_project/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── static/
│   └── style.css                   # Pink & brown theme styles
└── templates/
    ├── index.html                  # Homepage
    ├── price.html                  # Price calculator
    ├── tracking.html               # Package tracking
    ├── reschedule.html             # Delivery rescheduling
    ├── shipments.html              # Shipment records
    ├── inquiries.html              # Customer inquiries
    └── employee_dashboard.html     # Employee directory
```

## Development

The app runs in debug mode by default, which means:
- Auto-reloads when you make changes to files
- Shows detailed error messages
- **Note**: Do not use debug mode in production!

## Deployment

For production deployment, consider:
- Using a WSGI server like Gunicorn or uWSGI
- Setting up a proper database (currently using in-memory data)
- Configuring environment variables for sensitive data
- Disabling Flask debug mode

## License

MIT License - feel free to use this project for your own shipping business!

## Author

Created with ❤️ by Kam
