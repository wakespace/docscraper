import os
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

# Preencha esta constante com o ID do ficheiro do Google Drive que deseja testar
TARGET_FILE_ID = "1gKhELT6DiS-5xSXFXxgReyeNITx1BqeS"

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    print("A autenticar via OAuth 2.0 User Credentials...")
    
    client_id = os.environ.get('GCP_CLIENT_ID')
    client_secret = os.environ.get('GCP_CLIENT_SECRET')
    refresh_token = os.environ.get('GCP_REFRESH_TOKEN')

    if not all([client_id, client_secret, refresh_token]):
        print("ERRO: As variáveis GCP_CLIENT_ID, GCP_CLIENT_SECRET, ou GCP_REFRESH_TOKEN não estão definidas.")
        return

    try:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret
        )
    except Exception as e:
        print(f"ERRO: Falha ao interpretar as credenciais: {e}")
        return

    print(f"A tentar atualizar o ficheiro ID: {TARGET_FILE_ID}...")

    try:
        drive_service = build('drive', 'v3', credentials=creds)

        novo_conteudo = "Integração via OAuth 2.0 com o Google Drive a funcionar perfeitamente!"
        
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
