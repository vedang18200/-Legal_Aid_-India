# Legal Aid India

**Legal Aid India** is a Streamlit-powered web application that streamlines legal service delivery, allowing lawyers to manage profiles, consultations, cases, and client interactions efficiently.

---

## 🚀 Features

- **Lawyer Profile Management** – Create, view, and update detailed lawyer profiles, including name, email, specialization, experience, languages, and bio.
- **Consultation Scheduling** – Schedule new consultations, mark appointments as completed or cancelled, and view upcoming or past consultations.
- **Dashboard Overview** – Lawyer dashboard features real-time statistics like active cases, pending consultations, total clients, and available cases.
- **Case Management** – Display recent case updates with status and timestamps to track ongoing legal matters.
- **Modular Architecture** – Separation of concerns with dedicated directories for pages, services, assets, configs, and database interactions.

---

## 📂 Repository Structure

```
Legal_Aid_-India/
├── assets/          # Static assets (e.g., images, CSS)
├── components/      # Reusable UI components (Streamlit)
├── config/          # Configuration files and app settings
├── database/        # Database connections & data queries
├── pages/           # Streamlit app pages (multi-page app)
├── services/        # Business logic: case, consultation, lawyer services
├── test/            # Tests & test fixtures
├── utils/           # Helper utilities
├── router.py        # Page routing logic for Streamlit
├── main.py          # Streamlit entry point
├── requirements.txt # Python dependencies
└── test_acc_info.txt# (Potentially test account credentials/info)
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.9+
- `pip` package manager

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vedang18200/-Legal_Aid_-India.git
   cd -Legal_Aid_-India
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables or edit `config/` for database credentials.

4. Launch the app:
   ```bash
   streamlit run main.py
   ```

5. Navigate through:
   - **Lawyer Dashboard**
   - **Appointments & Consultations**
   - **Profile Management**

---

## 🛠 Project Modules

| Directory       | Description |
|----------------|-------------|
| `pages/`       | Contains page modules like `appointments.py`, `lawyer_profile.py`, enabling multi-page UI. |
| `services/`    | Encapsulates API-like functions such as `get_case_statistics`, `get_lawyer_consultations`, etc. |
| `database/`    | Database manager for handling queries (e.g., `execute_query`). |
| `config/`      | Houses style settings, constants (`LEGAL_CATEGORIES`, `MAJOR_CITIES`, etc.), and configuration files. |
| `components/`  | UI components to reuse across pages (if any). |
| `utils/`       | Utility helpers (e.g., common formatters, validators). |
| `router.py`    | Handles routing logic for the Streamlit multi-page setup. |
| `main.py`      | Application entry point bootstrapping the Streamlit app. |

---

## 🤝 Contributing

1. Fork this repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Make your changes & commit with meaningful messages.
4. Push to your branch and open a Pull Request.

---

## 🧪 Testing

Run tests using:
```bash
pytest --maxfail=1 --disable-warnings -q
```

---

## 📜 License

(Add your chosen license here, e.g., MIT, Apache 2.0)

---

## 📩 Contact

For questions or issues, please open an issue on the repository.

---

✨ Thank you for using **Legal Aid India**!
