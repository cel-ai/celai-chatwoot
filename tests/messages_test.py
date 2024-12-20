import json
import pytest
from cel.gateway.model.conversation_lead import ConversationLead
from celai_chatwoot.connector.model import WootLead
from celai_chatwoot.connector.model.woot_attachment import WootAttachment, WootLocationAttachment
from celai_chatwoot.connector.model.woot_message import WootMessage
from cel.gateway.model.base_connector import BaseConnector



@pytest.fixture
def msg() -> str:
    with open('./tests/data/incoming_text_msg_from_web.json') as f:
        message = json.load(f)
        return message
    
@pytest.fixture
def msg_img() -> str:
    with open('./tests/data/incoming_img_msg_from_web.json') as f:
        message = json.load(f)
        return message
    
@pytest.fixture
def msg_audio_from_tg() -> str:
        with open('./tests/data/incoming_audio_msg_tg.json') as f:
            message = json.load(f)
            return message

@pytest.fixture
def msg_location_from_tg() -> str:
    with open('./tests/data/incoming_location_tg.json') as f:
        message = json.load(f)
        return message

@pytest.fixture
def msg_file_from_tg() -> str:
    with open('./tests/data/incoming_file_msg_tg.json') as f:
        message = json.load(f)
        return message
    

@pytest.mark.asyncio
async def test_lead_parsing(msg):
    
    lead = WootLead.from_chatwoot_message(msg)
    
    assert isinstance(lead, WootLead)
    assert isinstance(lead, ConversationLead)
    
    assert lead.account_id == '8'
    assert lead.inbox_id == '211'
    assert lead.conversation_id == '33'
    assert lead.metadata['event'] == 'message_created'
    assert lead.metadata['message_type'] == 'incoming'
    assert lead.metadata['private'] == False
    assert lead.connector_name == None
    assert lead.conversation_from.name == 'cold-wind-258'
    assert lead.conversation_from.id == '5094'
    assert lead.conversation_from.email == 'foo@bar.com'
    assert lead.conversation_from.phone == '123456'
    
    
@pytest.mark.asyncio
async def test_message_parsing(msg):
    wootmsg = await WootMessage.load_from_message(msg)
    
    assert isinstance(wootmsg, WootMessage)
    assert wootmsg.text == 'asd'
    assert wootmsg.date == 1725664428
    
    
    
@pytest.mark.asyncio
async def test_message_with_img_parsing(msg_img):
    wootmsg = await WootMessage.load_from_message(msg_img)
    
    assert isinstance(wootmsg, WootMessage)
    assert wootmsg.text == None or wootmsg.text == ''
    assert wootmsg.date == 1725664594
    
    # "attachments": [
    #     {
    #         "id": 11529,
    #         "message_id": 436117,
    #         "file_type": "image",
    #         "account_id": 8,
    #         "extension": null,
    #         "data_url": "https://chatwoot.celai.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBbG91IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--1a8d1d96c0630370245a7f741b16990c82c4e3bb/ale1.jpg",
    #         "thumb_url": "https://chatwoot.celai.com/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBbG91IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--1a8d1d96c0630370245a7f741b16990c82c4e3bb/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdCem9MWm05eWJXRjBTU0lJYW5CbkJqb0dSVlE2RTNKbGMybDZaVjkwYjE5bWFXeHNXd2RwQWZvdyIsImV4cCI6bnVsbCwicHVyIjoidmFyaWF0aW9uIn19--27ede0471899a6e40b40ba7e4525adebc0ea198f/ale1.jpg",
    #         "file_size": 160813
    #     }
    # ],    

    assert len(wootmsg.attachments) == 1
    attach = wootmsg.attachments[0]
    assert isinstance(attach, WootAttachment)
    # assert attach.title == None
    assert attach.title == "Image"
    assert attach.mimeType == 'image/jpeg'
    assert attach.file_url == 'https://chatwoot.celai.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBbG91IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--1a8d1d96c0630370245a7f741b16990c82c4e3bb/ale1.jpg'
    assert attach.thumb_url == 'https://chatwoot.celai.com/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBbG91IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--1a8d1d96c0630370245a7f741b16990c82c4e3bb/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdCem9MWm05eWJXRjBTU0lJYW5CbkJqb0dSVlE2RTNKbGMybDZaVjkwYjE5bWFXeHNXd2RwQWZvdyIsImV4cCI6bnVsbCwicHVyIjoidmFyaWF0aW9uIn19--27ede0471899a6e40b40ba7e4525adebc0ea198f/ale1.jpg'
    

@pytest.mark.asyncio
async def test_message_with_audio_parsing(msg_audio_from_tg):
    wootmsg = await WootMessage.load_from_message(msg_audio_from_tg)
    
    assert isinstance(wootmsg, WootMessage)
    assert wootmsg.text == None or wootmsg.text == ''
    assert wootmsg.date == 1726894319

    # Audio attachment    
    # "id": 15183,
    # "message_id": 595489,
    # "file_type": "audio",
    # "account_id": 8,
    # "extension": null,
    # "data_url": "https://chatwoot.celai.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBcGc4IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--ced19bdedff4a7da3eee55e466fe5bc1506d0832/file_1.oga",
    # "thumb_url": "",
    # "file_size": 4062   

    assert len(wootmsg.attachments) == 1
    attach = wootmsg.attachments[0]
    assert isinstance(attach, WootAttachment)
    assert attach.title == "file_1.oga"
    assert attach.mimeType == 'audio/ogg'
    assert attach.file_url == 'https://chatwoot.celai.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBcGc4IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--ced19bdedff4a7da3eee55e466fe5bc1506d0832/file_1.oga'



@pytest.mark.asyncio
async def test_message_with_location_parsing(msg_location_from_tg):
    wootmsg = await WootMessage.load_from_message(msg_location_from_tg)
    
    assert isinstance(wootmsg, WootMessage)
    assert wootmsg.text == None or wootmsg.text == ''
    assert wootmsg.date == 1726894902

    # "id": 15184,
    # "message_id": 595490,
    # "file_type": "location",
    # "account_id": 8,
    # "coordinates_lat": -34.574992,
    # "coordinates_long": -58.502302,
    # "fallback_title": null,
    # "data_url": null 

    assert len(wootmsg.attachments) == 1
    attach = wootmsg.attachments[0]
    assert isinstance(attach, WootLocationAttachment)
    assert attach.type == 'location'
    assert attach.latitude == -34.574992
    assert attach.longitude == -58.502302
    
    
@pytest.mark.asyncio
async def test_message_file_pdf(msg_file_from_tg):
    wootmsg = await WootMessage.load_from_message(msg_file_from_tg)
    
    assert isinstance(wootmsg, WootMessage)
    assert wootmsg.text == 'sample pdf for testing'
    assert wootmsg.date == 1726895312

    # "id": 15185,
    # "message_id": 595520,
    # "file_type": "file",
    # "account_id": 8,
    # "extension": null,
    # "data_url": "https://chatwoot.celai.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBcGs4IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--67392c158ee9d2e382c576d70eaba10ca95c786e/file_2.pdf",
    # "thumb_url": "",
    # "file_size": 18810 

    assert len(wootmsg.attachments) == 1
    attach = wootmsg.attachments[0]
    assert isinstance(attach, WootAttachment)
    
    assert attach.title == "file_2.pdf"
    assert attach.mimeType == 'application/pdf'
    assert attach.file_url == 'https://chatwoot.celai.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBcGs4IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--67392c158ee9d2e382c576d70eaba10ca95c786e/file_2.pdf'