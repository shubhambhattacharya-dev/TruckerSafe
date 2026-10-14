# ADR-003: Combine weather risks by worst band

A checkpoint's final base band is the highest of its wind, rain, and snow bands. Load rules then upgrade wind risk. This conservative rule is deterministic and makes every displayed value reproducible in unit tests.
