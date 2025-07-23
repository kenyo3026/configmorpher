# ConfigMorpher 🎯

A lightweight and powerful Python configuration morpher that dynamically maps configuration data to any callable objects (functions, classes, methods) with ease.

## ✨ Key Features

- **🔄 Dynamic Mapping**: Automatically map configuration dictionaries to any callable object's parameters
- **📁 Multiple Formats**: Support for JSON, YAML, and TOML configuration files
- **🎯 Smart Navigation**: Access nested configurations using dot notation (e.g., `"database.connection.host"`)
- **🔧 Flexible Returns**: Choose between dataclass instances or dictionaries as return types
- **📦 Lightweight**: Minimal dependencies, focused on core functionality
- **🎨 Clean API**: Intuitive and developer-friendly interface

## 🚀 Quick Start

### Installation

#### From Git Repository (Recommended)
```bash
# Install directly from GitHub
pip install git+https://github.com/kenyo3026/configmorpher.git

# Or install a specific branch/tag
pip install git+https://github.com/kenyo3026/configmorpher.git@main
```

#### From PyPI (When Available)
```bash
pip install configmorpher
```

#### Development Installation
```bash
# Clone the repository
git clone https://github.com/kenyo3026/configmorpher.git
cd configmorpher

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

**Dependencies:**
- Python 3.7+
- PyYAML

### Basic Usage

```python
from config_morpher import ConfigMorpher

# Example configuration
config_data = {
    'database': {
        'host': 'localhost',
        'port': 5432,
        'username': 'admin',
        'password': 'secret'
    },
    'api': {
        'timeout': 30,
        'retries': 3
    }
}

# Initialize morpher
morpher = ConfigMorpher(config_data)

# Define your function/class
def connect_database(host: str, port: int, username: str, password: str):
    return f"Connecting to {host}:{port} as {username}"

# Morph configuration to match function parameters
db_config = morpher.morph(
    connect_database,
    start_from='database',
    return_type='dict'
)

# Use the morphed configuration
connection = connect_database(**db_config)
print(connection)  # Output: Connecting to localhost:5432 as admin
```

## 📖 Detailed Usage

### Loading from Files

```python
from pathlib import Path
from config_morpher import ConfigMorpher

# From YAML file
morpher = ConfigMorpher.from_yaml(Path('config.yaml'))

# From JSON file
morpher = ConfigMorpher.from_json(Path('config.json'))

# From TOML file
morpher = ConfigMorpher.from_toml(Path('config.toml'))
```

### Working with Classes

```python
class DatabaseConnection:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

# Morph configuration for class constructor
config_morpher = ConfigMorpher(config_data)
db_config = config_morpher.morph(
    DatabaseConnection,
    start_from='database',
    return_type='dict'
)

# Create instance
db = DatabaseConnection(**db_config)
```

### Working with Dataclasses

```python
from dataclasses import dataclass

@dataclass
class APIConfig:
    timeout: int
    retries: int
    base_url: str = "https://api.example.com"

# Morph to dataclass instance
api_config = config_morpher.morph(
    APIConfig,
    start_from='api',
    return_type='dataclass'
)

print(api_config.timeout)  # 30
```

### Real-world Example: OpenAI Client Configuration

```python
import openai
from config_morpher import ConfigMorpher

config_data = {
    'openai': {
        'base_url': 'https://api.openai.com/v1',
        'api_key': 'your-api-key-here',
        'chat': {
            'completions': {
                'model': 'gpt-4',
                'max_tokens': 1000,
                'temperature': 0.7,
            }
        }
    }
}

morpher = ConfigMorpher(config_data)

# Configure OpenAI client
openai_config = morpher.morph(openai.OpenAI, start_from='openai', return_type='dict')
client = openai.OpenAI(**openai_config)

# Configure chat completions
chat_config = morpher.morph(
    client.chat.completions.create,
    start_from='openai.chat.completions',
    return_type='dict'
)

