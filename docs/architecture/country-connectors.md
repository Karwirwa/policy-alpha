# Country Connectors

## Purpose

Country connectors provide a pluggable foundation for importing government documents from national data sources into the Policy Alpha Evidence Engine. They separate document discovery, download, parsing, and normalization from the evidence ingestion pipeline. Evidence generation remains the responsibility of the Evidence Engine.

## Architecture

Each connector implements a standardized document lifecycle with four responsibilities:

- `discover()`: identify available government documents.
- `download()`: retrieve raw document contents.
- `parse()`: extract raw structured information from a downloaded document.
- `normalize()`: convert parsed information into the platform's canonical `GovernmentDocument` format.

This interface is defined in `backend/app/connectors/base_connector.py`.

A shared `GovernmentConnector` implementation provides reusable connector infrastructure such as HTTP client initialization, retry and timeout configuration, logging hooks, download helpers, metadata normalization helpers, and connector health status.

Each connector also exposes a standardized `health()` interface for production monitoring. The health report is self-contained and does not execute external network requests.

The health report includes:

- `connector_name`
- `supported_country`
- `connector_version`
- `status`
- `last_successful_discovery`
- `last_successful_download`
- `capabilities`

Connector status values are currently expressed as placeholders and may include:

- `READY`
- `DISABLED`
- `MAINTENANCE`
- `NOT_IMPLEMENTED`

All connectors return `GovernmentDocument` objects so the Evidence Engine can consume normalized documents without depending on country-specific connector types.

## Connector implementations

Current placeholder connectors:

- `backend/app/connectors/government_connector.py`
- `backend/app/connectors/kenya_connector.py`
- `backend/app/connectors/us_connector.py`
- `backend/app/connectors/uk_connector.py`
- `backend/app/connectors/canada_connector.py`

Each connector currently exposes placeholder behavior only, with sample document references and stubbed metadata extraction.

## Adding a new country connector

To add a new country connector:

1. Create a new module under `backend/app/connectors/`, e.g. `nigeria_connector.py`.
2. Implement a class that inherits from `GovernmentConnector`.
3. Provide concrete implementations of `discover()`, `download()`, `parse()`, and `normalize()`.
4. Register the connector in `backend/app/connectors/__init__.py` if you want it to be discoverable through the package export list.

Each connector also exposes a `health()` method for production monitoring. The health report is intentionally self-contained and performs no external requests.

This approach keeps country-specific crawling logic outside the core Evidence Engine, so the engine itself does not need to change when new connectors are added.

## Future integration

A future connector registry or ingestion service can import each connector from `backend/app/connectors` and run the common interface methods. This keeps the Evidence Engine decoupled from source-specific download logic and enables adding new country connectors without modifying evidence extraction, entity resolution, or repository code.
