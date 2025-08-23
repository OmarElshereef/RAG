import os
from dotenv import load_dotenv
from supabase import create_client, Client


class SupabaseClient:
    _client: Client = None  

    @staticmethod
    def get_client() -> Client:
        if SupabaseClient._client is None:
            load_dotenv()
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")

            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

            SupabaseClient._client = create_client(url, key)

        return SupabaseClient._client
