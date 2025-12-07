# 💜 Emotion Map

**Community-Powered Emotional Self-Awareness Tool**

A Django web application that helps users gain emotional self-awareness through fast mood logging, data-driven micro-interventions, and intelligent pattern recognition. Built to support **UN SDG 3: Good Health and Well-being**.

![Django](https://img.shields.io/badge/Django-5.0.7-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🌟 Key Features

### 1. **Fast Mood Logging**
- Log emotional states with intensity ratings (1-10)
- Add contextual tags (#Work, #Home, #Exercise)
- Optional notes for deeper reflection

### 2. **Community-Powered Intervention Library**
- Micro-interventions (e.g., "Take 3 deep breaths")
- Community success scoring based on user feedback
- Vote on effectiveness: Helped / No Change / Made it Worse

### 3. **Data-Driven Insights**
- **Emotional Heatmap**: Visualize mood intensity by time of day and day of week
- **Correlation Engine**: Discover patterns like "Anxiety peaks on Mondays with #WorkDeadline"
- **Trend Charts**: 7-day mood intensity tracking with Chart.js

### 4. **Interactive UI**
- Built with HTMX for seamless interactivity
- Tailwind CSS for modern, responsive design
- Real-time feedback without page reloads

---

## 🎯 SDG 3 Alignment

This project directly supports **SDG 3: Good Health and Well-being** by:

- ✅ Promoting mental health awareness through self-tracking
- ✅ Providing accessible, evidence-based interventions
- ✅ Empowering users with data-driven insights into emotional patterns
- ✅ Creating a community-driven approach to mental wellness

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 5.0.7 |
| Database | SQLite (dev) / PostgreSQL (production) |
| Frontend | HTMX 1.9.10 |
| Styling | Tailwind CSS |
| Charts | Chart.js 4.4.0 |
| Language | Python 3.11+ |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11 or higher
- Git
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/emotion-map.git
cd emotion-map
```

2. **Create a virtual environment**
```bash
# On Mac/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create the database**
```bash
python manage.py migrate
```

5. **Seed sample interventions**
```bash
python manage.py seed_interventions
```

6. **Create a superuser (admin account)**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Main app: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

---

## 📊 Project Structure

```
emotion-map/
├── core/                          # Main Django app
│   ├── models.py                  # Database models (Mood, Intervention, Feedback, Tag)
│   ├── views.py                   # View logic and data processing
│   ├── forms.py                   # Django forms for user input
│   ├── urls.py                    # URL routing
│   ├── admin.py                   # Admin panel configuration
│   ├── templates/                 # HTML templates
│   │   ├── base.html             # Base template with navigation
│   │   ├── home.html             # Landing page
│   │   ├── dashboard.html        # Main dashboard with charts
│   │   ├── log_mood.html         # Mood logging form
│   │   ├── intervention_suggestion.html
│   │   ├── heatmap.html          # Emotional heatmap
│   │   ├── correlations.html     # Pattern insights
│   │   ├── interventions_list.html
│   │   └── submit_intervention.html
│   └── management/
│       └── commands/
│           └── seed_interventions.py  # Data seeding command
├── emotion_map/                   # Django project settings
│   ├── settings.py               # Project configuration
│   ├── urls.py                   # Main URL routing
│   └── wsgi.py                   # WSGI configuration
├── static/                        # Static files (future CSS/JS)
├── requirements.txt              # Python dependencies
├── manage.py                     # Django management script
└── README.md                     # This file
```

---

## 📈 Key Algorithms

### Community Success Score

The intervention efficacy scoring uses this formula:

```python
score = (helped_votes - worse_votes) / total_votes
```

**Range**: -1.0 (worst) to +1.0 (best)

**Example**:
- 10 "Helped" votes
- 2 "No Change" votes
- 1 "Made it Worse" vote
- Score = (10 - 1) / 13 = **0.69**

### Heatmap Aggregation

Uses Django ORM to aggregate mood intensity by:
- Day of week (0=Monday, 6=Sunday)
- Hour of day (0-23)

```python
avg_intensity = Mood.objects.filter(
    timestamp__week_day=day_idx,
    timestamp__hour=hour
).aggregate(Avg('intensity'))
```

---

## 🎨 Usage Examples

### 1. Log a Mood
```
Emotion: Anxiety
Intensity: 7/10
Tags: work, deadline
Note: "Big presentation tomorrow"
```

### 2. Get Intervention
System suggests: **"Take 3 Deep Breaths"**
User provides feedback: **"Helped"**

### 3. View Insights
- Heatmap shows: Anxiety peaks Monday mornings
- Correlation: #work tag → avg intensity 8.2
- Top intervention: "Drink Water" (score: 0.85)

---

## 🔮 Future Enhancements

- [ ] User authentication and personal data privacy
- [ ] Machine learning mood prediction
- [ ] Mobile app (React Native)
- [ ] Export data to CSV/JSON
- [ ] Integration with wearables (heart rate, sleep data)
- [ ] Therapist dashboard for clinical use
- [ ] Multi-language support

---

## 🤝 Contributing

Contributions are welcome! This is an open-source mental health tool.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 Database Schema

### Core Models

**Mood**
- `emotion` (choices: joy, sadness, anxiety, anger, etc.)
- `intensity` (1-10)
- `note` (optional text)
- `tags` (ManyToMany with Tag)
- `timestamp`
- `suggested_intervention` (ForeignKey to Intervention)

**Intervention**
- `title`
- `description`
- `submitted_by`
- `is_active`
- `created_at`

**Feedback**
- `mood` (ForeignKey to Mood)
- `intervention` (ForeignKey to Intervention)
- `result` (choices: helped, no_change, worse)
- `created_at`

**Tag**
- `name` (unique)
- `created_at`

---

## 🐛 Troubleshooting

### Issue: "No module named 'core'"
**Solution**: Make sure you've created the `core` app:
```bash
python manage.py startapp core
```

### Issue: Static files not loading
**Solution**: Run `collectstatic` command:
```bash
python manage.py collectstatic
```

### Issue: Database errors
**Solution**: Reset database:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_interventions
```

---

## 📄 License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

## 👥 Author

**Your Name**  
Data Analyst | Mental Health Advocate  
[GitHub](https://github.com/yourusername) | [LinkedIn](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- Mental health professionals who provided intervention suggestions
- The Django and HTMX communities
- Chart.js for visualization capabilities
- UN SDG framework for inspiration

---

## 📧 Contact

For questions, feedback, or collaboration:
- Email: your.email@example.com
- GitHub Issues: [Create an issue](https://github.com/yourusername/emotion-map/issues)

---

**Built with 💜 to support mental health awareness and SDG 3: Good Health and Well-being**