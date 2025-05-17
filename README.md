<p align="center">
  <img src="docs/images/freedom_broker_logo.png" alt="Freedom Broker Logo" width="200"/>
</p>

# Freedom Broker RFM Segmentation 🚀

<p align="center">
  <img src="docs/images/airflow_logo.png" alt="Airflow Logo" width="80"/>
  <img src="docs/images/python_logo.png" alt="Python Logo" width="80"/>
  <img src="docs/images/docker_logo.png" alt="Docker Logo" width="80"/>
  <img src="docs/images/postgres_logo.png" alt="PostgreSQL Logo" width="80"/>
</p>

> **Hackathon project**: customer segmentation for increasing commission income at Freedom Broker  
> using RFM (Recency, Frequency, Monetary) + KMeans clustering + Airflow automation.

---

## 📖 Table of Contents

- [About](#about)  
- [Project Structure](#project-structure)  
- [Setup & Installation](#setup--installation)  
- [Usage](#usage)  
  - [Running Locally with Docker Compose](#running-locally-with-docker-compose)  
  - [Airflow DAGs](#airflow-dags)  
  - [ML Segmentation](#ml-segmentation)  
- [Data Layout](#data-layout)  
- [Contributing](#contributing)  
- [License](#license)  

---

## 🎯 About

Freedom Broker – онлайн-брокер с доступом к акциям, облигациям, валютам и фьючерсам.  
Этот проект автоматизирует RFM-сегментацию клиентов:

1. **Recency**: сколько дней назад была последняя активность  
2. **Frequency**: как часто клиент совершает операции  
3. **Monetary**: сколько клиент приносит комиссий  

Результат — 10 смысловых клиентских сегментов, готовых к персонализированным маркетинговым действиям.

---

## 📂 Project Structure

```

freedom-broker-rfm/
├── dags/
│   ├── dag\_freedom-broker-rfm.py
│   ├── dag\_freedom-broker-rfm-extended.py
│   ├── first\_dag.py
│   └── sql/
│       ├── create\_rfm\_table.sql
│       ├── calculate\_rfm\_scores.sql
│       ├── create\_segment\_demographics.sql
│       ├── create\_segment\_summary.sql
│       └── create\_solution\_table.sql
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── images/
├── ml/
│   ├── rfm\_segmenter.py
│   └── models/
│       └── kmeans\_model.pkl
├── scripts/
│   ├── data\_loader.py
│   └── rfm\_calculator.py
├── docker-compose.yaml
├── requirements.txt
└── README.md

````

---

## 🛠 Setup & Installation

1. **Clone repository**  
   ```bash
   git clone https://github.com/yourusername/freedom-broker-rfm.git
   cd freedom-broker-rfm
   ```

2. **Copy environment variables**

   ```bash
   cp .env.example .env
   ```

3. **Install Python dependencies**
   *(если не используете Docker)*

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

### Running Locally with Docker Compose

```bash
docker-compose up -d
```

* Airflow UI → [http://localhost:8080](http://localhost:8080)
* PostgreSQL доступен на порту 5432
* Adminer UI (опционально) → [http://localhost:8081](http://localhost:8081)

---

### Airflow DAGs

* **`dag_freedom-broker-rfm.py`** — основной pipeline:

  1. Загружает сырые данные
  2. Вычисляет RFM
  3. Сохраняет результаты

* **`dag_freedom-broker-rfm-extended.py`**:

  * Добавляет кластеризацию сегментов

---

### ML Segmentation

Выполняется в `ml/rfm_segmenter.py`:

```bash
python ml/rfm_segmenter.py \
  --input data/processed/rfm_data.csv \
  --output ml/models/kmeans_model.pkl \
  --n_clusters 10
```

---

## 📊 Data Layout

```
data/
├── raw/           # Исходные CSV-файлы
└── processed/     # Выходные таблицы RFM и сегменты
```

---

## 🤝 Contributing

1. Fork this repo
2. Create a branch: `git checkout -b feature/xyz`
3. Commit your changes
4. Push and open a Pull Request

---

## ⚖️ License

MIT License — not yet but we will🎓

---

<p align="center">
  <img src="docs/images/thank_you.png" alt="Thank You" width="200"/>
</p>
