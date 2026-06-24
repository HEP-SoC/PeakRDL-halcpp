import os
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()


with open(os.path.join("src/peakrdl_halcpp", "__about__.py"), encoding='utf-8') as f:
    v_dict = {}
    exec(f.read(), v_dict)
    version = v_dict['__version__']

setuptools.setup(
    name="peakrdl_halcpp",
    version=version,
    author="Risto Pejasinovic",
    author_email="risto.pejasinovic@gmail.com",
    description="Generate CPP Hardware Abstraction Layer libraries",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/Risto97/PeakRDL-halcpp",
    package_dir={'': 'src'},
    packages=setuptools.find_packages("src"),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        "systemrdl-compiler>=1.25.0",
        "Jinja2>=3.0.0",
        "peakrdl>=1.1.0",
    ],
    entry_points = {
        "peakrdl.exporters": [
            'halcpp = peakrdl_halcpp.__peakrdl__:Exporter'
        ]
    },
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: Software Development :: Documentation",
    ),
    project_urls={
        "Source": "https://github.com/Risto97/PeakRDL-halcpp",
        "Tracker": "https://github.com/Risto97/PeakRDL-halcpp/issues",
    },
)
