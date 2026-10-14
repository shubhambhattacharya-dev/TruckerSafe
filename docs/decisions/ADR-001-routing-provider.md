# ADR-001: Use OSRM for route alternatives

Use OSRM through an adapter because it is key-free and returns road geometry, distance, duration, and alternatives. The adapter prevents OSRM-specific payloads from reaching business logic. OSRM may return fewer alternatives than requested; the app never fabricates routes.
