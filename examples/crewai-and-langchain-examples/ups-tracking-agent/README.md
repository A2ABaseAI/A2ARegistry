# UPS Tracking Agent

A production-ready CrewAI agent that understands UPS shipments and can check delivery status for given UPS tracking numbers. Built with Python 3.11+, CrewAI, and comprehensive UPS API integration.

## Features

- **🤖 CrewAI Agent**: Expert UPS shipping agent with natural language understanding
- **📦 UPS API Integration**: Full OAuth authentication and tracking API support
- **🔍 Smart Tracking**: Handles single or multiple tracking numbers
- **📊 Normalized Data**: Clean, structured shipment status with actionable guidance
- **⚡ Fast CLI**: Direct tracking for pure tracking numbers, LLM for natural language
- **🛡️ Production Ready**: Error handling, retries, rate limiting, and comprehensive logging
- **🧪 Comprehensive Testing**: Full test coverage with mocked and real API tests

## Tech Stack

- **Python 3.11+**
- **CrewAI** - AI agent framework
- **httpx** - Async HTTP client for UPS API calls
- **pydantic** - Data validation and models
- **python-dotenv** - Environment configuration
- **typer** - CLI framework
- **rich** - Beautiful CLI output
- **pytest** - Testing framework

## Quick Start

### 1. Installation

```bash
cd examples/ups-tracking-agent
pip install -e .
```

### 2. Configuration

```bash
cp env.example .env
```

Edit `.env` with your UPS credentials:

```bash
# Required UPS API credentials
UPS_CLIENT_ID=your-ups-client-id
UPS_CLIENT_SECRET=your-ups-client-secret
UPS_ACCOUNT_NUMBER=your-ups-account-number

# Required OpenAI API key for CrewAI
OPENAI_API_KEY=sk-your-openai-api-key

# Optional: Use sandbox for testing
UPS_USE_SANDBOX=true
```

### 3. Usage

#### Basic Tracking
```bash
ups-agent "1Z999AA10123456784"
```

#### Multiple Tracking Numbers
```bash
ups-agent "1Z999AA10123456784 1Z888BB20234567895"
```

#### Natural Language Queries
```bash
ups-agent "Check the status of my UPS package 1Z999AA10123456784"
ups-agent "Where is my shipment going to San Francisco?"
```

#### JSON Output
```bash
ups-agent --json "1Z999AA10123456784"
```

#### Sandbox Mode
```bash
ups-agent --sandbox "1Z999AA10123456784"
```

#### Health Check
```bash
ups-agent health
```

## UPS API Setup

### 1. Create UPS Developer Account