# Make API call
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}],
    **chat_config
)
```

## 📚 API Reference

### ConfigMorpher Class

#### Constructor
```python
ConfigMorpher(config: Dict[str, Any])
```
Initialize with a configuration dictionary.

#### Class Methods
```python
@classmethod
def from_yaml(cls, config_path: Path) -> ConfigMorpher:
    """Load configuration from YAML file"""

@classmethod
def from_json(cls, config_path: Path) -> ConfigMorpher:
    """Load configuration from JSON file"""

@classmethod
def from_toml(cls, config_path: Path) -> ConfigMorpher:
    """Load configuration from TOML file"""
```

#### Morph Method
```python
def morph(
    self,
    callable_obj: Union[CallableObj, Iterable[CallableObj]],
    start_from: Union[str, List[str]] = None,
    allow_extra_keys: bool = True,
    return_type: ReturnType = ReturnType.DICT,
    return_config_keys_only: bool = True,
) -> Union[Any, Tuple[Any, ...]]:
```

**Parameters:**
- `callable_obj`: The target callable(s) to map configuration to
- `start_from`: Navigate to specific nested configuration section
- `allow_extra_keys`: Whether to allow unused configuration keys
- `return_type`: Return as 'dict' or 'dataclass'
- `return_config_keys_only`: Include only keys present in configuration when returning dict

### ReturnType Enum
```python
class ReturnType(Enum):
    DATACLASS = 'dataclass'
    DICT = 'dict'
```

## 📝 Configuration File Examples

### YAML (config.yaml)
```yaml
database:
  host: localhost
  port: 5432
  username: admin
  password: secret

api:
  timeout: 30
  retries: 3
  base_url: https://api.example.com
```

### JSON (config.json)
```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "username": "admin",
    "password": "secret"
  },
  "api": {
    "timeout": 30,
    "retries": 3,
    "base_url": "https://api.example.com"
  }
}
```

### TOML (config.toml)
```toml
[database]
host = "localhost"
port = 5432
username = "admin"
password = "secret"

[api]
timeout = 30
retries = 3
base_url = "https://api.example.com"
```

## 🔧 Advanced Features

### Multiple Schema Parsing
```python
# Morph configuration for multiple callables at once
db_config, api_config = morpher.morph(
    [DatabaseConnection, APIConfig],
    start_from=['database', 'api'],
    return_type='dict'
)
```

### Nested Configuration Access
```python
# Access deeply nested configurations
deep_config = morpher.morph(
    some_function,
    start_from='level1.level2.level3',
    return_type='dict'
)
```

### Error Handling
```python
try:
    config = morpher.morph(MyClass, start_from='nonexistent')
except ValueError as e:
    print(f"Configuration error: {e}")
```

## 🚧 Future Work

We're continuously improving ConfigMorpher! Here's what's coming:

### Short-term (1-2 weeks)
- [ ] **Enhanced Documentation**: More examples and tutorials
- [ ] **Better Error Messages**: More descriptive and helpful error messages
- [ ] **Comprehensive Tests**: Full test suite with high coverage

### Medium-term (1-2 months)
- [ ] **Data Validation**: Built-in validation for configuration values
- [ ] **Environment Variables**: Support for environment variable substitution
- [ ] **Configuration Hot Reload**: Monitor and reload configuration files automatically
- [ ] **INI Format Support**: Additional configuration file format
- [ ] **Configuration Merging**: Merge multiple configuration sources

### Long-term (3-6 months)
- [ ] **Framework Integration**: FastAPI and Django plugins
- [ ] **CLI Tool**: Command-line interface for configuration management
- [ ] **Configuration Templates**: Template system for reusable configurations
- [ ] **Variable Interpolation**: Support for variable substitution in configurations
- [ ] **Configuration Inheritance**: Hierarchical configuration support

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Clone the repository
git clone https://github.com/kenyo3026/configmorpher.git
cd configmorpher

# Install dependencies
pip install -r requirements.txt

# Run tests (when available)
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for seamless configuration-to-code mapping
- Built with Python's powerful introspection capabilities
- Thanks to the open-source community for inspiration and feedback

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/kenyo3026/configmorpher/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kenyo3026/configmorpher/discussions)
- **Email**: your.email@example.com

---

Made with ❤️ by [Your Name]
