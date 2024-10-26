import os
from loguru import logger as log

# Load .env variables
from dotenv import load_dotenv
load_dotenv(override=True)


# REMOVE THIS BLOCK IF YOU ARE USING THIS SCRIPT AS A TEMPLATE
# -------------------------------------------------------------
import sys
from pathlib import Path
# Add parent directory to path
path = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(path.parents[0]))
# -------------------------------------------------------------

# Import Cel.ai modules
from celai_chatwoot.connector import WootConnector
from cel.gateway.message_gateway import MessageGateway, StreamMode
from cel.assistants.macaw.macaw_assistant import MacawAssistant
from cel.prompt.prompt_template import PromptTemplate
from cel.assistants.request_context import RequestContext


# Setup prompt
prompt = """You are an AI assistant. Called Celia. You can help a user to buy Bitcoins."""
prompt_template = PromptTemplate(prompt)

# Create the assistant based on the Macaw Assistant 
# NOTE: Make sure to provide api key in the environment variable `OPENAI_API_KEY`
# add this line to your .env file: OPENAI_API_KEY=your-key
# or uncomment the next line and replace `your-key` with your OpenAI API key
# os.environ["OPENAI_API_KEY"] = "your-key.."
ast = MacawAssistant(
    prompt=prompt_template
)
    
@ast.event('message')
async def handle_message(session, ctx: RequestContext):
    log.critical(f"Got message event with message!")
    assert isinstance(ctx.connector, WootConnector)
    
    if ctx.message.text == "img":
        await ctx.connector.send_image_message(
            ctx.lead,
            "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png",
            "This is an image"
        )       
        return RequestContext.cancel_ai_response()
    
    if ctx.message.text == "audio":
        await ctx.connector.send_audio_message(
            ctx.lead,
            "https://www.w3schools.com/html/horse.mp3"
        )       
        return RequestContext.cancel_ai_response()



# Create the Message Gateway - This component is the core of the assistant
# It handles the communication between the assistant and the connectors
gateway = MessageGateway(
    assistant=ast,
    host="127.0.0.1", port=8000
)

# For this example, we will use the Telegram connector
conn = WootConnector(
    bot_name="Testing Ale Bot",
    access_key=os.environ.get("CHATWOOT_ACCESS_KEY"),
    account_id=os.environ.get("CHATWOOT_ACCOUNT_ID"),
    inbox_id=os.environ.get("CHATWOOT_INBOX_ID"),
    chatwoot_url=os.environ.get("CHATWOOT_URL"),
    bot_description="This is a test bot",
    stream_mode=StreamMode.FULL
)
# Register the connector with the gateway
gateway.register_connector(conn)

# Then start the gateway and begin processing messages
gateway.run(enable_ngrok=True)
