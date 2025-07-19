# Gemini API Documentation
## Pricing and Rate Limits

### Overview
This document provides comprehensive information about Google's Gemini API pricing, rate limits, and usage tiers for basketball video analysis projects.

---

## Rate Limits Overview

Rate limits regulate the number of requests you can make to the Gemini API within a given timeframe. These limits help maintain fair usage, protect against abuse, and help maintain system performance for all users.

### How Rate Limits Work
Rate limits are measured across three dimensions:
- **Requests per minute (RPM)**
- **Requests per day (RPD)** 
- **Tokens per minute (input) (TPM)**

Your usage is evaluated against each limit, and exceeding any of them will trigger a rate limit error (HTTP 429).

**Important:** Rate limits are applied per project, not per API key.

---

## Usage Tiers

Rate limits are tied to the project's usage tier. As your API usage and spending increase, you'll have an option to upgrade to a higher tier with increased rate limits.

| Tier | Qualifications |
|------|---------------|
| **Free** | Users in eligible countries |
| **Tier 1** | Billing account linked to the project |
| **Tier 2** | Total spend: > $250 and at least 30 days since successful payment |
| **Tier 3** | Total spend: > $1,000 and at least 30 days since successful payment |

---

## Standard API Rate Limits

### Free Tier

| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| **Gemini 2.5 Pro** | 5 | 250,000 | 100 |
| **Gemini 2.5 Flash** | 10 | 250,000 | 250 |
| **Gemini 2.5 Flash-Lite Preview 06-17** | 15 | 250,000 | 1,000 |
| **Gemini 2.0 Flash** | 15 | 1,000,000 | 200 |
| **Gemini 2.0 Flash-Lite** | 30 | 1,000,000 | 200 |

### Tier 1

| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| **Gemini 2.5 Pro** | 5 | 250,000 | 100 |
| **Gemini 2.5 Flash** | 10 | 250,000 | 250 |
| **Gemini 2.5 Flash-Lite Preview 06-17** | 15 | 250,000 | 1,000 |
| **Gemini 2.0 Flash** | 15 | 1,000,000 | 200 |
| **Gemini 2.0 Flash-Lite** | 30 | 1,000,000 | 200 |

### Tier 2

| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| **Gemini 2.5 Pro** | 5 | 250,000 | 100 |
| **Gemini 2.5 Flash** | 10 | 250,000 | 250 |
| **Gemini 2.5 Flash-Lite Preview 06-17** | 15 | 250,000 | 1,000 |
| **Gemini 2.0 Flash** | 15 | 1,000,000 | 200 |
| **Gemini 2.0 Flash-Lite** | 30 | 1,000,000 | 200 |

### Tier 3

| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| **Gemini 2.5 Pro** | 5 | 250,000 | 100 |
| **Gemini 2.5 Flash** | 10 | 250,000 | 250 |
| **Gemini 2.5 Flash-Lite Preview 06-17** | 15 | 250,000 | 1,000 |
| **Gemini 2.0 Flash** | 15 | 1,000,000 | 200 |
| **Gemini 2.0 Flash-Lite** | 30 | 1,000,000 | 200 |

---

## Multi-modal Generation Models

| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| **Gemini 2.5 Flash Preview TTS** | 3 | 10,000 | 15 |
| **Gemini 2.5 Pro Preview TTS** | - | - | - |
| **Gemini 2.0 Flash Preview Image Generation** | 10 | 200,000 | 100 |

---

## Batch Mode Rate Limits

Batch Mode requests are subject to their own rate limits, separate from the non-batch mode API calls.

- **Concurrent batch requests:** 100
- **Input file size limit:** 2GB
- **File storage limit:** 20GB

---

## Pricing Information

### Free Tier
- **Gemini 2.5 Pro:** $0.0025 per 1M input tokens, $0.075 per 1M output tokens
- **Gemini 2.5 Flash:** $0.0005 per 1M input tokens, $0.015 per 1M output tokens
- **Gemini 2.0 Flash:** $0.0005 per 1M input tokens, $0.015 per 1M output tokens

### Paid Tiers
Pricing remains the same across tiers, but rate limits increase.

---

## Basketball Video Analysis Impact

### Current Project Usage
- **Model Used:** `gemini-2.0-flash-exp`
- **Rate Limit:** 10 requests per minute (Free Tier)
- **Issue Encountered:** Rate limit exceeded when processing 40 clips in parallel

### Solutions for Rate Limiting

#### 1. Batch Processing
```python
# Process clips in batches of 8-10
batch_size = 8
delay_between_batches = 60  # seconds
```

#### 2. Sequential Processing
```python
# Process one clip at a time
max_workers = 1
delay_between_requests = 6  # seconds (10 requests/minute)
```

#### 3. Model Switching
- **Gemini 2.5 Pro:** Higher rate limits but different output format
- **Gemini 2.0 Flash:** Better prompt following, lower rate limits
- **Gemini 2.0 Flash-Lite:** 30 RPM (3x higher than Flash)

#### 4. Tier Upgrades
- **Tier 1:** Requires billing account
- **Tier 2:** >$250 spend + 30 days
- **Tier 3:** >$1,000 spend + 30 days

---

## Error Handling

### Rate Limit Error (429)
```
429 You exceeded your current quota. Please migrate to Gemini 2.0 Flash 
Preview (Image Generation) (models/gemini-2.0-flash-preview-image-generation) 
for higher quota limits.
```

### Response Format
```json
{
  "violations": [{
    "quota_metric": "generativelanguage.googleapis.com/generate_requests_per_model",
    "quota_id": "GenerateRequestsPerMinutePerProjectPerModel",
    "quota_dimensions": {
      "key": "model",
      "value": "gemini-2.0-flash-exp"
    },
    "quota_value": 10
  }],
  "retry_delay": {
    "seconds": 27
  }
}
```

---

## Best Practices

### For Basketball Video Analysis
1. **Use Flash models** for consistent prompt following
2. **Implement batching** to avoid rate limits
3. **Add delays** between requests
4. **Monitor usage** to stay within limits
5. **Consider tier upgrades** for higher throughput

### Rate Limit Management
1. **Track request timing** to avoid bursts
2. **Implement exponential backoff** for retries
3. **Use different models** for different tasks
4. **Monitor quota usage** in Google Cloud Console

---

## Model Comparison for Video Analysis

| Model | RPM | Prompt Following | Output Format | Best For |
|-------|-----|------------------|---------------|----------|
| **Gemini 2.0 Flash** | 15 | Excellent | Plain text | Event timelines |
| **Gemini 2.5 Pro** | 5 | Good | JSON/Structured | Complex analysis |
| **Gemini 2.0 Flash-Lite** | 30 | Good | Plain text | High throughput |

---

## References
- [Official Gemini API Documentation](https://ai.google.dev/docs)
- [Rate Limits Guide](https://ai.google.dev/docs/rate_limits)
- [Pricing Information](https://ai.google.dev/pricing)
- [Model Comparison](https://ai.google.dev/models)

---

*Last updated: July 2024*
*For basketball video analysis project: A2/2_game_events* 