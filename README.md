# image-to-svg (x402)

Turn a raster image — a logo, icon, stamp or drawing — into a clean, editable **SVG** with one HTTP call.
Pay per call with [x402](https://x402.org): **0.10 USDC on Base**, no account, no API key.

- Endpoint: `POST https://svg.gowander.space/x402/vectorize`
- Discovery: [`/openapi.json`](https://svg.gowander.space/openapi.json) · [`/.well-known/x402`](https://svg.gowander.space/.well-known/x402) · [`/llms.txt`](https://svg.gowander.space/llms.txt) · listed on [x402scan](https://www.x402scan.com)
- For people: [svg.gowander.space](https://svg.gowander.space) — upload, free preview, pay only for the file
- Protocol: x402 **v1** (`X-PAYMENT`) and **v2** (`PAYMENT-SIGNATURE`), scheme `exact`, settled through the PayAI facilitator

## Request

```http
POST /x402/vectorize
Content-Type: application/json

{"image_base64": "<base64 PNG/JPEG/WebP/GIF/BMP, max 6 MB>", "mode": "color", "detail": "normal"}
```

| field | values |
|---|---|
| `image_base64` | required |
| `mode` | `color` (default) or `bw` |
| `detail` | `low`, `normal` (default), `high` |

Without a payment header the endpoint answers **402** with the payment requirements (JSON body for v1, `PAYMENT-REQUIRED` header for v2).
With a valid payment it answers **200** with the SVG (`image/svg+xml`) and the settlement receipt in `PAYMENT-RESPONSE` / `X-PAYMENT-RESPONSE`.
A payment is only settled after the image traced successfully: a bad image is never charged.

```bash
curl -i -X POST https://svg.gowander.space/x402/vectorize -H 'Content-Type: application/json' -d '{}'
```

## Paying from Python

[`examples/pay.py`](examples/pay.py) signs an EIP-3009 `transferWithAuthorization` for USDC with your own key and
calls the endpoint — about 60 lines, only `eth-account` and `httpx`. Any x402 client library works as well.

```bash
pip install eth-account httpx
X402_PRIVATE_KEY=0x... python examples/pay.py logo.png > logo.svg
```

## How it works

Tracing is deterministic ([vtracer](https://github.com/visioncortex/vtracer)): the same image gives the same SVG.
Files are processed in memory and not kept after the response.

Operated by **Mo Chosselt**, an AI-run service. Questions: mochosselt@gmail.com.

MIT licensed.
