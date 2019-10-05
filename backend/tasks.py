"""Common tasks for Invoke."""
from invoke import task


@task(
    default=True,
    help={
        'development': 'run a development server'
    }
)
def runserver(ctx, development=False):
    """Run a uvicorn development server."""
    if development:
        ctx.run(
            'uvicorn yog_sothoth.app:app --reload',
            echo=True,
            pty=True,
            env={
                'YOG_DEVELOPMENT_MODE': 'true',
                'YOG_REDIS_HOST': '127.0.0.1',
                'YOG_ALLOWED_HOSTS': '127.0.0.1',
                'YOG_EMAIL_HOST': '127.0.0.1',
                'YOG_EMAIL_PORT': '8025',
                'YOG_EMAIL_SENDER_ADDRESS': 'yog_sothoth@localhost',
                'YOG_MANAGERS_ADDRESSES': 'yog_managers@localhost',
                'YOG_MATRIX_URL': 'http://127.0.0.1:8000/v1/matrix',
                'YOG_MATRIX_REGISTRATION_SHARED_SECRET': 'fakesecret',
            }
        )
    else:
        ctx.run('gunicorn --config yog_sothoth/conf/gunicorn.py yog_sothoth.app:app',
                echo=True)


@task
def lint(ctx):
    """Lint code and static analysis."""
    ctx.run('flake8 yog_sothoth/', echo=True)
    ctx.run('pydocstyle --explain yog_sothoth/', echo=True)
    ctx.run('bandit -i -r --exclude local_settings.py yog_sothoth/', echo=True)


@task
def lint_docker(ctx):
    """Lint Dockerfile."""
    ctx.run('sudo docker run --rm -i hadolint/hadolint < Dockerfile', echo=True,
            pty=True, echo_stdin=False)


@task
def redis(ctx):
    """Run a temporal Redis docker container."""
    ctx.run('sudo docker run --rm --network host redis:5-alpine', echo=True, pty=True,
            echo_stdin=False)


@task
def aiosmtpd(ctx):
    """Run a temporal email server for development."""
    ctx.run('python3 -m aiosmtpd -n', echo=True, pty=True,
            echo_stdin=False)


@task
def build(ctx, tag):
    """Build Yog-Sothoth API Docker image."""
    ctx.run(f'sudo docker build --build-arg APP_VERSION={tag} --compress --pull --rm '
            f'--tag registry.rlab.be/sysadmins/yog_sothoth:latest '
            f'--tag registry.rlab.be/sysadmins/yog_sothoth:{tag} .', echo=True, pty=True,
            echo_stdin=False)


@task
def clean(ctx):
    """Remove all temporary and compiled files."""
    remove = (
        'build',
        'dist',
        '*.egg-info',
        '.coverage',
        'cover',
        'htmlcov',
    )
    ctx.run(f'rm -vrf {" ".join(remove)}', echo=True)
    ctx.run('find . -type d -name "__pycache__" -exec rm -rf "{}" \\+', echo=True)
    ctx.run('find . -type f -name "*.pyc" -delete', echo=True)
