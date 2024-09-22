<!-- A centered logo of celia -->
<p align="center">
  <img src="https://raw.githubusercontent.com/cel-ai/celai/30b489b21090e3c3f00ffea66d0ae4ac812bd839/cel/assets/celia_logo.png" width="250" />
</p>

# Celai Chatwoot Connector

`celai-chatwoot` is Python package that provides a connector for integrating the Cel.ai framework with Chatwoot. This allows seamless communication between your Cel.ai assistants and Chatwoot, enabling you to leverage Chatwoot's powerful customer support features.
- [Cel.ai](https://github.com/cel-ai/celai) 
- [Chatwoot](https://www.chatwoot.com/)

## Features

- Easy integration with Chatwoot Bot API 
- Full stream mode support
- Customizable bot settings

## Installation

You can install the `celai-chatwoot` package using pip:

```bash
pip install celai-chatwoot
```

## Usage

To use the `celai-chatwoot` connector, you need to create an instance of `WootConnector` and register it with the Cel.ai gateway. Below is an example of how to do this:

```python
import os
from celai_chatwoot.connector import WootConnector

# Create an instance of WootConnector
conn = WootConnector(
    bot_name="Bot Name",
    access_key=os.environ.get("CHATWOOT_ACCESS_KEY"),
    account_id=os.environ.get("CHATWOOT_ACCOUNT_ID"),
    chatwoot_url=os.environ.get("CHATWOOT_URL"),
    bot_description="This is a test bot",
    stream_mode=StreamMode.FULL
)

# Register the connector with the gateway
gateway.register_connector(conn)
```

## Environment Variables

The `WootConnector` requires the following environment variables to be set:

- `CHATWOOT_ACCESS_KEY`: Your Chatwoot access key
- `CHATWOOT_ACCOUNT_ID`: Your Chatwoot account ID
- `CHATWOOT_URL`: The URL of your Chatwoot instance

Run your Cel.ai assistant, then a new Chatwoot bot called "Bot Name" will be created in your Chatwoot instance. Assign the bot to any Inbox you want to use it with.

## Implemented Features

|                     | RECEIVE | SEND  |
|---------------------|:-------:|:-----:|
| **Text**            |    ✅    |   ✅   |
| **Image**           |    ✅    |   ✅   |
| **Audio**           |    ✅    |   ✅   |
| **Files**           |    ✅    |   ❌   |
| **Custom Attributes** |    ❌    |   ✅   |
| **Video**           |    ❌    |   ❌   |
| **Location**        |    ✅    |   ❌   |
| **Buttons**         |    -    |   ✅   |
| **Templates**       |    -    |   ❌   |

## Roadmap

Current version: 0.1.0 supports basic Chatwoot features such as sending and receiving text messages. Future versions will include the following features:

  - Image and file uploads
  - Custom attributes
  - Audio and video messages


## Contributing

We welcome contributions to the `celai-chatwoot` project. If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

Special thanks to the Cel.ai and Chatwoot teams for their amazing frameworks and support.

## Contact

For any questions or inquiries, please contact us at [alejamp@gmail.com].