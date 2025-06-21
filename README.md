# SHTxd Clip

A modern, feature-rich YouTube video downloader with a beautiful GUI built using Python and CustomTkinter.

## Features

- 🎬 Download single videos or entire playlists
- 🎨 Modern, dark-themed user interface
- 📱 Responsive design that works on different screen sizes
- 🎵 Support for multiple formats (MP4, MP3, etc.)
- 📊 Progress tracking with detailed statistics
- 🔍 Video preview with thumbnails and metadata
- 📚 Playlist management with custom range selection
- 🚀 Fast, multi-threaded downloads

## Requirements

- Python 3.7 or higher
- Required Python packages (automatically checked):
  - customtkinter
  - requests
  - pillow (PIL)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd SHTxd-YT-Dwnl
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install customtkinter requests pillow
```

## Usage

Run the application:
```bash
python3 main.py
```

Or use the provided scripts:
```bash
# Setup script (installs dependencies)
./setup.sh

# Run script
./run.sh
```

## Project Structure

```
SHTxd-YT-Dwnl/
├── main.py          # Main entry point
├── config.py        # Configuration settings
├── core.py          # Core download logic
├── ui.py            # User interface components
├── utils.py         # Utility functions
├── setup.sh         # Setup script
├── run.sh           # Run script
└── venv/            # Virtual environment (created after setup)
```

## Configuration

The application uses sensible defaults, but you can customize settings in `config.py`:

- Default download directory
- UI colors and themes
- Download quality preferences
- Playlist download limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect YouTube's Terms of Service and copyright laws.

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Run `python3 main.py` to check for missing packages
2. **Permission errors**: Ensure you have write permissions to the download directory
3. **Network issues**: Check your internet connection and firewall settings

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed
2. Make sure you're using Python 3.7+
3. Try running in a fresh virtual environment

## Disclaimer

This tool is for educational purposes only. Users are responsible for complying with YouTube's Terms of Service and applicable copyright laws.
