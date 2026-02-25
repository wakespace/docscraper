import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    print("A autenticar com a Service Account para listagem...")
    
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

    try:
        drive_service = build('drive', 'v3', credentials=creds)

        print("A consultar ficheiros acessíveis...")
        response = drive_service.files().list(q="trashed=false", fields="files(id, name)").execute()
        files = response.get('files', [])

        if not files:
            print("O robô não tem acesso a NENHUM arquivo no Drive.")
        else:
            print(f"O robô tem acesso a {len(files)} ficheiro(s):")
            for f in files:
                print(f" - ID: {f.get('id')} | Nome: {f.get('name')}")

    except HttpError as error:
        print(f"ERRO API (Código {error.resp.status}): {error._get_reason()}")
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")

if __name__ == "__main__":
    main()
