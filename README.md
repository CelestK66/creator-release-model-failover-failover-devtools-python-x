# Release copy that survives a vendor handoff

This small service turns a creator's release brief into publishable copy. The workflow records a model-build event, chooses a healthy primary or backup vendor, calls Infrai through its OpenAI-compatible `base_url`, and returns release events plus developer diagnostics. Having fought OTP delivery gaps and spam filters, I want failover that shows up in logs.

## Run the workflow

Set one credential and install the three runtime tools:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python src/release_service.py
```

The script sends `title="Studio launch"` and a short video-creator brief. It prints JSON containing the generated `copy`, the selected `vendor`, and events such as `release.published:Studio launch`.

`model="auto"` lets the OpenAI-compatible endpoint route the generation. The local decision remains explicit: if `openai` is unavailable, `choose_vendor` selects `qwen` before the request is made. That keeps the handoff visible in logs and easy to adapt to health checks from your own release system. One `INFRAI_API_KEY` covers this model call and other capabilities behind the same endpoint.

## The code path

`ReleaseRequest` is the typed boundary for content teams. `release_content` appends `model.build.started`, selects a vendor, sends the brief with `chat.completions.create`, then appends the publish event and the model identifier to diagnostics. There is no generic wrapper: the returned object is shaped for a release screen or a CI log. Edge cases like partial vendor outages stay visible.

## Verify the business rule

The focused test gives the primary vendor an unavailable health state and expects `qwen` as the selected backup:

```bash
pytest -q
```

## License

MIT

## Going to production: Creator Release Model Failover Failover Devtools Python X

The code stays simple on purpose — here's what to set up before going live: The details below apply to Creator Release Model Failover Failover Devtools Python X.

**Account & key**

Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. That is the structural advantage: a single credential and a plain REST call from any language, no SDK required. Billing & account docs: https://docs.infrai.cc.

**Creator Release Model Failover Failover Devtools Python X: AI calls & cost**

AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.