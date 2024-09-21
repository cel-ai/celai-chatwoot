import mimetypes
from cel.gateway.model.attachment import FileAttachment,\
                                        LocationAttachment,\
                                        MessageAttachmentType

class WootLocationAttachment(LocationAttachment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

                                                
class WootAttachment(FileAttachment):
    
    def __init__(self, 
                 title: str = None, 
                 description: str = None, 
                 mimeType: str = None,
                 thumb_url: str = None,
                 file_url: str = None, 
                 metadata: any = None, 
                 type: MessageAttachmentType = None):
        
        super().__init__(
            title=title, 
            description=description, 
            content=None, 
            mimeType=mimeType, 
            file_url=file_url, 
            metadata=metadata, 
            type=type)
        
        self.thumb_url = thumb_url
        
    
    def __str__(self):
        return f"WootAttachment: {self.title}"
    
    def __repr__(self):
        return f"WootAttachment: {self.title}"
    
    
    @classmethod
    async def load_from_message(cls, message: dict) -> list:
        attachs = message.get("attachments")
        if not attachs:
            return None
        
        response = []
        
        for attach in attachs:
            # check if the message has a photo
            if attach["file_type"] == 'image':
                response.append(await cls.load_image_from_message(attach))
            if attach["file_type"] == 'audio':
                response.append(await cls.load_audio_from_message(attach))
            if attach["file_type"] == 'location':
                response.append(await cls.load_location_from_message(attach))
            if attach["file_type"] == 'file':
                response.append(await cls.load_file_from_message(attach))
            if attach["file_type"] == 'video':
                response.append(await cls.load_video_from_message(attach))
        
        return response
        

    # Sample message with image attachment from Chatwoot
    # "id": 11529,
    # "message_id": 436117,
    # "file_type": "image",
    # "account_id": 8,
    # "extension": null,
    # "data_url": "https://chatwoot.celai.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBbG91IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--1a8d1d96c0630370245a7f741b16990c82c4e3bb/ale1.jpg",
    # "thumb_url": "https://chatwoot.celai.com/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBbG91IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--1a8d1d96c0630370245a7f741b16990c82c4e3bb/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdCem9MWm05eWJXRjBTU0lJYW5CbkJqb0dSVlE2RTNKbGMybDZaVjkwYjE5bWFXeHNXd2RwQWZvdyIsImV4cCI6bnVsbCwicHVyIjoidmFyaWF0aW9uIn19--27ede0471899a6e40b40ba7e4525adebc0ea198f/ale1.jpg",
    # "file_size": 160813
    @classmethod
    async def load_image_from_message(cls, attach: dict):
        
        return WootAttachment(
            title="Image",
            description="Image attachment",
            mimeType=mimetypes.guess_type(attach["data_url"])[0],
            metadata=attach,
            thumb_url=attach["thumb_url"],
            file_url=attach["data_url"],
            type=MessageAttachmentType.IMAGE
        )
        
       
    #  Sample audio message from Chatwoot
    # "id": 207,
    # "message_id": 2467,
    # "file_type": "audio",
    # "account_id": 4,
    # "extension": null,
    # "data_url": "https://chatwoot.com/rails/asd.oga"
    # "thumb_url": "",
    # "file_size": 7989
    @classmethod
    async def load_audio_from_message(cls, attach: dict):
        filename = attach["data_url"].split("/")[-1]
        return WootAttachment(
            title=filename,
            description="Audio attachment",
            mimeType=mimetypes.guess_type(attach["data_url"])[0],
            metadata=attach,
            file_url=attach["data_url"],
            type=MessageAttachmentType.AUDIO
        )
    
    
    #  Sample location message from Chatwoot
    # "id": 15184,
    # "message_id": 595490,
    # "file_type": "location",
    # "account_id": 8,
    # "coordinates_lat": -34.574992,
    # "coordinates_long": -58.502302,
    # "fallback_title": null,
    # "data_url": null
    @classmethod
    async def load_location_from_message(cls, attach: dict):
        return WootLocationAttachment(
            latitude=attach["coordinates_lat"],
            longitude=attach["coordinates_long"],
            metadata=attach,
            description="Location attachment")
    
    # "id": 15185,
    # "message_id": 595520,
    # "file_type": "file",
    # "account_id": 8,
    # "extension": null,
    # "data_url": "https://chatwoot.celai.com/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBcGs4IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--67392c158ee9d2e382c576d70eaba10ca95c786e/file_2.pdf",
    # "thumb_url": "",
    # "file_size": 18810    
    @classmethod
    async def load_file_from_message(cls, attach: dict):
        filename = attach["data_url"].split("/")[-1]
        return WootAttachment(
            title=filename,
            description="File attachment",
            mimeType=mimetypes.guess_type(attach["data_url"])[0],
            metadata=attach,
            file_url=attach["data_url"],
            type=MessageAttachmentType.DOCUMENT
        )
    
    
    @classmethod
    async def load_video_from_message(cls, attach: dict):
        raise NotImplementedError("Video attachment not implemented")