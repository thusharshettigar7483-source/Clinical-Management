# Medicare Specialist Portal 🏥

A modern, clinical-grade Python desktop application for hospital and clinic management, built with **CustomTkinter** and **SQLite**. It upgrades and modernizes legacy Java Swing systems into an intuitive, responsive, and beautiful healthcare platform.

---

## ✨ Features & Capabilities

### 🔐 1. Smart Authentication & Role-Based Access
- **Login & Registration**: Split-screen/card layout with live input normalization (spaces converted to underscores; regex constraint `^[a-z_]+$`).
- **Interactive Password Visibility**: Show/hide toggle (`👁` / `🔒`).
- **PBKDF2 Password Hashing**: Secure 100,000-iteration PBKDF2 SHA-256 key derivation with salt.
- **Role-Based Routing**:
  - `role == 'admin'` ➔ **Admin Command Center**
  - `role == 'patient'` ➔ **Patient Booking Dashboard**
- **⚡ Quick Demo Chips**: One-click autofill for testing Administrator (`admin` / `admin123`) and Patient accounts (`rahul_verma` / `patient123`).

---

### 🩺 2. Patient Booking Dashboard & Dynamic Branch Matrix
- **Validated Input Fields**:
  - **Full Name**: Strict letters & spaces validation (`^[a-zA-Z ]+$`).
  - **Contact Number**: Pre-filled prefix `+91 ` with strict 10-digit validation (`^\+91 \d{10}$`).
  - **Appointment Date**: Future-date validation (restricted to tomorrow or later).
  - **Interactive Calendar Picker**: Custom date picker modal preventing selection of past dates or today.
- **Dynamic Real-Time Branch Card**:
  - Updates automatically whenever either **Doctor** or **Time Slot** changes.
  - Resolves specialist credentials, clinic branch, address, room/suite number, and direct helpline.

#### 📍 Doctor & Clinic Schedule Matrix
| Specialist Doctor | 11 AM - 1 PM Slot | 3 PM - 5 PM Slot |
| :--- | :--- | :--- |
| **Dr. Sharma (Cardio)** | Surathkal Branch | Pumpwell Branch |
| **Dr. Gupta (Neuro)** | Bondel Branch | Kulur Branch |
| **Dr. Satwik Rai (Physio)** | Ladyhill Branch | PVS Branch |
| **Dr. Ashika Shetty (ENT)** | Kodialbail Branch | Sulthan Bathery Branch |
| **Dr. Nikhil Poojary (Ortho)** | Ullal Branch | Yekkur Branch |

---

### 📋 3. Patient Consultation History
- View all past and upcoming appointments booked under the patient's account.
- Search appointments by Doctor name, Location, or Date in real time.
- Status indicator pills (`Pending` 🟡, `Confirmed` 🟢, `Rejected` 🔴).
- Quick navigation back to the booking portal.

---

### 👑 4. Admin Command Center (Control Center)
- **Live KPI Metric Cards**:
  - Total Bookings
  - Pending Review
  - Confirmed Consultations
  - Rejected / Cancelled
  - Today's Scheduled Consultations
- **Real-Time Filtering & Search**:
  - Filter by status (`All`, `Pending`, `Confirmed`, `Rejected`).
  - Filter by specialist doctor.
  - Instant text search across Patient Name, Contact, Doctor, Clinic, or Reference ID.
- **Interactive Review Workflow**:
  - **`✓ Accept`**: Marks appointment as `Confirmed`. Active **only** when status is `Pending`.
  - **`✕ Reject`**: Triggers confirmation modal and marks as `Rejected`. Active **only** when status is `Pending`.
  - Real-time table refresh with non-intrusive toast notification.
- **📥 CSV Export**: Export complete appointment records to `.csv` for administrative reporting.

---

### 🎨 5. Modern UI/UX Standards
- **Theme Modes**: Seamless Dark Mode (`🌙`) and Light Mode (`☀️`) toggle.
- **Status Pills**: Color-coded badges with dedicated background and text contrast.
- **Smooth Toast Notifications**: In-window auto-dismissing feedback banners (`Success`, `Error`, `Warning`, `Info`).
- **Confirmation Modals**: Centered, non-blocking modal dialogues.
- **High-DPI Support**: Crisp fonts and elements on Windows high-resolution monitors.

---

## 🛠️ Architecture & Directory Structure

```
Thushar_Hospital/
│
├── app/
│   ├── __init__.py
│   ├── config.py                 # Colors, doctor matrix, constants, themes
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py         # SQLite connection & CRUD operations
│   │   └── seed_data.py          # Auto-seed script for default admin & samples
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Password hashing & authentication logic
│   │   ├── appointment_service.py# Booking validation & schedule logic
│   │   └── validation_service.py # Strict regex & date validation rules
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py        # Window controller & screen routing
│       ├── components/
│       │   ├── __init__.py
│       │   ├── toast.py          # Floating Toast notifications
│       │   ├── modal.py          # Confirmation & alert modal dialogs
│       │   ├── status_badge.py   # Status pill badge component
│       │   ├── stat_card.py      # Metric KPI cards
│       │   ├── date_picker.py    # Modern calendar popup dialog
│       │   └── header_bar.py     # Top navigation & user profile bar
│       └── views/
│           ├── __init__.py
│           ├── auth_view.py      # Login & Registration screens
│           ├── patient_view.py   # Booking Dashboard & Dynamic Branch card
│           ├── history_view.py   # Patient Appointment History
│           └── admin_view.py     # Admin Control Center & review workflow
│
├── main.py                       # Application entry point
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.13)

### 2. Install Dependencies
Open PowerShell or Command Prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python main.py
```

---

## 🔑 Default Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` |
| **Patient (Sample 1)** | `rahul_verma` | `patient123` |
| **Patient (Sample 2)** | `priya_shetty` | `patient123` |
| **Patient (Sample 3)** | `vikram_nayak` | `patient123` |

*(You can also click the quick-login chips on the login screen, or click **"Create Patient Account"** to register a new user).*

---

## 🧪 Database
On first launch, an SQLite database `medicare_hospital.db` is created automatically in the project root with the required schemas (`users` and `appointments`) and pre-seeded with the administrator account and initial consultation records.
