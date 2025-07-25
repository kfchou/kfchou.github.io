Sources:
1.  https://getindata.com/blog/deploying-serverless-mlflow-google-cloud-platform-using-cloud-run/ - MLFlow, Google OAuth2.0

> One of the most important aspects here is the use of the OAuth2-Proxy as a middle layer within the Cloud Run container. Using Cloud Run’s built-in authorization mechanism (“Require authentication. Manage authorized users with Cloud IAM.” option) is usable only when programmatic requests are being made. When interactive requests to the web based UI need to be made (like with the MLFlow web UI case), there is no built-in way yet to authenticate in the Cloud Run service.

Quickstart -- https://github.com/seandavi/fastapi-google-oauth-example/ -- uses `authlib.integrations.starlette_client`'s `OAuth` module.

OAuth App Demo - https://www.youtube.com/watch?v=n4e3Cy2Tq3Q -- a slightly more in-depth example, but uses `Flask`

Another OAuth APp Demo -- https://www.youtube.com/watch?v=dntaWShszR4

# Pre-configuring OAuth 2.0 Client
The Client ID / Client Secret can be created by visiting https://console.cloud.google.com/apis/credentials/oauthclient and configuring the new client as a Web Application as shown below. 

The authored Javascript Origin will be the domain name of your app. When developing locally, you can set it to `http://localhost:8080`

During pre-configuration, the **Authorized redirect URIs will be left blank. Later it will be filled with the URL of the deployed Cloud Run instance**. This is where users will be redirected to after they have been authenticated.

# Configure Secrets
Secret Manager
Click on to PERMISSIONS
Copy the service account that will have access to your app.
Click on to GRANT ACCESS
Add the service account as principal
Grant Role -> Secret Manager Secret Accessor

You'll see that the service account is now both an "editor" and "secret manager secret accessor"

# Attach the Secrets as Environment Variables
Now go to your deployed service
Click on "Edit and Deploy new version"
Click the "Container" tab, then the "Variables and secrets" tab. 
Use the "Add Variable" button to add new variables, modify existing ones by updating the values, and delete variables by clicking the trash icon.

# Finishing OAuth2.0 configuration
Once deployed, update *Authorized redirect URIs* with your app's deployed URI:
 https://mlflow-.a.run.app/oauth2/callback


```py
import os
import pathlib
from functools import wraps
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from authlib.integrations.starlette_client import OAuth

app = FastAPI(root_path="/auth")

# load environment variables
from dotenv import load_dotenv, find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # to allow Http traffic for local dev
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "../client_secret.json")

if GOOGLE_CLIENT_SECRET is None or GOOGLE_CLIENT_ID is None:
    raise ValueError("Please set the GOOGLE_CLIENT_SECRET and GOOGLE_CLIENT_ID environment variables.")

app.add_middleware(SessionMiddleware, secret_key=GOOGLE_CLIENT_SECRET)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

authorized_users = ["kennethfchou@gmail.com"]
def login_is_required(function):
    @wraps(function)
    async def wrapper(request: Request, *args, **kwargs):
        
        # Get the user info from the session
        user_info = request.session.get('user_info')
        user_email = user_info.get('email')
        if user_email not in authorized_users:
            raise HTTPException(status_code=401, detail="Authorization required")
        else:
            return await function(request, *args, **kwargs)

    return wrapper

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        print("TOKEN STRUCTURE:", token)
        print("TOKEN KEYS:", list(token.keys()))

        # Use userinfo endpoint instead of trying to parse id_token
        user_info = await oauth.google.userinfo(token=token)
        
        request.session['user_info'] = user_info
        
        print(request.session.keys())
        print("session.state:", request.session['state'])
        print("user email:", request.session['user_info']['email'])
        
        return RedirectResponse("/auth/protected_area")

    except Exception as e:
        print(f"Error in auth_callback: {e}")
        return {"error": str(e)}

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

@app.get("/")
async def index():
    return {"message": "Hello World", "login_url": "/login"}

@app.get("/protected_area")
@login_is_required
async def protected_area(request: Request):
    return {"message": f"Hello {request.session['user_info']['name']}!", "logout_url": "/logout"}
```
