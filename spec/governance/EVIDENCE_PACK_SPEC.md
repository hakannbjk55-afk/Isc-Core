
## Authoritative Byte Source

The `.tar` archive is the sole authoritative source of bytes for verification.

Verification implementations:

- MUST treat the archive byte stream as the canonical object.
- MUST compute integrity checks exclusively against bytes contained inside the archive.
- MUST NOT use any extracted workspace copy as an input to verification.
- MUST ignore modifications to extracted files that are not re-packed into the archive.

An extracted file is a non-authoritative representation.

A modified extracted copy that is not re-packed into the archive does not constitute tampering of the evidence pack.

Any tampering is defined strictly as a mutation of the authoritative archive byte stream.
