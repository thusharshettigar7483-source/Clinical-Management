"""
Configuration constants, theme definitions, and clinic schedule matrices
for Medicare Specialist Portal.
"""

from typing import Dict, List, Tuple

APP_NAME = "Medicare Specialist Portal"
APP_VERSION = "2.0.0"
APP_SUBTITLE = "Specialist Healthcare & Clinic Management System"

# Default Window Dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 780
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 650

# Database File Path
DB_NAME = "medicare_hospital.db"

# Color Palette (Hex Codes)
COLORS = {
    # Brand Primary
    "primary": "#0F4C81",          # Deep Hospital Blue / Classic Teal
    "primary_hover": "#0D3E6B",
    "primary_light": "#E0F2FE",    # Soft blue container
    "primary_text": "#0F4C81",

    # Accent / Success CTA
    "accent": "#10B981",           # Emerald Health Green
    "accent_hover": "#059669",
    "accent_light": "#D1FAE5",

    # Danger / Rejection
    "danger": "#EF4444",           # Soft Crimson
    "danger_hover": "#DC2626",
    "danger_light": "#FEE2E2",

    # Warning / Pending
    "warning": "#F59E0B",          # Warm Amber
    "warning_hover": "#D97706",
    "warning_light": "#FEF3C7",

    # Info / Neutral
    "info": "#3B82F6",
    "info_light": "#DBEAFE",

    # Light Theme Surfaces
    "light": {
        "bg": "#F8FAFC",           # Clean slate background
        "card_bg": "#FFFFFF",      # Elevated card surface
        "card_alt": "#F1F5F9",     # Slightly muted card surface
        "border": "#E2E8F0",       # Clean light border
        "text_primary": "#0F172A", # Near black high-contrast text
        "text_secondary": "#64748B",# Muted subtitle text
        "input_bg": "#F8FAFC",
        "input_border": "#CBD5E1",
        "header_bg": "#FFFFFF",
        "table_row_even": "#FFFFFF",
        "table_row_odd": "#F8FAFC",
        "table_hover": "#F1F5F9",
    },

    # Dark Theme Surfaces
    "dark": {
        "bg": "#0B132B",           # Deep dark slate
        "card_bg": "#1C2541",      # Elevated dark container
        "card_alt": "#243256",
        "border": "#3A506B",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "input_bg": "#0E1838",
        "input_border": "#3A506B",
        "header_bg": "#1C2541",
        "table_row_even": "#1C2541",
        "table_row_odd": "#172038",
        "table_hover": "#253457",
    }
}

# Time Slots
TIME_SLOTS: List[str] = [
    "11 AM - 1 PM",
    "3 PM - 5 PM"
]

