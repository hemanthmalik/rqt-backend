from quart import Quart
from db import sa_connection

def create_app(**config_overrides):
    app = Quart(__name__)
    app.config.from_pyfile("settings.py")
    app.config.update(config_overrides)

    from counter.views import counter_app
    app.register_blueprint(counter_app)

    @app.before_serving
    async def create_db_connection():
        print("Starting app")
        app.sac = await sa_connection()

    @app.after_serving
    async def close_db_connection():
        print("closing down app")
        await app.sac.close()

    return app