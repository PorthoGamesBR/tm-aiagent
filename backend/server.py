from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from bootstrap import Application

class Server:
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        app.state.application = Application()
        yield
        
    async def health(self):
        return {"status": "ok"}

    
    def create_app(self):
        self.app = FastAPI(
            lifespan=self.lifespan
        )
        self.app.mount(
            "/",
            StaticFiles(directory="./front", html=True),
            name="static"
        )
        self.app.get("/health")(self.health)
        return self.app

server = Server()
app = server.create_app()