# Doctors & Schedule Matrix (Specialty and Branch Locations by Time Slot)
DOCTOR_SCHEDULE_MATRIX: Dict[str, Dict[str, any]] = {
    "Dr. Sharma (Cardio)": {
        "specialty": "Cardiology",
        "full_name": "Dr. Sharma",
        "experience": "14+ Years Exp. | MBBS, MD (Cardiology)",
        "slots": {
            "11 AM - 1 PM": {
                "branch": "Surathkal Branch",
                "address": "NH 66, Near NITK Main Gate, Surathkal, Mangalore - 575014",
                "room": "Cardiology Suite A-101",
                "phone": "+91 824 2474000"
            },
            "3 PM - 5 PM": {
                "branch": "Pumpwell Branch",
                "address": "Medicare Central Tower, Pumpwell Circle, Mangalore - 575002",
                "room": "Cardiac Care OPD, 2nd Floor",
                "phone": "+91 824 2435100"
            }
        }
    },
    "Dr. Gupta (Neuro)": {
        "specialty": "Neurology",
        "full_name": "Dr. Gupta",
        "experience": "12+ Years Exp. | MBBS, DM (Neurology)",
        "slots": {
            "11 AM - 1 PM": {
                "branch": "Bondel Branch",
                "address": "Airport Road, Opp. Kavoor Junction, Bondel, Mangalore - 575008",
                "room": "Neuro Sciences Wing, Room 204",
                "phone": "+91 824 2488200"
            },
            "3 PM - 5 PM": {
                "branch": "Kulur Branch",
                "address": "Kulur Ferry Road, Near Kulur Bridge, Mangalore - 575013",
                "room": "Neurology Consultation B-12",
                "phone": "+91 824 2456300"
            }
        }
    },
    "Dr. Satwik Rai (Physio)": {
        "specialty": "Physiotherapy & Rehab",
        "full_name": "Dr. Satwik Rai",
        "experience": "10+ Years Exp. | BPT, MPT (Musculoskeletal)",
        "slots": {
            "11 AM - 1 PM": {
                "branch": "Ladyhill Branch",
                "address": "Chilimbi Heights, Ladyhill Main Road, Mangalore - 575006",
                "room": "Rehabilitation & Physio Studio 1",
                "phone": "+91 824 2451900"
            },
            "3 PM - 5 PM": {
                "branch": "PVS Branch",
                "address": "Navabharath Circle, PVS Kalakunj Road, Kodialbail, Mangalore - 575003",
                "room": "Sports Medicine & Physio Room 302",
                "phone": "+91 824 2490500"
            }
        }
    },
    "Dr. Ashika Shetty (ENT)": {
        "specialty": "ENT & Head-Neck Surgery",
        "full_name": "Dr. Ashika Shetty",
        "experience": "9+ Years Exp. | MBBS, MS (ENT)",
        "slots": {
            "11 AM - 1 PM": {
                "branch": "Kodialbail Branch",
                "address": "Empire Mall Commercial Wing, MG Road, Kodialbail, Mangalore - 575003",
                "room": "ENT Diagnostics Center 105",
                "phone": "+91 824 2444700"
            },
            "3 PM - 5 PM": {
                "branch": "Sulthan Bathery Branch",
                "address": "Boloor Waterfront Road, Near Watch Tower, Sulthan Bathery, Mangalore - 575006",
                "room": "ENT Clinic Suite C-3",
                "phone": "+91 824 2452100"
            }
        }
    },
    "Dr. Nikhil Poojary (Ortho)": {
        "specialty": "Orthopedics & Joint Care",
        "full_name": "Dr. Nikhil Poojary",
        "experience": "15+ Years Exp. | MBBS, MS (Ortho), DNB",
        "slots": {
            "11 AM - 1 PM": {
                "branch": "Ullal Branch",
                "address": "Kotekar Cross Road, Main Highway, Ullal, Mangalore - 575020",
                "room": "Orthopedic Clinic & Cast Room O-10",
                "phone": "+91 824 2467800"
            },
            "3 PM - 5 PM": {
                "branch": "Yekkur Branch",
                "address": "Kankanady Bypass Road, Yekkur Junction, Mangalore - 575007",
                "room": "Joint Replacement Center Room 108",
                "phone": "+91 824 2439200"
            }
        }
    }
}

DOCTOR_LIST: List[str] = list(DOCTOR_SCHEDULE_MATRIX.keys())

# Status Types
STATUS_PENDING = "Pending"
STATUS_CONFIRMED = "Confirmed"
STATUS_REJECTED = "Rejected"

STATUS_COLORS = {
    STATUS_PENDING: {
        "bg": "#FEF3C7",
        "text": "#B45309",
        "border": "#FDE68A",
        "dark_bg": "#451A03",
        "dark_text": "#FCD34D",
        "dark_border": "#78350F"
    },
    STATUS_CONFIRMED: {
        "bg": "#D1FAE5",
        "text": "#047857",
        "border": "#A7F3D0",
        "dark_bg": "#064E3B",
        "dark_text": "#6EE7B7",
        "dark_border": "#065F46"
    },
    STATUS_REJECTED: {
        "bg": "#FEE2E2",
        "text": "#B91C1C",
        "border": "#FECACA",
        "dark_bg": "#7F1D1D",
        "dark_text": "#FCA5A5",
        "dark_border": "#991B1B"
    }
}
