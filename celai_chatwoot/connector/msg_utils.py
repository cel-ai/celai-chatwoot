import asyncio
import base64
from dataclasses import dataclass
import json
import aiohttp
from typing import Any, Optional, Dict
from loguru import logger as log
import filetype
import os

ChatwootMessageTypes = ["incoming", "outgoing"]

@dataclass
class ChatwootAttachment:
    content: Any
    type: str = None
    fileName: Optional[str] = None
    fileUrl: Optional[str] = None


class ChatwootMessages:
    
    def __init__(self, 
                 base_url: str, 
                 account_id: str, 
                 access_key: str, 
                 headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.account_id = account_id
        self.access_key = access_key
        self.headers = headers or {}
        self.headers.update({
            'api_access_token': access_key
        })
        
        
    async def __build_content(self, attach: ChatwootAttachment):        
        if attach.type == "image":
            return await self.__build_content_image(attach.content)
        elif attach.type.startswith("audio"):
            return await self.__build_content_audio(attach.content)

        raise NotImplementedError(f"ChatwootClient: Unknown attachment type: {attach.type}")
                
    async def __build_content_image(self, content: Any):
        
        b64_img = None
        # if image is a file path, read the file
        # -------------------------------------------------------------
        if isinstance(content, str) and os.path.exists(content):
            with open(content, "rb") as f:
                b64_img = base64.b64encode(f.read()).decode()
        elif isinstance(content, bytes):
            b64_img = base64.b64encode(content).decode()
        elif isinstance(content, str):
            if content.startswith("data:image"):
                b64_img = content.split("base64,")[1]
            if content.startswith("http"):
                # download the image
                async with aiohttp.ClientSession() as session:
                    async with session.get(content) as resp:
                        b64_img = base64.b64encode(await resp.read()).decode()
            if len(content) > 100:
                b64_img = content
        else:
            raise ValueError("image must be a url/path to a file, a bytes object or a base64 string")             
        
        return b64_img
      
    async def __build_content_audio(self, content: str):
        if isinstance(content, str) and os.path.exists(content):
            with open(content, "rb") as f:
                b64_audio = base64.b64encode(f.read()).decode()
        elif isinstance(content, bytes):
            b64_audio = base64.b64encode(content).decode()
        elif isinstance(content, str):
            if content.startswith("data:audio"):
                b64_audio = content.split("base64,")[1]
            if content.startswith("http"):
                # download the audio
                async with aiohttp.ClientSession() as session:
                    async with session.get(content) as resp:
                        b64_audio = base64.b64encode(await resp.read()).decode()
                        
            if len(content) > 100:
                b64_audio = content
        else:
            raise ValueError("audio must be a url/path to a file, a bytes object or a base64 string")             
        
        return b64_audio
        
        
    # -------------------------------------------------------------
    async def send_text_message(
        self,
        conversation_id: str,
        content: str,
        content_attributes: Optional[Dict[str, Any]] = None,
        content_type: Optional[str] = None,
        message_type: Optional[str] = "outgoing",
        private: Optional[bool] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        assert message_type in ChatwootMessageTypes, f"message_type must be one of {ChatwootMessageTypes}"
        
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        log.debug(f"Sending message to Chatwoot url: {url}")

        payload = {
            'content': content,
            'content_attributes': content_attributes,
            'content_type': content_type,
            'message_type': message_type,
            'private': private
        }
        
        # set default headers
        headers = headers or {}
        headers.update({
            'api_access_token': self.access_key
        })
        
        
        # Remove keys with None values
        payload = {k: v for k, v in payload.items() if v is not None}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                response_data = await response.json()
                return response_data
            

    async def send_attachment(self, conversation_id, attach: ChatwootAttachment=None, text=None, is_private=False, content_attributes=None):
        assert isinstance(attach, ChatwootAttachment), "attach must be an instance of ChatwootAttachment"
        
        # Construct the URL
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        
        # Initialize the form data
        form = aiohttp.FormData()
        
        # Append the private flag
        form.add_field("private", "true" if is_private else "false")
        
        form.add_field("message_type", "outgoing")
        
        # Append the text content if provided
        if text:
            form.add_field("content", text)
                
        # Append the content attributes if provided
        # if content_attributes and 'items' in content_attributes:
        #     form.add_field("content_attributes", json.dumps(content_attributes or {}))
        #     form.add_field("content_type", "input_select")
        
        
        content = await self.__build_content(attach)
        buffer = base64.b64decode(content)
        file_type = filetype.guess(buffer)
        form.add_field("attachments[]", buffer, filename=attach.fileName or "audio.ogg", content_type=file_type.mime)
               
        
        # Make the HTTP request
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=form, headers=self.headers) as response:
                    res = await response.json()
                    print(res)
                    return res
            except aiohttp.ClientError as e:
                print(e)    




    
    
if __name__ == "__main__":
    
    import os
    #  load ogg file
    audio_content = None
    path = 'tests/data/sample.ogg'
    #  load file content
    with open(path, 'rb') as f:
        audio_content = f.read()
        
    
    
    b64_img = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII="
    conversation_id = 36
    
    client = ChatwootMessages(base_url=os.environ.get("CHATWOOT_URL"),
                            account_id=os.environ.get("CHATWOOT_ACCOUNT_ID"), 
                            access_key=os.environ.get("CHATWOOT_ACCESS_KEY"))
    
    async def send_image1():
        attach = ChatwootAttachment(type="image", content="https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg")
        await client.send_attachment(conversation_id=conversation_id, attach=attach, text="Hello", is_private=False)
        
    async def send_image_ba64():
        attach = ChatwootAttachment(type="image", content=b64_img, fileName="example.png")
        await client.send_attachment(conversation_id=conversation_id, attach=attach, is_private=False)  
        
    async def send_audio():
        attach = ChatwootAttachment(type="audio", 
                                    content=audio_content,
                                    fileName="sample.ogg")
        await client.send_attachment(conversation_id=conversation_id, attach=attach, is_private=False)
    
    async def send_input_select():
        content_type = "input_select"
        content_attributes = {
            "items": [
                { "title": "Option1", "value": "Option 1" },
                { "title": "Option2", "value": "Option 2" }
            ]
        }
        
        res = await client.send_text_message(conversation_id=conversation_id, 
                                       content="Hello, world!", 
                                       message_type="outgoing", 
                                       private=False,
                                       content_attributes=content_attributes,
                                       content_type=content_type)    
        
    async def send_article():
        content_type = "article"
       
        content_attributes = {
            "items": [
                { "title": "API start guide", "description": "A random start api guide", "link": "http://google.com" },
                { "title": "Development docs", "description": "Development docs and guidelines", "link": "http://google.com" }
            ]
        }        
        res = await client.send_text_message(conversation_id=conversation_id, 
                                       content="Hello, world!", 
                                       message_type="outgoing", 
                                       private=False,
                                       content_attributes=content_attributes,
                                       content_type=content_type)     
    
    async def send_cards():
        content_type = "cards"
        content_attributes = {
            "items":[
                {
                    "media_url":"https://assets.ajio.com/medias/sys_master/root/hdb/h9a/13582024212510/-1117Wx1400H-460345219-white-MODEL.jpg",
                    "title":"Nike Shoes 2.0",
                    "description":"Running with Nike Shoe 2.0",
                    "actions":[
                    {
                        "type":"link",
                        "text":"View More",
                        "uri":"google.com"
                    },
                    {
                        "type":"postback",
                        "text":"Add to cart",
                        "payload":"ITEM_SELECTED"
                    }
                    ]
                }
            ]            
        }
        
        res = await client.send_text_message(conversation_id=conversation_id, 
                                content="Hello, world!", 
                                message_type="outgoing", 
                                private=False,
                                content_attributes=content_attributes,
                                content_type=content_type)          
    
    
    # Example usage
    async def main():
        await send_image1()
        await send_image_ba64()
        await send_audio()
        pass

    # Run the example
    asyncio.run(main())
