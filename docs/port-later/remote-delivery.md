# Parked: remote image delivery

The proposed fetch changes are not active. Keep the existing PNG delivery
contract until an offline transport fixture proves all of the following:

- [ ] A request for a PNG cannot silently overwrite an existing JPEG or
  WebP with the same stem, even if it appears during transfer. Reject an
  alternate format before copying unless the caller approves the actual path.
- [ ] Validate the delivered bytes, extension and job-local receipts before
  publishing. Reject out-of-job paths and symlinks that escape the job.
- [ ] Accept regular files inside a job reached through a symlinked parent.
  Compare paths against the resolved job root.
- [ ] Protect the image, prompt and metadata as one delivery. Same-stem
  formats and concurrent publishers must not overwrite each other's receipts.
- [ ] Inject failures at each install step, including a directory at the
  metadata destination. Leave the complete prior set untouched, or no new
  files for a fresh destination. Never pair an old image with a new prompt.
