import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    print("A autenticar via OAuth 2.0 User Credentials para listagem...")
    
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

    try:
        drive_service = build('drive', 'v3', credentials=creds)

        print("A consultar ficheiros acessíveis...")
        response = drive_service.files().list(q="trashed=false", fields="files(id, name)").execute()
        files = response.get('files', [])

        if not files:
            print("O utilizador autenticado não tem acesso a NENHUM arquivo no Drive.")
        else:
            print(f"O utilizador autenticado tem acesso a {len(files)} ficheiro(s):")
            for f in files:
                print(f" - ID: {f.get('id')} | Nome: {f.get('name')}")

    except HttpError as error:
        print(f"ERRO API (Código {error.resp.status}): {error._get_reason()}")
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")

if __name__ == "__main__":
    main()
