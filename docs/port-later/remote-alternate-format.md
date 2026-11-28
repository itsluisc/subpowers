# Parked: alternate-format remote fetch

Remote fetch is PNG-only. A job offering a JPEG or WebP is rejected before
copying its image or receipts; the requested output path is never substituted.

Different extensions with the same stem share the prompt and metadata paths.
Protecting only the image name cannot prevent one delivery from overwriting
another image's provenance. Before restoring alternate formats, give each
delivery unambiguous receipt ownership and test simultaneous publishers,
existing receipts, and failures installing either receipt. Publish the image
only after both receipts are installed.
