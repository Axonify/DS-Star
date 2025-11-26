# DS-STAR: A Data Science Agentic Framework

DS-STAR (Data Science - Structured Thought and Action) is a Python-based agentic framework for automating data science tasks. It leverages a multi-agent system powered by Google's Gemini models via Vertex AI, with optional support for OpenAI models. The framework uses gcloud authentication for secure, enterprise-grade access without requiring API key management.

This project is an implementation of the paper from Google Research: [DS-STAR: A State-of-the-Art Versatile Data Science Agent](https://research.google/blog/ds-star-a-state-of-the-art-versatile-data-science-agent/). [Paper](https://arxiv.org/pdf/2509.21825)

## Features

- **Agentic Workflow**: Implements a pipeline of specialized AI agents (Analyzer, Planner, Coder, Verifier, Router, Debugger, Finalyzer) that collaborate to solve data science problems.
- **Vertex AI Integration**: Enterprise-ready with Vertex AI support using gcloud authentication for secure, organization-wide deployments of Gemini models. No API keys required.
- **Multi-Provider Support**: Flexible architecture allowing optional integration with OpenAI GPT models alongside Vertex AI Gemini models. Each agent can be configured with a different model provider.
- **Reproducibility**: Every step of the pipeline is saved, including prompts, generated code, execution results, and metadata. This allows for complete auditability and reproducibility of results.
- **Interactive & Resume-able**: Runs can be paused and resumed. The interactive mode allows for step-by-step execution.
- **Code Editing & Debugging**: Allows users to manually edit the generated code during a run and features an auto-debug agent to fix execution errors.
- **Rich Data Science Toolkit**: Built-in support for pandas, scikit-learn, matplotlib, seaborn, and NLP libraries (textblob, vadersentiment) for comprehensive data analysis.
- **Configuration-driven**: Project settings, model parameters, and run configurations are managed through a `config.yaml` file.

## How it Works

The DS-STAR pipeline is composed of several phases and agents:

1.  **Analysis**: The `Analyzer` agent inspects the initial data files and generates summaries.
2.  **Iterative Planning & Execution**:
    *   The `Planner` creates an initial plan to address the user's query.
    *   The `Coder` generates Python code to execute the current step of the plan.
    *   The code is executed, and the result is captured.
    *   An automatic `Debugger` agent attempts to fix any code that fails.
    *   The `Verifier` checks if the result sufficiently answers the query.
    *   The `Router` decides what to do next: either finalize the plan or add a new step for refinement.
    *   This loop continues until the plan is deemed sufficient or the maximum number of refinement rounds is reached.
3.  **Finalization**: The `Finalyzer` agent takes the final code and results and formats them into a clean, specified output format (e.g., JSON).

All artifacts for each run are stored in the `runs/` directory, organized by `run_id`.

## Project Structure

```
/
├─── dsstar.py               # Main script containing the agent logic and CLI
├─── provider.py             # Model provider abstraction (Gemini, Vertex AI, OpenAI)
├─── config.yaml             # Main configuration file
├─── prompt.yaml             # Prompts for the different AI agents
├─── pyproject.toml          # Project metadata and dependencies (uv format)
├─── uv.lock                 # Locked dependency versions for reproducibility
├─── .python-version         # Python version specification for uv
├─── data/                   # Directory for your data files
└─── runs/                   # Directory where all experiment runs and artifacts are stored
```

## Getting Started

### Prerequisites

- Python 3.11+
- **Vertex AI with GCP**: GCP project with Vertex AI API enabled and gcloud authentication configured (for Gemini models)
- **OpenAI** (optional): OpenAI API key if you want to use GPT models
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Installation

#### Using uv (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd DS-Star
    ```

2.  **Install uv (if not already installed):**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

3.  **Install dependencies with uv:**
    ```bash
    uv sync
    ```

### Configuration

#### Step 1: Set up Google Cloud Authentication

DS-STAR uses Vertex AI for accessing Gemini models via gcloud authentication. This provides secure, enterprise-grade access without managing API keys.

```bash
# Install gcloud CLI if not already installed
# https://cloud.google.com/sdk/docs/install

# Authenticate with your Google account
gcloud auth application-default login

# Enable Vertex AI API (if not already enabled)
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

#### Step 2: Configure `config.yaml`

Create a `config.yaml` file in the root of the project:

```yaml
# config.yaml
model_name: 'gemini-2.5-flash'
max_refinement_rounds: 3
interactive: false
preserve_artifacts: true

# Vertex AI configuration for Gemini models
use_vertex_ai: true
vertex_ai_project: "your-gcp-project-id"  # Or set GOOGLE_CLOUD_PROJECT env var
vertex_ai_location: "us-central1"  # Your preferred GCP region

# Gemini generation parameters
temperature: 1.0  # Range: 0.0-2.0, controls randomness (lower = more deterministic)
seed: null  # Optional integer for deterministic outputs (null = random)

# Optional: Configure specific models for different agents
agent_models:
  PLANNER: 'gemini-2.5-flash'
  CODER: 'gemini-2.5-flash'
  VERIFIER: 'gemini-2.5-flash'
```

## Usage

Place your data files (e.g., `.xlsx`, `.csv`) in the `data/` directory.

### Starting a New Run

To start a new analysis, you need to provide the data files and a query.

Using uv:
```bash
uv run python dsstar.py --data-files file1.xlsx file2.xlsx --query "What is the total sales for each department?"
```

### Resuming a Run

If a run was interrupted, you can resume it using its `run_id`.

```bash
uv run python dsstar.py --resume <run_id>
```

### Editing Code During a Run

You can manually edit the last generated piece of code and re-run it. This is useful for manual debugging or tweaking the agent's logic.

```bash
uv run python dsstar.py --edit-last --resume <run_id>
```
This will open the last code file in your default text editor (`nano`, `vim`, etc.). After you save and close the editor, the script will re-execute the modified code.

### Interactive Mode

To review each step before proceeding, use the interactive flag.

```bash
uv run python dsstar.py --interactive --data-files ... --query "..."
```

## UV Package Manager

This project uses `uv` for fast and reliable dependency management. Here are some useful commands:

### Common UV Commands

- **Install dependencies**: `uv sync`
- **Add a new dependency**: `uv add package-name`
- **Remove a dependency**: `uv remove package-name`
- **Update dependencies**: `uv sync --upgrade`
- **Run a command in the virtual environment**: `uv run python script.py`
- **Show installed packages**: `uv pip list`

### Benefits of UV

- **Speed**: uv is 10-100x faster than pip
- **Reliability**: Consistent dependency resolution with lock files
- **No virtual environment activation needed**: Use `uv run` to execute commands directly
- **Better dependency resolution**: Automatically resolves complex dependency conflicts

## Configuration Reference

The following options are available in `config.yaml` and can be overridden by CLI arguments:

### Basic Settings
- `run_id` (string): The ID of a run to resume.
- `max_refinement_rounds` (int): The maximum number of times the agent will try to refine its plan.
- `model_name` (string): The default model to use (e.g., `gemini-2.5-flash`, `gpt-4`).
- `interactive` (bool): If true, waits for user input before executing each step.
- `auto_debug` (bool): If true, the `Debugger` agent will automatically try to fix failing code (defaults to true)
- `execution_timeout` (int): Timeout in seconds for code execution.
- `preserve_artifacts` (bool): if set, all step artifacts are saved to the `runs` directory (set to true by defualt)

### Vertex AI Settings (Required for Gemini Models)
- `use_vertex_ai` (bool): Set to `true` to use Vertex AI for Gemini models (recommended).
- `vertex_ai_project` (string): Your GCP project ID. Can also be set via `GOOGLE_CLOUD_PROJECT` environment variable.
- `vertex_ai_location` (string): GCP region for Vertex AI (e.g., `us-central1`).

### Generation Parameters (For Gemini Models)
- `temperature` (float): Controls randomness in model outputs. Range: 0.0-2.0, default: 1.0.
  - Lower values (e.g., 0.2) produce more deterministic, focused outputs
  - Higher values (e.g., 1.8) produce more creative, diverse outputs
- `seed` (int or null): Optional integer seed for more deterministic outputs. Default: `null` (random).
  - Set to a specific integer (e.g., 42) to get more reproducible results across runs
  - Keep as `null` for random seed on each request


### Per-Agent Model Configuration
- `agent_models` (dict): A dictionary mapping agent names to specific model names. If not specified, `model_name` is used. You can mix different providers for different agents.
  ```yaml
  agent_models:
    PLANNER: 'gpt-4'              # Use OpenAI for planning
    CODER: 'gemini-2.5-flash'     # Use Gemini for coding
    VERIFIER: 'gemini-2.5-flash'  # Use Gemini for verification
  ```