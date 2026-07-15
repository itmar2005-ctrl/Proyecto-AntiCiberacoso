from setuptools import setup, find_packages

setup(
    name="purple-team",
    version="2.0.0",
    description="Professional Purple Team Cybersecurity Framework",
    author="Purple Team Security",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "purple-team=purple_team.__main__:main",
        ],
    },
    install_requires=[
        "cryptography>=41.0.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "full": [
            "flask>=2.3.0",
            "pillow>=10.0.0",
            "scapy>=2.5.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],
)
