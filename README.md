# 🎓 Dumroo.ai Query Assistant

An AI-powered data query assistant for Dumroo.ai's admin panel. Ask natural language questions about student data and get instant answers with role-based access control.

## 🌟 Features

- **Natural Language Queries**: Ask questions in plain English (e.g., "Show students who haven't submitted homework yet")
- **Role-Based Access Control (RBAC)**: Admins only see data from their assigned class and region
- **LangChain Integration**: Powered by LangChain's Pandas DataFrame Agent
- **Interactive UI**: Clean, user-friendly Streamlit interface
- **Query History**: Track your previous queries and results
- **Data Summary**: Quick overview of key metrics (homework submission, quiz scores, etc.)

## 📋 Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd dumroo-ai-query-assistant
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## 🎮 Usage

### Run the application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Configure your admin role

1. In the sidebar, enter your username (default: `Roshni_Admin`)
2. Select your assigned class (8 or 9)
3. Select your region (North or South)

### Ask questions

Use the query input to ask natural language questions:

**Example Queries:**
- "Show students who haven't submitted homework yet"
- "List all students with quiz scores above 85"
- "What is the average quiz score?"
- "Show me the top 3 students by quiz score"
- "How many students submitted homework?"
- "List students sorted by date"
- "Show students with quiz scores below 75"

## 📁 Project Structure

```
dumroo-ai-query-assistant/
├── app.py                    # Main Streamlit application
├── query_agent.py            # LangChain query agent
├── utils.py                  # RBAC and data utilities
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
└── data/
    └── students_data.csv     # Sample student dataset
```

## 🔧 Configuration

### Dataset Structure

The `students_data.csv` file should have the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| student_name | Student's name | Aarav |
| class | Grade/Class number | 8 |
| region | Geographic region | North |
| homework_submitted | Yes/No | Yes |
| quiz_score | Score (0-100) | 89 |
| date | Date in YYYY-MM-DD | 2025-11-04 |

### Role-Based Access

Admins are restricted to data based on:
- **assigned_class**: Only see students from their class
- **region**: Only see students from their region

Example admin role:
```python
{
    "username": "Roshni_Admin",
    "assigned_class": 8,
    "region": "North"
}
```

This admin would only see students from Class 8 in the North region.

## 🛠️ Tech Stack

- **Python 3.10+**: Core language
- **Streamlit**: Web UI framework
- **LangChain**: LLM orchestration
- **LangChain Experimental**: Pandas DataFrame Agent
- **OpenAI GPT-3.5/4**: Natural language processing
- **Pandas**: Data manipulation
- **python-dotenv**: Environment variable management

## 📊 Features Deep Dive

### Natural Language Processing

The application uses LangChain's Pandas DataFrame Agent which:
- Converts natural language to Python/Pandas code
- Executes queries on the filtered DataFrame
- Returns human-readable results
- Handles complex aggregations and filtering

### Security & Access Control

- Data is filtered **before** being passed to the AI agent
- Admins cannot access data outside their permissions
- API keys are stored securely in environment variables
- No data is sent to external services except OpenAI API

### Query History

- Last 5 queries are displayed in the UI
- Full history maintained in session state
- Can be cleared with "Clear History" button

## 🐛 Troubleshooting

### OpenAI API Key Error

```
⚠️ OpenAI API key not found
```

**Solution**: Make sure you've created a `.env` file with your API key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Import Error for LangChain

```
ModuleNotFoundError: No module named 'langchain'
```

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Data File Not Found

```
FileNotFoundError: Data file not found: data/students_data.csv
```

**Solution**: Make sure you're running the app from the project root directory.

## 🚧 Future Enhancements

- [ ] Add support for more data sources (JSON, SQL databases)
- [ ] Implement super-admin role with full data access
- [ ] Add data visualization (charts, graphs)
- [ ] Export query results to CSV/Excel
- [ ] Add authentication system
- [ ] Support for multiple datasets
- [ ] Query result caching
- [ ] Advanced filtering options

## 📝 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Powered by LangChain & OpenAI | Dumroo.ai © 2025**
