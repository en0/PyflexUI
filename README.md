# PyFlexUI

A Web UI for the PyFlex.

## Quick Start

Install python requirements

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start the webserver
```bash
flask --app webui.webapp run
```

## Unit Tests

Add the development requirements to your Python virtual environment.

```bash
pip install -r dev-requirements.txt
```

Run unittest

```bash
pytest
```

Optionally, run unittests on a file-watch.

```bash
ptw
```

## Developer Guide

The PyFlexUI is split into 3 different layers.

1. The Web UI and HTTP API.
2. The service layer.
3. The adapter layer.

### The Web UI/HTTP API

This module, located in the `/webui' directory contains all details related
to the HTTP and HTML.

#### webui.html

the `html` directory contains the HTML templates for the website. You can add
additional pages by copying `about.html` and changing it's content. 

The `layout.html` is a template which includes the `header.html`, `footer.html`, and
the currently requested page upon the time of request. You should not need to
make changes to the `layout.html` unless you want to affect the structure of the
entire website.

#### webui.services

This module contains functions to retrieve services from the service layer
located in the `/pyflex` directory.

#### webui.webapp

This module contains API endpoints and the page-request handlers. You should add
additional routes to this file to extend the API's functionality. You should not
need to add additional page-request handlers. See the `webui.html` module for
details.

#### webui.inputs

This folder holds files that have been uploaded to the webserver.

#### webui.outputs

This folder holds files to be downloaded by the user.

#### webui.resources

This folder contains other HTML resources such as javascript, css, and other
static content.

### PyFlex Adapters

This module, located in the `/adapters` directory contains code that is specific
to the way you have your pyflex wired up. This is a low-level boundary component
that might change depending on your setup.

This is a useful abstraction that will allow this code to run in many different
instances, including situations where it might not be running on the pyflex
hardware.

#### adapters.flashrom

This module contains a adapter to interact with the flashrom utility installed
on the server.

### Service Layer

This module, located in the `/pyflex` directory contains code that is specific
to the pyflex. Any systems that might be reused or even deployed with an
interface including, but not limited to the web UI. This module should contain
the majority of the logic that relates to interactiving with the pyflex
hardware.

#### pyflex.flashrom_service

This module defines a service that provides the ability to read and write ROMs
using the pyflex SPI bus.

#### pyflex.exceptions

This module contains exceptions to decouple the UI and adapter layers.

#### pyflex.models

This module contains data structures and DTOs for interacting with the service
layer.

#### pyflex.typing

This module contains typing interface on which the service layer depends.
