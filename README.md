# Edutap Apple Passdata server

## Software Installation

enter the directry containing the software and run the following command

```bash
make install
```

## Usage

```bash
make run
```

## Testing

### unit tests
```bash
./venv/bin/pytest -m "not integration"
```

### integration tests
For these we need the real apple certificates and keys. They are not included in the repository for security reasons.
These tests create an apple pass and start the viewer for apple passes (runs only on OSX)
```bash
./venv/bin/pytest -m "integration"
```

## Configuration

### Certificates and Keys

Follow the instructions for [Apple Certificates](https://github.com/edutap-eu/edutap.models_apple#installation-cert-stuff).
Store the certificates and keys in the directory `certs` in the root directory of this project.

