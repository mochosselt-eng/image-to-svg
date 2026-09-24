"""Pay https://svg.gowander.space/x402/vectorize with x402 (v1, scheme "exact",
USDC on Base) and print the SVG.

    pip install eth-account httpx
    X402_PRIVATE_KEY=0x... python pay.py logo.png > logo.svg

The key only signs an EIP-3009 transferWithAuthorization for the exact price
to the address in the 402 challenge; nothing else is ever signed.
"""
import base64
import json
import os
import secrets
import sys
import time

import httpx
from eth_account import Account

URL = os.environ.get("X402_URL", "https://svg.gowander.space/x402/vectorize")
CHAIN_IDS = {"base": 8453, "base-sepolia": 84532}


def main(path: str) -> None:
    body = {"image_base64": base64.b64encode(open(path, "rb").read()).decode(), "mode": "color"}
    with httpx.Client(timeout=120) as client:
        challenge = client.post(URL, json=body)
        if challenge.status_code != 402:
            sys.exit(f"expected 402, got {challenge.status_code}: {challenge.text[:200]}")
        req = challenge.json()["accepts"][0]

        account = Account.from_key(os.environ["X402_PRIVATE_KEY"])
        now = int(time.time())
        auth = {"from": account.address, "to": req["payTo"], "value": int(req["maxAmountRequired"]),
                "validAfter": now - 60, "validBefore": now + int(req.get("maxTimeoutSeconds", 120)),
                "nonce": "0x" + secrets.token_hex(32)}
        signed = Account.sign_typed_data(
            account.key,
            domain_data={"name": req["extra"]["name"], "version": req["extra"]["version"],
                         "chainId": CHAIN_IDS[req["network"]], "verifyingContract": req["asset"]},
            message_types={"TransferWithAuthorization": [
                {"name": "from", "type": "address"}, {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"}, {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"}, {"name": "nonce", "type": "bytes32"}]},
            message_data=auth)
        payment = {"x402Version": 1, "scheme": "exact", "network": req["network"],
                   "payload": {"signature": "0x" + signed.signature.hex().removeprefix("0x"),
                               "authorization": {k: str(v) for k, v in auth.items()}}}
        header = base64.b64encode(json.dumps(payment).encode()).decode()

        paid = client.post(URL, json=body, headers={"X-PAYMENT": header})
        if paid.status_code != 200:
            sys.exit(f"payment not accepted ({paid.status_code}): {paid.text[:300]}")
        receipt = json.loads(base64.b64decode(paid.headers["X-PAYMENT-RESPONSE"]))
        print(f"paid: {receipt.get('transaction')}", file=sys.stderr)
        sys.stdout.write(paid.text)


if __name__ == "__main__":
    main(sys.argv[1])
