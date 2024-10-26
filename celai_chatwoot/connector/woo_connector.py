import asyncio
import json
from typing import Any, Dict
from urllib.parse import urljoin
from loguru import logger as log
from fastapi import APIRouter, BackgroundTasks
from loguru import logger as log
import shortuuid
from cel.comms.utils import async_run
from cel.gateway.model.base_connector import BaseConnector
from cel.gateway.message_gateway import StreamMode
from cel.gateway.model.message_gateway_context import MessageGatewayContext
from cel.gateway.model.outgoing import OutgoingMessage,\
                                            OutgoingMessageType,\
                                            OutgoingLinkMessage,\
                                            OutgoingSelectMessage,\
                                            OutgoingTextMessage

from celai_chatwoot.connector.model.woot_lead import WootLead
from celai_chatwoot.connector.model.woot_message import WootMessage
from celai_chatwoot.connector.msg_utils import ChatwootMessages, ChatwootAttachment
from .bot_utils import ChatwootAgentsBots





class WootConnector(BaseConnector):
       
    def __init__(self,
                 bot_name: str,
                 account_id: str,
                 access_key: str,
                 chatwoot_url: str,
                 inbox_id: str,
                 bot_description: str = "Celai Bot",
                 stream_mode: StreamMode = StreamMode.SENTENCE):
        log.debug("Creating Chatwoot connector")

        self.router = APIRouter(prefix="/chatwoot")
        self.paused = False
        
        # generate shortuuid for security token
        self.security_token = shortuuid.uuid()
        self.__create_routes(self.router)
        self.stream_mode = stream_mode
        
        # Chatwoot configuration
        self.bot_name = bot_name
        self.account_id = account_id
        self.access_key = access_key
        self.inbox_id = inbox_id
        self.chatwoot_url = chatwoot_url
        self.bot_description = bot_description or "Celai generated Bot"
        

    def __create_routes(self, router: APIRouter):
                
        @router.post(f"/webhook/{self.security_token}")
        async def telegram_webhook(payload: Dict[Any, Any], background_tasks: BackgroundTasks):
 
            background_tasks.add_task(self.__process_message, payload)
            return {"status": "ok"}

    async def __process_message(self, payload: dict):
        log.debug(f"Processing Chatwoot request {payload}")
        
        if self.paused:
            log.warning("Chatwoot connector is paused, ignoring message")
            return         
        
        try:
            log.debug("Received Chatwoot request")
            # log.debug(payload)

            if payload.get("message_type", "outgoing") == "outgoing":
                log.debug("Ignoring outgoing message")
                return
            
            msg = await WootMessage.load_from_message(payload, connector=self)
            
            has_attachments = msg.attachments is not None and len(msg.attachments) > 0
            if has_attachments:
                log.debug(f"Received message with attachments: {msg.attachments}")
            
            assert isinstance(msg, WootMessage), "msg must be an instance of WootMessage"
            
            
            # Process message through the gateway
            if self.gateway:
                async for m in self.gateway.process_message(msg, mode=self.stream_mode):
                    pass            
                
        except Exception as e:
            log.error(f"Error processing chatwoot incoming request to webhook: {e}")


    async def send_select_message(self, 
                                  lead: WootLead, 
                                  text: str, 
                                  options: list[str], 
                                  metadata: dict = {}, 
                                  is_partial: bool = True):
        # TODO: send select message to chatwoot
        log.warning("Chatwoot send select message is not implemented yet")


    async def send_link_message(self, 
                                lead: WootLead, 
                                text: str, 
                                links: list, 
                                metadata: dict = {}, 
                                is_partial: bool = True):

        # TODO: send link message to chatwoot
        log.warning("Chatwoot send link message is not implemented yet")



    async def send_message(self, message: OutgoingMessage):
        assert isinstance(message, OutgoingMessage),\
            "message must be an instance of OutgoingMessage"
        assert isinstance(message.lead, WootLead),\
            "lead must be an instance of TelegramLead"
        lead = message.lead
        
        if message.type == OutgoingMessageType.TEXT:
            assert isinstance(message, OutgoingTextMessage),\
            "message must be an instance of OutgoingMessage"
            await self.send_text_message(lead, 
                                         message.content, 
                                         metadata=message.metadata, 
                                         is_partial=message.is_partial)
            
        if message.type == OutgoingMessageType.SELECT:
            assert isinstance(message, OutgoingSelectMessage),\
            "message must be an instance of OutgoingSelectMessage"
            
            await self.send_select_message(lead, 
                                           message.content, 
                                           options=message.options, 
                                           metadata=message.metadata, 
                                           is_partial=message.is_partial)

        if message.type == OutgoingMessageType.LINK:
            assert isinstance(message, OutgoingLinkMessage),\
            "message must be an instance of OutgoingLinkMessage"
            
            await self.send_link_message(lead, 
                                           message.content, 
                                           url=message.links, 
                                           metadata=message.metadata, 
                                           is_partial=message.is_partial)
        


    async def send_text_message(self, lead: WootLead, text: str, metadata: dict = {}, is_partial: bool = True):
        """ Send a text message to the lead. The simplest way to send a message to the lead.
        
        Args:
            - lead[WootLead]: The lead to send the message
            - text[str]: The text to send
            - metadata[dict]: Metadata to send with the message
            - is_partial[bool]: If the message is partial or not
        """        
        
        is_private = (metadata or {}).get("private", False)
        
        log.debug(f"Sending message to Chatwoot acc: {lead.account_id}, inbox: {lead.inbox_id}, conv: {lead.conversation_id}, private:{is_private}, text: {text}")   
        client = ChatwootMessages(base_url=self.chatwoot_url,
                                  account_id=lead.account_id,
                                  access_key=self.access_key)
            
        await client.send_text_message(conversation_id=lead.conversation_id,
                                       content=text,
                                       content_attributes=metadata,
                                       message_type="outgoing",
                                       private=is_private)
        
        
    async def send_typing_action(self, lead: WootLead):    
        log.warning("Chatwoot typing action is not implemented yet")
        
        
        
    async def send_image_message(self, 
                                 lead: WootLead, 
                                 image: Any, 
                                 filename:str, 
                                 caption:str = None, 
                                 metadata: dict = {}, 
                                 is_partial: bool = True):
        
        client = ChatwootMessages(base_url=self.chatwoot_url,
                                  account_id=lead.account_id,
                                  access_key=self.access_key)
        
        is_private = (metadata or {}).get("private", False)
              
        attach = ChatwootAttachment(type="image", 
                                    content=image, 
                                    fileName=filename)
        
        await client.send_attachment(conversation_id=lead.conversation_id,
                                     attach=attach,
                                     text=caption,
                                     is_private=is_private)
        
    async def send_audio_message(self, 
                                 lead: WootLead, 
                                 content: Any, 
                                 filename:str=None,
                                 caption:str = None, 
                                 metadata: dict = {}):
        
        client = ChatwootMessages(base_url=self.chatwoot_url,
                                  account_id=lead.account_id,
                                  access_key=self.access_key)
        
        is_private = (metadata or {}).get("private", False)
        attach = ChatwootAttachment(type="audio",
                                    content=content, 
                                    fileName=filename)
        
        await client.send_attachment(conversation_id=lead.conversation_id,
                                     attach=attach,
                                     text=caption,
                                     is_private=is_private)
                                 


    def name(self) -> str:
        return "telegram"
        
    def get_router(self) -> APIRouter:
        return self.router
    
    def set_gateway(self, gateway):
        from cel.gateway.message_gateway import MessageGateway
        assert isinstance(gateway, MessageGateway), \
            "gateway must be an instance of MessageGateway"
        self.gateway = gateway
    
    def startup(self, context: MessageGatewayContext):
        # verify if the webhook_url is set and is HTTPS
        assert context.webhook_url, "webhook_url must be set in the context"
        assert context.webhook_url.startswith("https"),\
            (f"webhook_url must be HTTPS, got: {context.webhook_url}"
            "Be sure that your url is public and has a valid SSL certificate.")
        
        async def update_bot():
            try:
                base_url = f"{context.webhook_url}"
                webhook_url = urljoin(base_url, f"{self.router.prefix}/webhook/{self.security_token}")
                
                log.debug(f"Updating Chatwoot Bot webhook url to: {webhook_url}")

                client = ChatwootAgentsBots(
                    base_url=self.chatwoot_url,
                    account_id=self.account_id,
                    access_key=self.access_key
                )
                
                bot = await client.upsert_bot(name=self.bot_name,
                                            outgoing_url=webhook_url,
                                            description=self.bot_description)
                               
                bot_id = bot["id"]
                log.debug(f"Chatwoot Bot '{self.bot_name}' id:{bot_id} updated. Adding bot to inbox {self.inbox_id}")
                await client.assign_bot_to_inbox(inbox_id=self.inbox_id, agent_bot_id=bot_id)
                log.debug(f"Chatwoot Bot '{self.bot_name}' assigned to inbox {self.inbox_id}")
                
            except Exception as e:
                log.error(f"Error updating Chatwoot bot: {e}")
                log.exception(e)
                raise e
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(update_bot())
        except RuntimeError:
            # If no loop is running, use asyncio.run()
            asyncio.run(update_bot())        
        
    
    def shutdown(self, context: MessageGatewayContext):
        log.debug("Shutting down Chatwoot connector")
        # TODO: remove chatwoot webhook url
        
        
    def pause(self):
        log.debug("Pausing Chatwoot connector")
        self.paused = True
    
    def resume(self):
        log.debug("Resuming Chatwoot connector")
        self.paused = False
