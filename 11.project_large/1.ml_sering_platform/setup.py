from setuptools import setup, find_packages

setup(
    name="ml_serving_platform",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "aiofiles",
        "python-dotenv",
        "requests",
        "numpy",
        "pandas",
        "scikit-learn",
        "torch",
        "transformers"
    ],
) 