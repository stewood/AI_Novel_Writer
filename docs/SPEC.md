# Novel Writer - Technical Specification

## Overview

Novel Writer is an AI-powered command-line tool that helps authors generate creative story ideas through a system of specialized AI agents. The tool uses a multi-agent architecture to create, evaluate, and refine story concepts, ensuring high-quality, original outputs.

## System Architecture

### 1. Command-Line Interface

#### Entry Points
- Main command: `novel_writer`
- Primary subcommand: `novel_writer idea`
- Future subcommands planned: `outline`, `scene`, `character`

#### Command Options
```bash
novel_writer idea [OPTIONS]
  --genre TEXT      Specify a genre for the story
  --tone TEXT       Specify the emotional/narrative tone
  --themes TEXT     Specify themes to explore (multiple allowed)
  --output TEXT     Path for the output file
  --log-level TEXT  Set logging level (ERROR|WARN|INFO|DEBUG|SUPERDEBUG)
  --log-file TEXT   Path to log file
  --console-log     Enable detailed console logging
```

### 2. Agent System

#### 2.1 Facilitator Agent
- **Purpose**: Orchestrates the entire idea generation process
- **Responsibilities**:
  - Coordinates other agents
  - Manages workflow progression
  - Ensures quality control
  - Handles error recovery

#### 2.2 Genre and Vibe Generator Agent
- **Purpose**: Determines story genre and tone
- **Responsibilities**:
  - Selects random subgenre if none specified
  - Ensures genre-tone compatibility
  - Suggests appropriate themes

#### 2.3 Pitch Generator Agent
- **Purpose**: Creates initial story concepts
- **Responsibilities**:
  - Generates multiple story pitches
  - Ensures genre alignment
  - Incorporates specified themes

#### 2.4 Critic Agent
- **Purpose**: Evaluates story pitches
- **Responsibilities**:
  - Scores pitches on multiple criteria
  - Provides detailed feedback
  - Identifies potential improvements

#### 2.5 Improver Agent
- **Purpose**: Enhances story concepts
- **Responsibilities**:
  - Refines weak pitches
  - Addresses critic feedback
  - Strengthens story elements

#### 2.6 Voter Agent
- **Purpose**: Selects best story concept
- **Responsibilities**:
  - Evaluates improved pitches
  - Ranks options
  - Makes final selection

#### 2.7 Tropemaster Agent
- **Purpose**: Analyzes and improves trope usage
- **Responsibilities**:
  - Identifies common tropes
  - Suggests unique twists
  - Ensures originality

#### 2.8 Meeting Recorder Agent
- **Purpose**: Documents final output
- **Responsibilities**:
  - Formats results
  - Generates YAML frontmatter
  - Creates Markdown document

### 3. Configuration System

#### 3.1 LLM Configuration
- Supports multiple API providers
- Manages API keys and quotas
- Handles rate limiting
- Supports different model configurations

#### 3.2 Logging System
- **Levels**:
  - ERROR: Critical failures
  - WARN: Important issues
  - INFO: Major milestones
  - DEBUG: Detailed operations
  - SUPERDEBUG: Complete tracing
- **Outputs**:
  - File logging
  - Console logging
  - Status updates

### 4. Output Format

#### 4.1 Directory Structure
```
ideas/
  └── story-title/
      └── story-title_YYYYMMDD-HHMMSS.md
```

#### 4.2 Document Format
```yaml
---
doc_type: idea
doc_id: idea_YYYYMMDD_HHMMSS
status: winner
version: v1
tags: [genre, tone, themes, AI_generated]
title: Story Title
elevator_pitch: 1-2 sentence hook
genre: main genre or subgenre
tone: emotional/narrative style
themes: [core themes]
summary: expanded story concept
notes: creative rationale
tropes: [detected tropes]
trope_suggestions: [alternative twists]
---

[Markdown content with structured sections]
```

## Development Guidelines

### 1. Code Organization
```
novel_writer/
├── agents/           # Agent implementations
├── config/          # Configuration modules
├── data/           # Static data (genres, etc.)
├── utils/          # Utility functions
└── cli.py         # Command-line interface
```

### 2. Testing Requirements
- Unit tests for each agent
- Integration tests for workflows
- Test coverage requirements
- Mock LLM responses

### 3. Error Handling
- Graceful degradation
- Informative error messages
- Recovery strategies
- User feedback

### 4. Performance Considerations
- Asynchronous operations
- Rate limiting
- Resource management
- Response caching

## Future Enhancements

### 1. Planned Features
- Story outline generation
- Character development
- Scene generation
- World-building assistance

### 2. Technical Improvements
- Plugin system
- Custom agent development
- Alternative LLM providers
- Enhanced caching

### 3. User Experience
- Interactive mode
- Progress visualization
- Template customization
- Export formats

## Dependencies

### Required Packages
- click>=8.0.0: CLI framework
- openai>=1.0.0: LLM integration
- pyyaml>=6.0.0: Configuration handling
- rich>=10.0.0: Console output
- python-dotenv>=1.0.0: Environment management

### Development Dependencies
- pytest>=7.0.0: Testing framework
- pytest-asyncio>=0.23.0: Async test support 