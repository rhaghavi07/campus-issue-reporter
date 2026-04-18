# Smart Campus Issue Reporter & Data Dashboard

This project is a role-based web application where students can report campus issues and administrators can manage and analyze them using data dashboards.

## Features

### 1. Authentication System

Student Login:
- Register using email and OTP verification
- Create password after verification
- Login using email and password
- Can:
  - Report issues
  - View their complaints
  - Check status
  - Delete their own issues

Admin (Staff):
- Secure login
- Can:
  - View all issues
  - Update status (Pending, In Progress, Resolved)
  - Access dashboard

---

### 2. Report an Issue

Students can:
- Select issue type:
  - Electricity
  - Water
  - Cleanliness
  - WiFi
  - Others (custom input)
- Enter location (block/classroom)
- Add description

All data is stored using SQLite database.

---

### 3. View Issues

- Displays all reported issues
- Ordered by:
  - Pending → In Progress → Resolved
- Only the issue owner can delete their issue
- Staff can update status

---

### 4. Data Dashboard

Visualizations:
- Pie Chart → Most common issues
- Bar Graph → Issues per location
- Line Graph → Issues over time

Even when no data is present:
- Dashboard shows 0 values
- Graphs are still displayed

---

### 5. Smart Insights

The system automatically identifies:
- Most reported issue
- Most affected location

---

## Technologies Used

- Python (Flask)
- SQLite
- Pandas
- NumPy
- Matplotlib
- Seaborn
- HTML
- CSS

---