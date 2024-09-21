import base64
import json
import aiohttp
from typing import Any, Optional, Dict
from loguru import logger as log

ChatwootMessageTypes = ["incoming", "outgoing"]


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


    # -------------------------------------------------------------
    async def send_image_message(self, 
                                 conversation_id, 
                                 attach=None, 
                                 text=None, 
                                 is_private=False, 
                                 content_attributes=None):
        
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
        if content_attributes and 'items' in content_attributes:
            form.add_field("content_attributes", json.dumps(content_attributes or {}))
            form.add_field("content_type", "input_select")
        
        # Handle attachment based on type
        if attach and attach.get('type') == 'url':
            if not attach.get('fileUrl'):
                raise ValueError("Missing fileUrl")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(attach['fileUrl']) as response:
                    if response.status != 200:
                        raise ValueError("Failed to fetch the file from URL")
                    image_name = os.path.basename(attach['fileUrl'])
                    form.add_field("attachments[]", 
                                   await response.read(), 
                                   filename=image_name, 
                                   content_type="image")
        
        elif attach and attach.get('type') == 'b64':
            if not attach.get('content'):
                raise ValueError("Missing content")
            if not attach.get('fileName'):
                raise ValueError("Missing fileName")
            
            # Decode base64 content
            buffer = base64.b64decode(attach['content'])
            form.add_field("attachments[]",
                           buffer, 
                           filename=attach['fileName'], 
                           content_type="image")
        
        else:
            raise ValueError("Unknown attachment type")
        
        # Set up headers
        headers = {
            "api_access_token": f"{self.access_key}"
        }
        
        # Make the HTTP request
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=form, headers=headers) as response:
                    res = await response.json()
                    print(res)
                    return res
            except aiohttp.ClientError as e:
                print(e)    




if __name__ == "__main__":
    import asyncio
    import os
    
    b64_img = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII="
    
    async def main():
        
        client = ChatwootMessages(os.environ.get("CHATWOOT_URL"),
                                os.environ.get("CHATWOOT_ACCOUNT_ID"),
                                os.environ.get("CHATWOOT_ACCESS_KEY"))
       
        res = await client.send_text_message(conversation_id=34,
                                             content="Hello, world!",
                                             message_type="outgoing",
                                             private=False)
                     
                     
        attach = {
            "type": "url",
            "fileUrl": "https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg"
        }
        await client.send_image_message(conversation_id=35, attach=attach, text="Hello", is_private=False)

        
        attach = {
            "type": "b64",
            "content": b64_img,
            "fileName": "example.png"
        }
        await client.send_image_message(conversation_id=35, attach=attach, is_private=False)
                            
        
        print(res)
    
    
    asyncio.run(main())
