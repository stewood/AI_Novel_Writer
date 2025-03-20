# Novel Writer - Technical Specification

## Overview

Novel Writer is an AI-powered command-line tool that helps authors generate creative story ideas and outlines through a system of specialized AI agents. The tool uses a multi-agent architecture to create, evaluate, and refine story concepts, ensuring high-quality, original outputs.

## System Architecture

### 1. Command-Line Interface

#### Entry Points
- Main command: `novel_writer`
- Primary subcommands: 
  - `novel_writer idea` - Generate story ideas
  - `novel_writer outline` - Generate story outlines
- Future subcommands planned: `scene`, `character`

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

novel_writer outline [OPTIONS]
  --idea-file TEXT  Path to the idea file
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
  - Generates story outlines

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

#### 2.9 Plot Outliner Agent
- **Purpose**: Generates detailed story outlines
- **Responsibilities**:
  - Creates chapter-by-chapter structure
  - Ensures proper story arc
  - Maintains pacing and tension
  - Incorporates themes and character arcs

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
outlines/
  └── story-title/
      └── story-title-outline_YYYYMMDD-HHMMSS.md
```

#### 4.2 Idea Document Format
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

#### 4.3 Outline Document Format
```yaml
---
doc_type: outline
doc_id: outline_YYYYMMDD_HHMMSS
version: v1
status: draft
title: Story Title
genre: main genre or subgenre
tone: emotional/narrative style
themes: [core themes]
summary: story summary
---

# Outline Metadata
- Title: Story Title
- Genre: Main Genre
- Tone: Emotional Style
- Themes: Core Themes

## Story Summary
[Expanded story summary]

## Chapter Outlines
### Chapter 1: [Title]
**Act:** I
**Key Events:**
- Event 1
- Event 2
- Event 3
**Emotional Turn:** [Character emotional change]
**Character Focus:** [Main characters]
**Summary:** [Chapter summary]

[Additional chapters...]
```

## Development Guidelines

### 1. Code Organization
```
novel_writer/
├── agents/           # Agent implementations
│   ├── base_agent.py
│   ├── facilitator_agent.py
│   ├── genre_vibe_agent.py
│   ├── pitch_generator_agent.py
│   ├── critic_agent.py
│   ├── improver_agent.py
│   ├── voter_agent.py
│   ├── tropemaster_agent.py
│   ├── meeting_recorder_agent.py
│   └── plot_outliner_agent.py
├── config/          # Configuration modules
│   ├── llm.py
│   └── logging.py
├── data/           # Static data (genres, etc.)
├── utils/          # Utility functions
│   ├── file_ops.py
│   └── progress.py
└── cli.py         # Command-line interface

tests/
├── conftest.py    # Test configuration
├── test_agents/   # Agent tests
└── integration_tests/  # Integration tests
```

### 2. Testing Requirements
- Unit tests for each agent
- Integration tests for workflows
- Test coverage requirements
- Mock LLM responses
- Separate test and integration test directories

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
- Character development
- Scene generation
- World-building assistance
- Multiple outline formats

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