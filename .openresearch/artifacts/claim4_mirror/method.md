# Claim 4 route 2: dataset transport calibration

The parent route showed that the Toronto-hosted CIFAR-10 archive transfer
dominated a 30-minute execution window. This child changes only the transport
URL to a Hugging Face CDN mirror. Torchvision still enforces the original
archive MD5 `c58f30108f718f92721af3b95e74349a`, and the verifier independently
records and checks that digest before accepting the regenerated numerical
payload.

The fixed command, Python lock, model, initialization, permutation, batch size,
reference examples, error examples, estimator, bootstrap, and controls remain
unchanged. The previously accepted committed evidence is checked first by the
cumulative runner.
