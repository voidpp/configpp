#!/bin/bash

sphinx-apidoc -f -o docs/source configpp

sphinx-build -b html docs/source/ docs/build/
