# RevitMind

RevitMind is an intelligent assistant for Autodesk Revit that leverages the power of AI to help MEP engineers and designers work more efficiently. Built as a pyRevit extension, it provides natural language interaction with Revit, allowing users to perform complex tasks using simple commands.

## Features

- 🤖 Natural Language Processing: Interact with Revit using plain English or Turkish commands
- 🔍 Smart MEP Analysis: Analyze ductwork, piping, and other MEP elements
- 📊 Automated Measurements: Calculate lengths, sizes, and other parameters automatically
- 🛠️ Custom Commands: Perform complex operations with simple text commands
- 🌐 AI-Powered: Utilizes OpenRouter API for intelligent command processing

## Installation

1. Install [pyRevit](https://github.com/eirannejad/pyRevit) if you haven't already
2. Clone this repository to your pyRevit extensions folder:
```bash
cd %appdata%\pyRevit\Extensions
git clone https://github.com/BTankut/RevitMind.git
```
3. Restart Revit
4. The RevitMind tab should now appear in your Revit ribbon

## Usage

1. Click on the "Chat" button in the RevitMind tab
2. Type your command in natural language, for example:
   - "Calculate the total length of all ducts"
   - "Find the largest duct in the model"
   - "List all duct sizes"
3. RevitMind will process your command and execute the appropriate Revit operations

## Requirements

- Autodesk Revit 2022 or later
- pyRevit 4.8 or later
- Python 2.7 (included with pyRevit)
- Internet connection for AI functionality

## Configuration

1. Obtain an API key from [OpenRouter](https://openrouter.ai/)
2. Create a `chatgptapikey.env` file in the server directory
3. Add your API key to the file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [pyRevit](https://github.com/eirannejad/pyRevit)
- Powered by [OpenRouter](https://openrouter.ai/)
- Special thanks to the Revit API community

## Version History

- v0.1.0 (2024-01-26)
  - Initial release
  - Basic MEP analysis functionality
  - Natural language command processing
  - Support for both English and Turkish commands
