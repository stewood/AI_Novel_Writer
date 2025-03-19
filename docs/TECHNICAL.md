# Novel Writer - Technical Documentation

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation for Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/novel_writer.git
cd novel_writer
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. Install in development mode:
```bash
pip install -e .
```

### Environment Configuration

1. Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_paid_api_key
OPENROUTER_FREE_API_KEY=your_free_api_key
```

2. Configure logging (optional):
```env
LOG_LEVEL=DEBUG
LOG_FILE=path/to/custom.log
CONSOLE_LOG=True
```

## Project Structure

```
novel_writer/
├── agents/                 # AI agent implementations
│   ├── __init__.py
│   ├── facilitator_agent.py
│   ├── genre_vibe_agent.py
│   ├── pitch_generator_agent.py
│   ├── critic_agent.py
│   ├── improver_agent.py
│   ├── voter_agent.py
│   ├── tropemaster_agent.py
│   └── meeting_recorder_agent.py
├── config/                # Configuration modules
│   ├── __init__.py
│   ├── llm.py
│   └── logging.py
├── data/                 # Static data files
│   └── subgenres.json
├── utils/               # Utility functions
│   ├── __init__.py
│   └── file_utils.py
└── cli.py              # Command-line interface
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=novel_writer

# Run specific test file
pytest tests/test_facilitator_agent.py

# Run with verbose output
pytest -v
```

### Writing Tests

1. Create test files in the `tests/` directory
2. Use pytest fixtures for common setup
3. Mock LLM responses using the provided mock classes
4. Test both success and error cases

Example test:
```python
async def test_genre_selection(mock_llm):
    agent = GenreVibeAgent(llm_config=mock_llm)
    result = await agent.select_genre()
    assert "genre" in result
    assert "subgenre" in result
```

## Agent Development

### Creating a New Agent

1. Create a new file in `agents/`
2. Inherit from base agent class
3. Implement required methods
4. Add tests

Example:
```python
from novel_writer.agents.base import BaseAgent

class NewAgent(BaseAgent):
    async def process(self, input_data: dict) -> dict:
        # Implementation
        pass
```

### Agent Communication

- Agents communicate through standardized dictionaries
- Use typed data structures where possible
- Handle missing or invalid data gracefully
- Log important state changes

## Error Handling

### Guidelines
1. Use custom exceptions for specific error cases
2. Provide detailed error messages
3. Log errors with appropriate context
4. Implement recovery strategies where possible

### Example
```python
class AgentError(Exception):
    pass

try:
    result = await agent.process(data)
except AgentError as e:
    logger.error(f"Agent failed: {e}")
    # Implement recovery strategy
```

## Logging

### Levels
- ERROR: Critical failures
- WARN: Important issues
- INFO: Major milestones
- DEBUG: Detailed operations
- SUPERDEBUG: Complete tracing

### Best Practices
1. Log entry and exit of major functions
2. Include relevant context in log messages
3. Use appropriate log levels
4. Don't log sensitive information

## Contributing

1. Create a feature branch
2. Write tests for new functionality
3. Update documentation
4. Submit pull request

### Commit Message Format
```
type(scope): description

- feat: New feature
- fix: Bug fix
- docs: Documentation
- test: Tests
- refactor: Code refactoring
```

## Performance Optimization

### Guidelines
1. Use async/await for I/O operations
2. Implement caching where appropriate
3. Monitor API rate limits
4. Profile code for bottlenecks

### Example Cache Implementation
```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_genre_suggestions(theme: str) -> list:
    # Implementation
    pass
``` 