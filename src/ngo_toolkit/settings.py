from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_SHEETS_CREDENTIALS: dict # Google sheet credentials
    PUBLIC_SPREADSHEET_ID: str # The ID of the spreadsheet to update.
    RANKED_NGO_SHEET_NAME: str # The name of the ranked NGO result file.


    class Config:
        env_file = ".env"  # Specify the .env file
        env_file_encoding = "utf-8"

settings = Settings()