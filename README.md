# Novel Writer

An AI-powered novel writing assistant that helps you generate creative story ideas using multiple specialized AI agents.

## Installation

You can install Novel Writer using pip:

```bash
pip install novel-writer
```

Or install in development mode:

```bash
git clone https://github.com/yourusername/novel-writer.git
cd novel-writer
pip install -e .
```

## Usage

After installation, you can use the `novel_writer` command from anywhere:

```bash
novel_writer idea --genre cyberpunk --tone noir --themes identity technology corruption
```

### Available Commands

- `novel_writer idea`: Generate a new story idea
  - `--genre`: Specify the main genre (e.g., science fiction, fantasy)
  - `--tone`: Specify the tone (e.g., dark, hopeful, gritty)
  - `--themes`: Specify themes (can provide multiple)
  - `--output`: Specify output directory (optional)

### Examples

Generate a cyberpunk story idea:
```bash
novel_writer idea --genre cyberpunk --tone noir --themes identity technology corruption
```

Generate a fantasy story idea:
```bash
novel_writer idea --genre fantasy --tone epic --themes heroism sacrifice destiny
```

## Development

To run tests:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 