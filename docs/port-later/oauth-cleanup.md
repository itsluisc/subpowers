# Parked: isolated-profile OAuth cleanup

The painter retains its baseline behavior. Do not reintroduce the cleanup
change until offline tests with a stub painter and synthetic login prove:

- [ ] Remove only the temporary credential, including on early probe failure,
  successful delivery and failed receipt installation. A kept diagnostics
  directory must not retain it. Leave the original login unchanged.
- [ ] Exercise cleanup failure **after** the painter has produced an image:
  make the temporary credential directory read-only. The parked change
  returned **1** before the no-retry handler was installed. The dispatcher
  interprets 1 as permission to try another painter.
- [ ] Fail closed on that cleanup error, return **5** (painted, not
  delivered), and do not claim delivery. Exercise the dispatcher with a
  counted fallback stub: one paint, zero fallbacks. A paid paint must
  never be repeated, even if cleanup or delivery fails.
- [ ] Use no real login, provider calls or identifying diagnostics in tests.
