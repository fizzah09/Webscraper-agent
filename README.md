# CrewAI Multi-Agent System with OpenRouter

This project implements a multi-agent system using CrewAI framework with OpenRouter LLM integration for blog analysis and reporting.

## 🎯 Project Overview

A sequential multi-agent workflow that:
1. **Crawls** blogs based on keywords
2. **Cleans** and preprocesses text data
3. **Analyzes** topics, themes, and motives
4. **Evaluates** sentiment polarity
5. **Generates** visual reports and insights

## 🔑 OpenRouter + CrewAI Integration

### Why OpenRouter?

OpenRouter provides access to multiple LLM providers through a single API:
- ✅ Access to GPT-4, Claude, Llama, Gemini, and more
- ✅ Pay-as-you-go pricing
- ✅ No separate API keys for each provider
- ✅ Easy switching between models
- ✅ Built-in rate limiting and fallbacks

### Quick Start

1. **Get OpenRouter API Key**
   ```
   Visit: https://openrouter.ai/
   Sign up and create an API key
   ```

2. **Configure Environment**
   ```powershell
   # Copy the example env file
   Copy-Item .env.example .env
   
   # Edit .env and add your key
   notepad .env
   ```

3. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run Setup Script** (Optional)
   ```powershell
   .\setup.ps1
   ```

## 📦 Installation

### Requirements
- Python 3.8+
- pip package manager
- OpenRouter API key

### Install All Dependencies
```powershell
pip install -r requirements.txt
```

### Required Packages
- `crewai` - Multi-agent orchestration
- `langchain-openai` - LLM integration
- `python-dotenv` - Environment variables
- `beautifulsoup4` - Web scraping
- `textblob` - Sentiment analysis
- `pandas` - Data manipulation
- `matplotlib` - Visualization
- `wordcloud` - Word cloud generation
- `langdetect` - Language detection

## 🚀 Usage

### Basic Usage
```powershell
python orcherstration.py
```

### Example with OpenRouter
```powershell
python example_openrouter_crew.py
```

## 🤖 Agents Overview

### 1. Crawler Agent
- **Role**: Web crawler
- **Goal**: Collect blog post content
- **Tools**: BeautifulSoup, requests

### 2. Cleaner Agent
- **Role**: Text preprocessor
- **Goal**: Clean and normalize text data
- **Tools**: Language detection, text cleaning

### 3. Analyzer Agent 🔥 (Uses OpenRouter)
- **Role**: Content analyzer
- **Goal**: Extract topics, themes, and motives
- **LLM**: OpenRouter (GPT-4, Claude, etc.)
- **Tools**: NLP analysis

### 4. Sentiment Agent
- **Role**: Sentiment evaluator
- **Goal**: Determine emotional polarity
- **Tools**: TextBlob, optional LLM enhancement

### 5. Reporter Agent
- **Role**: Report generator
- **Goal**: Create visual insights
- **Output**: Charts, word clouds, summary reports

## 🔧 Configuration

### Environment Variables (.env)
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_SITE_URL=http://localhost:3000
OPENROUTER_APP_NAME=CrewAI Multi-Agent System
```

### Model Selection

Edit `analyzer_agent.py` to change the model:

```python
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",  # Change this
    # ... other config
)
```

**Available Models:**
- `openai/gpt-4o-mini` - Fast & cheap (recommended for dev)
- `openai/gpt-4-turbo` - High quality
- `anthropic/claude-3-opus` - Long context
- `meta-llama/llama-3-70b` - Open source
- `google/gemini-pro-1.5` - Google's model

See full list: https://openrouter.ai/models

## 📊 Output Files

The system generates:
- `sentiment_chart.png` - Bar chart of sentiment scores
- `wordcloud.png` - Visual word frequency
- `report.txt` - Text summary of insights
- `crew_output.txt` - Full crew execution log

## 🛠️ Project Structure

```
crewaiagent/
├── analyzer_agent.py          # 🔥 Uses OpenRouter LLM
├── cleaneragent.py            # Text preprocessing
├── crawleragent.py            # Web scraping
├── sentiment_agent.py         # Sentiment analysis
├── reporter_agent.py          # Report generation
├── orcherstration.py          # Main crew orchestration
├── example_openrouter_crew.py # Complete example
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── setup.ps1                 # Setup automation script
├── OPENROUTER_SETUP_GUIDE.md # Detailed guide
└── README.md                 # This file
```

## 🔍 How It Works

### Sequential Flow

```
Keyword → Crawler → Cleaner → Analyzer → Sentiment → Reporter
          ↓         ↓         ↓          ↓          ↓
        Raw HTML   Clean    Topics    Polarity   Reports
                   Text     & Tone    Scores
```

### OpenRouter Integration Points

1. **Analyzer Agent**: Uses LLM for topic extraction
2. **Sentiment Agent**: Optional LLM-enhanced sentiment
3. **All Agents**: Can use `llm` parameter for AI-powered decisions

### Example Agent with LLM

```python
from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

agent = Agent(
    role="Content Analyzer",
    goal="Analyze content",
    llm=llm,  # Pass LLM here
    verbose=True
)
```

## 💰 Cost Management

- Start with `gpt-4o-mini` (cheapest)
- Monitor usage at: https://openrouter.ai/activity
- Set spending limits in OpenRouter dashboard
- Cache results to avoid redundant API calls

## 🐛 Troubleshooting

### Import Errors
```powershell
pip install langchain-openai --upgrade
pip install crewai --upgrade
```

### Authentication Failed
- Check `.env` file exists in project root
- Verify API key format: `sk-or-v1-...`
- Ensure no extra spaces in `.env`

### Rate Limit Errors
- Use cheaper models for testing
- Add delays between requests
- Check OpenRouter dashboard for limits

### Module Not Found
```powershell
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Documentation

- **OpenRouter Setup**: See `OPENROUTER_SETUP_GUIDE.md`
- **OpenRouter Docs**: https://openrouter.ai/docs
- **CrewAI Docs**: https://docs.crewai.com
- **LangChain Docs**: https://python.langchain.com

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with OpenRouter
5. Submit a pull request

## 📝 License

This project is for educational purposes.

## 🔐 Security

- Never commit `.env` files
- Add `.env` to `.gitignore`
- Rotate API keys regularly
- Use environment variables for all secrets

## 🎓 Learning Resources

- [OpenRouter Models](https://openrouter.ai/models)
- [CrewAI Examples](https://github.com/joaomdmoura/crewAI-examples)
- [LangChain Tutorial](https://python.langchain.com/docs/get_started/introduction)

## 💡 Tips

1. **Development**: Use `gpt-4o-mini` for testing
2. **Production**: Upgrade to `gpt-4-turbo` for quality
3. **Debugging**: Set `verbose=True` on agents
4. **Monitoring**: Check OpenRouter dashboard daily
5. **Optimization**: Cache LLM responses when possible

## 🚦 Status

✅ OpenRouter integration configured
✅ Multi-agent workflow implemented
✅ Example code provided
✅ Documentation complete

---

**Need Help?**
- Check `OPENROUTER_SETUP_GUIDE.md` for detailed setup
- Run `.\setup.ps1` for automated setup
- Test with `python example_openrouter_crew.py`

**Happy Building! 🚀**