1. Visit [UPS Developer Portal](https://developer.ups.com/)
2. Create an account and log in
3. Create a new application

### 2. Get API Credentials

1. **Client ID**: Found in your application dashboard
2. **Client Secret**: Generated when you create the application
3. **Account Number**: Your UPS account number (optional but recommended)

### 3. Required Permissions

Ensure your UPS application has these permissions:
- `Tracking` - Read access to tracking information
- `Address Validation` - Optional, for address validation

### 4. Sandbox vs Production

- **Sandbox**: Use `UPS_USE_SANDBOX=true` for testing
- **Production**: Use `UPS_USE_SANDBOX=false` for real tracking

## Agent Capabilities

### Status Understanding

The agent understands these UPS shipment statuses:

- **LABEL_CREATED**: Package label created, ready for pickup
- **IN_TRANSIT**: Package moving through UPS network
- **OUT_FOR_DELIVERY**: Package out for delivery today
- **DELIVERED**: Package successfully delivered
- **EXCEPTION**: Issue requiring attention
- **ON_HOLD**: Delivery on hold
- **PICKUP_AVAILABLE**: Available for pickup
- **CUSTOMS**: Processing through customs
- **UNKNOWN**: Status unclear

### Smart Features

- **Tracking Number Validation**: Validates UPS tracking number format
- **Staleness Detection**: Identifies packages with no movement for 48+ hours
- **Actionable Guidance**: Provides specific next steps for each status
- **PII Protection**: Logs never contain sensitive information
- **Rate Limiting**: Handles UPS API rate limits with exponential backoff
- **Error Recovery**: Graceful handling of network and API errors

## API Examples

### Python API Usage

```python
import asyncio
from ups_agent import UPSClient, UPSNormalizer, UPSStatusAgent

async def track_shipment():
    # Initialize client
    client = UPSClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        account_number="your_account"
    )
    
    # Initialize normalizer
    normalizer = UPSNormalizer()
    
    # Initialize agent
    agent = UPSStatusAgent(client=client, normalizer=normalizer)
    
    # Track shipment
    async with client:
        result = await agent.process_query("Track 1Z999AA10123456784")
        print(result)

# Run the example
asyncio.run(track_shipment())
```

### Direct Tracking (Bypass LLM)

```python
import asyncio
from ups_agent import UPSClient, UPSNormalizer

async def direct_tracking():
    client = UPSClient(
        client_id="your_client_id",
        client_secret="your_client_secret"
    )
    
    normalizer = UPSNormalizer()
    
    async with client:
        # Track directly
        ups_response = await client.track("1Z999AA10123456784")
        shipment_status = normalizer.normalize(ups_response)
        
        print(f"Status: {shipment_status.status_code}")
        print(f"Explanation: {shipment_status.explain()}")

asyncio.run(direct_tracking())
```

## Response Examples

### Natural Language Response
```
Your order 1Z999AA10123456784 was shipped on 2024-01-15 via UPS Ground. 
Tracking: 1Z999AA10123456784 → https://www.ups.com/track?trackingNumber=1Z999AA10123456784
Package is in transit at Louisville, KY. Estimated delivery: 2024-01-17 at 6:00 PM. 
Track regularly; contact UPS if no movement for 48+ hours.
```

### JSON Response
```json
[
  {
    "tracking_number": "1Z999AA10123456784",
    "status_code": "IN_TRANSIT",
    "status_text": "Package is in transit at Louisville, KY",
    "estimated_delivery": "2024-01-17T18:00:00",
    "delivered_at": null,
    "last_location": "Louisville, KY",
    "service": "UPS Ground",
    "weight": "5.0 LBS",
    "checkpoints": [
      {
        "timestamp": "2024-01-15T14:30:00",
        "location": "Louisville, KY",
        "description": "In Transit"
      }
    ]
  }
]
```

## Project Structure

```
ups-tracking-agent/
├── src/
│   └── ups_agent/
│       ├── __init__.py
│       ├── agent.py          # CrewAI agent implementation
│       ├── client.py         # UPS API client
│       ├── cli.py            # CLI interface
│       ├── config.py         # Configuration management
│       ├── models.py         # Pydantic models
│       └── normalizer.py     # Data normalization
├── tests/
│   ├── test_agent.py
│   ├── test_client_auth.py
│   ├── test_cli.py
│   └── test_normalization.py
├── pyproject.toml
├── env.example
└── README.md
```

## Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Categories
```bash
# Test normalization
pytest tests/test_normalization.py

# Test client authentication
pytest tests/test_client_auth.py

# Test CLI
pytest tests/test_cli.py
```

### Test with Coverage
```bash
pytest --cov=ups_agent tests/
```

## Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `UPS_CLIENT_ID` | - | UPS API client ID (required) |
| `UPS_CLIENT_SECRET` | - | UPS API client secret (required) |
| `UPS_ACCOUNT_NUMBER` | - | UPS account number (optional) |
| `UPS_API_BASE` | `https://onlinetools.ups.com` | UPS API base URL |
| `UPS_USE_SANDBOX` | `false` | Use UPS sandbox environment |
| `OPENAI_API_KEY` | - | OpenAI API key for CrewAI (required) |
| `CREWAI_MODEL` | `gpt-4o-mini` | CrewAI model |
| `CREWAI_TEMPERATURE` | `0.1` | CrewAI temperature |
| `DEBUG` | `false` | Debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |

## Error Handling

The agent handles various error scenarios:

- **Invalid Tracking Numbers**: Validates format and provides helpful error messages
- **API Authentication**: Clear error messages for credential issues
- **Network Errors**: Automatic retries with exponential backoff
- **Rate Limiting**: Handles UPS API rate limits gracefully
- **Not Found**: Clear messages for non-existent tracking numbers
- **Stale Packages**: Identifies packages with no movement for 48+ hours

## Production Deployment

### Environment Setup

1. **Set Production Values**:
   ```bash
   UPS_USE_SANDBOX=false
   DEBUG=false
   LOG_LEVEL=INFO
   ```

2. **Secure Credentials**: Use environment variables or secure secret management

3. **Monitoring**: Set up logging and monitoring for API calls

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

CMD ["ups-agent", "--help"]
```

### Health Monitoring

Use the health check command for monitoring:

```bash
ups-agent health
```

Returns:
- ✓ UPS credentials configured
- ✓ OpenAI credentials configured  
- ✓ UPS API connection successful

## Troubleshooting

### Common Issues

1. **"UPS_CLIENT_ID is required"**
   - Ensure UPS credentials are set in `.env` file
   - Check UPS Developer Portal for correct credentials

2. **"UPS API authentication failed"**
   - Verify client ID and secret are correct
   - Check if UPS application has tracking permissions

3. **"Tracking number not found"**
   - Verify tracking number format
   - Check if package exists in UPS system
   - Ensure tracking number is not too old

4. **"OpenAI API key required"**
   - Set `OPENAI_API_KEY` in `.env` file
   - Ensure OpenAI account has sufficient credits

### Debug Mode

Enable debug logging for troubleshooting:

```bash
ups-agent --debug "1Z999AA10123456784"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review UPS API documentation
- Open an issue in the repository
