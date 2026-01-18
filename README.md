# PowerBI-LLM

> AI-Powered Documentation Assistant for Power BI Reports

## Overview

**PowerBI-LLM** is an intelligent documentation assistant that leverages Large Language Models (OpenAI) to automatically generate professional documentation for Power BI reports. It eliminates the tedious manual work of documenting dashboards, KPIs, measures, and data structures.

### What It Does

This tool analyzes your Power BI project files (.pbip) and PDF exports to:
- **Generate embedded README pages** directly within Power BI files with dashboard summaries and KPI definitions
- **Create comprehensive external documentation** suitable for platforms like Confluence, including dataset details, measures, and DAX expressions
- **Support multiple languages** (English, French, Chinese) for international teams
- **Intelligently route requests** using OpenAI's function calling to the appropriate documentation generator

---

### Architecture Overview

```

## Project Structure

```
PowerBI-LLM/
│
├── streamlit_app.py              # Main entry point - Streamlit application
├── requirements.txt              # Python dependencies
│
├── config/                       # Configuration and constants
│   ├── config.py                # Application constants, error messages, UI text
│   ├── function_descriptions.py # OpenAI function definitions for function calling
│   └── translation.py           # Multi-language translation support
│
├── src/                         # Core application logic
│   │
│   ├── handlers/                # High-level business logic handlers
│   │   ├── readme_handler.py            # Orchestrates README generation flow
│   │   └── documentation_handler.py     # Orchestrates documentation generation flow
│   │
│   ├── openai_connecter/        # OpenAI integration layer
│   │   ├── function_coordinator.py      # Routes requests to handlers (DIP pattern)
│   │   ├── handlers/                    # Function-specific handler implementations
│   │   │   ├── base_handler.py         # Abstract FunctionHandler + DTOs
│   │   │   ├── readme_function_handler.py       # Concrete README handler
│   │   │   └── documentation_function_handler.py # Concrete documentation handler
│   │   ├── general_openai_connecter.py  # OpenAI API calls (completions, function calling)
│   │   └── summarize_dashboard.py       # Dashboard summarization using LLM
│   │
│   ├── file_operator/           # File handling operations
│   │   └── file_operations.py   # ZIP extraction, PDF-to-image conversion, file modification
│   │
│   ├── json_operator/           # JSON data manipulation
│   │   ├── json_extraction.py   # Extract structure from Power BI JSON files
│   │   └── json_update.py       # Modify and insert data into Power BI JSON
│   │
│   ├── ui/                      # Streamlit UI components
│   │   ├── sidebar.py           # API key, language, model selection inputs
│   │   └── inputs.py            # File upload and action buttons
│   │
│   └── validators/              # Input validation
│       └── input_validator.py   # Validate API key and uploaded files
│
└── functions/                   # Legacy utility functions (mostly unused)
```

### Layer Responsibilities

1. **UI Layer** (`streamlit_app.py`, `src/ui/`): User interface, input collection, file uploads
2. **Handler Layer** (`src/handlers/`): High-level business logic orchestration
3. **Coordinator Layer** (`src/openai_connecter/function_coordinator.py`): Request routing using DIP
4. **Implementation Layer** (`src/openai_connecter/handlers/`): Concrete handler implementations
5. **Service Layer** (`src/openai_connecter/`, `src/file_operator/`, `src/json_operator/`): Specialized operations
6. **Configuration Layer** (`config/`): Constants, translations, function definitions

---

## Getting Started

### Prerequisites

- **Python 3.x** (tested with Python 3.8+)
- **OpenAI API Key** with access to GPT models
- **Power BI Project** as a `.zip` file (PBIP format)
- **PDF Export** of your Power BI report

### Running the Application

```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

### Basic Usage

1. **Enter OpenAI API Key**: Paste your API key in the sidebar
2. **Select Language**: Choose your preferred output language (English, French, Chinese)
3. **Select Model**: Choose the OpenAI model (gpt-5, gpt-4.1, gpt-3.5-turbo)
4. **Upload Files**:
   - Upload your Power BI project as a `.zip` file
   - Upload a PDF export of your report
5. **Choose Action**:
   - Click **"Generate README"** to create an embedded README page in the PBIP file
   - Click **"Generate Documentation"** to create a comprehensive external documentation file
6. **Download Results**: Download the modified PBIP file or documentation file

---

## How It Works

### Application Flow

```
1. User uploads ZIP (PBIP) + PDF files
          ↓
2. Validation (API key, file types)
          ↓
3. File extraction & PDF-to-image conversion
          ↓
4. User selects action (README or Documentation)
          ↓
5. FunctionCoordinator routes to appropriate handler
          ↓
6. Handler processes request:
   - Extracts dashboard structure from JSON
   - Converts PDF pages to images
   - Sends to OpenAI for summarization
   - Generates structured documentation
          ↓
7. For README: Modifies report.json and repackages ZIP
   For Documentation: Generates text file
          ↓
8. User downloads result
```

---

## Contributing

Contributions are welcome! When contributing, please:

1. Follow the **SOLID principles** outlined in this README
2. Implement the `FunctionHandler` interface for new handlers
3. Add appropriate error handling and validation
4. Update documentation and configuration
5. Write tests for new functionality
6. Keep handlers focused and maintainable
