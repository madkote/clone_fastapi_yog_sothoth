"""Yog-Sothoth: small app for self-registration to Matrix homeserver."""
import uvicorn

if __name__ == '__main__':
    print('Running development server...')
    uvicorn.run('yog_sothoth.app:app', host='127.0.0.1', port=8000, reload=True)
