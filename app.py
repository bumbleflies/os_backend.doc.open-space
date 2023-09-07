import os

import uvicorn as uvicorn

if __name__ == '__main__':
    reload = os.getenv('OS_FRONTEND_RELOAD', False)
    app = os.getenv('OS_FRONTEND_APP', "api.routes:app")
    port = os.getenv('OS_FRONTEND_PORT', 5000)
    uvicorn.run(app, host='0.0.0.0', port=port, reload=reload)
