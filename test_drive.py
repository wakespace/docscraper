import os
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

# Preencha esta constante com o ID do ficheiro do Google Drive que deseja testar
TARGET_FILE_ID = "1gKhELT6DiS-5xSXFXxgReyeNITx1BqeS"

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    print("A autenticar com a Service Account...")
    
    creds_json_str = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not creds_json_str:
        print("ERRO: A variável de ambiente GOOGLE_CREDENTIALS_JSON não está definida.")
        return

    try:
        creds_info = json.loads(creds_json_str)
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=SCOPES)
    except Exception as e:
        print(f"ERRO: Falha ao interpretar as credenciais: {e}")
        return

    print(f"A tentar atualizar o ficheiro ID: {TARGET_FILE_ID}...")

    try:
        drive_service = build('drive', 'v3', credentials=creds)

        novo_conteudo = "Integração com o Google Drive a funcionar perfeitamente!"
        
        media = MediaIoBaseUpload(
            io.BytesIO(novo_conteudo.encode('utf-8')),
            mimetype='text/plain',
            resumable=True
        )

        drive_service.files().update(
            fileId=TARGET_FILE_ID,
            media_body=media
        ).execute()

        print("SUCESSO: Ficheiro atualizado no Google Drive!")

    except HttpError as error:
        print(f"ERRO API (Código {error.resp.status}): {error._get_reason()}")
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")

if __name__ == "__main__":
    main()
