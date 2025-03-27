# 💬 Telegram Currency Converter Bot

A Telegram bot for tracking and converting exchange rates for USD to RUB and THB.  
The bot uses real-time data from TinkoffInvest and Bangkok Bank APIs.

---

## 🛠 Features

- Get real-time USD exchange rates from multiple banking APIs
- Supports both RUB and THB currencies
- Provides detailed rate information including bank names and timestamps
- Telegram command interface
- Built with modular Python architecture

---

## 📥 Available Commands

### `/info`
Returns the current exchange rates from:
- **TinkoffInvest API** (USD to RUB)
- **Bangkok Bank API** (USD to THB)

Each response includes:
- Bank name
- Rate
- Timestamp
- Timezone information

_Example:_
Tinkoff Invest: USD/RUB = 92.34 As of: 2024-03-24 12:30:00 MSK

Bangkok Bank: USD/THB = 35.20 As of: 2024-03-24 17:30:00 ICT

---

### `/reset`
Force-resets internal rate data. Use this command if:
- The bot encounters an error fetching data
- You suspect rates are outdated
- You want to manually refresh both sources

After reset, the next `/info` command will re-fetch all data from the APIs.

---

## 🔧 Technologies Used

- Python 3.10+
- Telebot (PyTelegramBotAPI)
- Pandas
- TinkoffInvest API
- Bangkok Bank public data
- Heroku (for deployment)
- Git + GitHub Actions (for CI/CD)

---

## 🔒 Configuration

Environment variables are used to securely store:
- Telegram bot token
- API keys (if applicable)

A sample `.env.example` file is provided in the repository.

---

## ✅ Improvements Planned

- Add currency conversion for additional pairs
- Add logging to file/database
- Add retry logic for API failures
- Add unit tests and coverage reports

---

## 📍 Notes

- This bot was built as a practical solution for real-world currency tracking
- The architecture is modular and can be extended to support more banks/APIs
- Codebase is beginner-friendly and well-commented

---

## 👤 Author

Dmitrii Zverev  
[GitHub](https://github.com/ZverevDmitriyZDV) • [LinkedIn](https://linkedin.com/in/zverevdmitriy)
