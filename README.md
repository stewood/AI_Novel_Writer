# NovelWriter Idea Generator

A powerful CLI tool that uses AI agents to generate unique and compelling novel ideas. The tool orchestrates multiple specialized agents to create, evaluate, and refine story concepts.

## Features

- Generate unique story ideas using AI agents
- Support for various science fiction and fantasy subgenres
- Intelligent pitch generation and evaluation
- Trope analysis and improvement suggestions
- Structured output in Markdown format with YAML frontmatter
- Comprehensive logging system

## Installation

```bash
pip install novelwriter_idea
```

## Usage

Generate a new story idea:

```bash
novelwriter_idea idea [OPTIONS]

Options:
  --genre TEXT     Specify a genre (optional)
  --tone TEXT      Specify the tone (optional)
  --themes TEXT    Specify themes (optional)
  --output PATH    Specify output path (optional)
  --help          Show this message and exit.
```

## Output Structure

Generated ideas are saved as Markdown files with the following structure:

```yaml
---
doc_type: idea
doc_id: idea_20250319_153000
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
```

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install development dependencies: `pip install -r requirements.txt`
5. Run tests: `pytest`

## License

MIT License 