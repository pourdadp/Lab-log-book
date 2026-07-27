# 🧪 LabLogix: Enterprise Laboratory Equipment Logbook & Management System

**LabLogix** is a cutting-edge, lightweight, and robust web-based application designed to digitize and streamline laboratory operations. Say goodbye to messy paper logbooks and fragmented spreadsheets! LabLogix empowers modern laboratories with real-time tracking, intelligent default-parameter validation, comprehensive audit trails, and seamless local-network mobility—all presented in a clean, high-performance interface with full Shamsi (Jalali) calendar integration.

---

## 🚀 Key Features & Marketing Highlights

* **Intelligent Parameter Validation & Smart Warnings:** Define baseline operating parameters and default temperatures for each device. LabLogix automatically triggers real-time visual alerts whenever a recorded reading deviates from standard configurations, ensuring immediate quality control and error prevention.
* **Complete Asset & Lifecycle Management:** Effortlessly manage instrument inventories, including specific room/location tracking, designated responsible specialists, maintenance statuses, and calibration expiration alerts.
* **Native Shamsi Calendar Support:** Purpose-built for Persian-speaking environments, all timestamps, logs, and audit trails natively utilize the Jalali (Shamsi) calendar system for seamless compliance and local record-keeping.
* **Granular Role-Based Access Control (RBAC):** Secure your laboratory data with three distinct permission levels:
  * **System Administrator (Admin):** Full control over user accounts, device configurations, experts, and system logs.
  * **Reporting Specialist (Report):** Authorized to log operational entries, monitor device statuses, and generate filtered printable reports.
  * **Viewer:** Read-only access to inspect equipment health and historical logs.
* **Advanced Filtering & Print-Ready Reports:** Instantly filter log entries by specific equipment, warning statuses, or failure flags. Generate clean, professional print-ready outputs or download formatted reports with a single click.
* **Complete System Audit Trail:** Keep a secure, immutable history of all user activities—including logins, device edits, user management, and operational logs—ensuring total accountability.
* **Local Network Mobility:** Hosted locally on a single master machine, the application broadcasts across your local Wi-Fi or LAN network, enabling team members to access and update logs directly from their mobile phones, tablets, or remote lab stations without installing extra software.

---

## 📦 Prerequisites & Tech Stack

Built on modern, high-speed Python frameworks:
* **Python** 3.8+
* **Streamlit** (for high-performance reactive UI)
* **Pandas** (for data manipulation and filtering)
* **Jdatetime** (for precise Shamsi date and time handling)
* **SQLite** (lightweight, zero-configuration embedded database)

---

## 🛠️ Installation & Setup Guide

1. Clone or download the repository to your host machine.
2. Install the required Python dependencies by running the following command in your terminal:
   ```bash
   pip install streamlit pandas jdatetime
