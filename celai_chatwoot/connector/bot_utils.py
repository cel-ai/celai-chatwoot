from typing import Optional, Dict
from loguru import logger as log    
import aiohttp
from typing import Any, Dict, Optional

class ChatwootAgentsBots:
    
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

    async def list_agent_bots(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/agent_bots"
        log.debug(f"Listing agent bots from Chatwoot url: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response_data = await response.json()
                return response_data

    async def create_agent_bot(self,
                                name: Optional[str] = None,
                                description: Optional[str] = None,
                                outgoing_url: Optional[str] = None
                            ) -> Dict[str, Any]:
        
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/agent_bots"
        log.debug(f"Creating agent bot at Chatwoot url: {url}")

        payload = {
            'name': name,
            'description': description,
            'outgoing_url': outgoing_url
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                response_data = await response.json()
                return response_data

    async def delete_agent_bot(self, agent_bot_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/agent_bots/{agent_bot_id}"
        log.debug(f"Deleting agent bot from Chatwoot url: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.headers) as response:
                response_data = await response.json()
                return response_data

    async def get_agent_bot(self, agent_bot_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/agent_bots/{agent_bot_id}"
        log.debug(f"Getting agent bot from Chatwoot url: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response_data = await response.json()
                return response_data


    async def update_agent_bot(self,
                                agent_bot_id: str,
                                name: Optional[str],
                                description: Optional[str] = None,
                                outgoing_url: Optional[str] = None) -> Dict[str, Any]:
        
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/agent_bots/{agent_bot_id}"
        log.debug(f"Updating agent bot at Chatwoot url: {url}")

        payload = {
            'name': name,
            'description': description,
            'outgoing_url': outgoing_url
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, json=payload, headers=self.headers) as response:
                response_data = await response.json()
                return response_data



    async def find_agent_bot_by_name(self,name: str):
        
        bots = await self.list_agent_bots()
        bot = next((bot for bot in bots if bot["name"] == name), None)
        return bot


    async def upsert_bot(self,
                        name: Optional[str] = None,
                        description: Optional[str] = None,
                        outgoing_url: Optional[str] = None):
        bot = await self.find_agent_bot_by_name(name)
        
        if bot:
            bot_id = bot["id"]
            log.debug(f"Bot '{name}' id:{bot_id} found. Updating bot with webhook url {outgoing_url}")
            return await self.update_agent_bot(bot_id, name, description, outgoing_url)
            
        log.warning(f"Bot '{name}' not found. Creating bot with webhook url {outgoing_url}")
        return await self.create_agent_bot(name, description, outgoing_url)
        
        
    # add bot to inbox https://app.chatwoot.com/api/v1/accounts/{account_id}/inboxes/{id}/set_agent_bot
    async def assign_bot_to_inbox(self, inbox_id: str | int, agent_bot_id: str | int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/inboxes/{inbox_id}/set_agent_bot"
        log.debug(f"Adding bot to inbox at Chatwoot url: {url}")

        payload = {
            'agent_bot': agent_bot_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                response_data = await response.json()
                return response_data



if __name__ == "__main__":
    
    import asyncio
    import os

    async def main():
        
        client = ChatwootAgentsBots(
            base_url=os.environ.get("CHATWOOT_URL"),
            account_id=os.environ.get("CHATWOOT_ACCOUNT_ID"),
            access_key=os.environ.get("CHATWOOT_ACCESS_KEY")
        )

        bot_name = "Testing Ale Bot"
        bot_desc = "This is a test bot"
        
        # Upsert bot
        res = await client.upsert_bot(
            name=bot_name,
            description=bot_desc,
            outgoing_url="https://alebot.ngrok.io/webhook"
        )
        log.debug(f"Bot created or updated: {res}")
        
        #  check if the bot was created or updated
        bot = await client.find_agent_bot_by_name(
            name=bot_name
        )
        
        # find bot by name
        log.debug(f"Bot found: {bot}")
        
        bot_id = bot["id"]
        
        # list bots
        bots = await client.list_agent_bots()
        log.debug(f"Bots: {bots}")
        
        for b in bots:
            #  show id, name, description
            log.debug(f"Bot: {b['id']} {b['name']} {b['description']}")
            
        # assign bot to inbox 
        inbox_id = 1
        bot_id = 1
        await client.assign_bot_to_inbox(inbox_id, bot_id)

        print("Done!")

    asyncio.run(main())
