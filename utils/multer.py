
from fastapi import  UploadFile
from database.supabase_client import SupabaseClient

STORAGE_BUCKET = "images"

supabase = SupabaseClient().get_client()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}

async def upload_to_supabase_storage(file:UploadFile) -> str:
    """Upload file to Supabase storage and return public URL"""
    try:
        if not validate_image_file(file):
            raise 

        file_path = f"images/{file.filename}" 

        # Read the file content
        file_content = await file.read()

        # Upload the file to Supabase Storage
        supabase.storage.from_("images").upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        
        public_url_response =  supabase.storage.from_("images").get_public_url(file_path)
        return public_url_response        
    except Exception as e:
        raise Exception(f"Failed to upload to Supabase: {str(e)}")



def validate_image_file(file: UploadFile) -> bool:
    """Validate uploaded image file"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return False
    return True
