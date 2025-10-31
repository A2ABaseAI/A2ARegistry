# Shopify Status Agent

A production-ready LangChain + FastAPI application that provides a chat interface for tracking Shopify orders. The agent can answer "Where's my order?" style questions by querying the Shopify Admin API and returning shipment status and tracking links.

## Features

- **🤖 LangChain Agent**: Powered by OpenAI GPT models with conversation memory
- **🛍️ Shopify Integration**: Real-time order lookup via Shopify Admin API
- **💬 Chat Interface**: Clean, responsive web UI with streaming responses
- **🔒 Privacy Protection**: Automatic PII masking for emails and phone numbers
- **🧪 Mock Mode**: Built-in mock data for testing without Shopify API
- **📱 Responsive Design**: Works on desktop and mobile devices
- **⚡ Streaming**: Real-time response streaming with Server-Sent Events

## Tech Stack

- **Python 3.11+**
- **LangChain** - AI agent framework
- **FastAPI** - Web framework
- **OpenAI** - LLM provider (configurable)
- **httpx** - Async HTTP client for Shopify API
- **Pydantic** - Data validation
- **Jinja2** - HTML templating
- **Vanilla JavaScript** - Frontend with SSE streaming

## Quick Start

### 1. Clone and Setup

```bash
cd examples/shopify-status-agent
cp env.sample .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```bash
# Required for OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Shopify API (leave empty for mock mode)
SHOPIFY_SHOP=your-shop-name
SHOPIFY_ACCESS_TOKEN=shpat_your-shopify-access-token-here

# Application settings
MOCK_MODE=true  # Set to false for real Shopify API
DEBUG=true
```

### 3. Install Dependencies

```bash
pip install -e .
```

### 4. Run the Application

```bash
uvicorn app.server:app --reload
```

### 5. Open Chat Interface

Visit [http://localhost:8000](http://localhost:8000) in your browser.

## Usage Examples

### Chat Interface

Open the web interface and try these examples:

- "Where's my order #1001?"
- "Track order #1002 for customer@example.com"
- "What's the status of order #1003?"

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/healthz
```

#### Chat (Non-streaming)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Track order #1001 for customer@example.com"}'
```

#### Chat (Streaming)
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"message": "Where is my order #1001?"}'
```

## Mock Data

When `MOCK_MODE=true`, the agent uses these sample orders:

- **Order #1001**: Shipped with UPS tracking `1Z999AA1234567890`
- **Order #1002**: Processing (not yet shipped)
- **Order #1003**: Delivered with UPS tracking `1Z999BB9876543210`

## Shopify API Setup

To use with real Shopify data:

1. **Create a Private App** in your Shopify admin
2. **Enable Admin API access** with these permissions:
   - `read_orders`
   - `read_fulfillments`
3. **Get the access token** and update your `.env` file
4. **Set `MOCK_MODE=false`**

### Required Shopify Permissions

- `read_orders` - To fetch order information
- `read_fulfillments` - To get tracking information

## Project Structure

```
shopify-status-agent/
├── app/
│   ├── config.py          # Configuration management
│   ├── schemas.py          # Pydantic models
│   ├── server.py           # FastAPI application
│   ├── llm.py             # LLM configuration
│   ├── agent.py           # LangChain agent
│   ├── tools/
│   │   └── shopify.py     # Shopify API tools
│   ├── templates/
│   │   └── index.html     # Chat interface
│   └── static/
│       ├── app.js         # Frontend JavaScript
│       └── styles.css     # CSS styles
├── tests/
│   ├── test_shopify_tools.py
│   └── test_agent.py
├── pyproject.toml
├── env.sample
└── README.md
```

## Agent Capabilities

The LangChain agent can:

- **Find orders** by order number, email, or phone
- **Extract order status** (processing, shipped, delivered)
- **Provide tracking information** with carrier and tracking URLs
- **Mask PII** automatically (emails, phone numbers)
- **Handle multiple orders** and provide clear summaries
- **Ask for missing information** when needed

## Response Examples

### Shipped Order
> "Your order #1001 was **shipped** on 2024-01-12 via UPS. Tracking: 1Z999AA1234567890 → [Track Package](https://www.ups.com/track?trackingNumber=1Z999AA1234567890)"

### Processing Order
> "Your order #1002 is **processing**. We'll email you tracking once it ships."

### Order Not Found
> "I couldn't find an order with that information. Please check your order number or provide your email/phone."

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black app/ tests/
isort app/ tests/
```

### Type Checking

```bash
mypy app/
```

## Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `LLM_PROVIDER` | `openai` | LLM provider |
| `OPENAI_API_KEY` | - | OpenAI API key (required) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model |
| `OPENAI_TEMPERATURE` | `0.1` | Model temperature |
| `SHOPIFY_SHOP` | - | Shopify shop name |
| `SHOPIFY_API_VERSION` | `2024-07` | Shopify API version |
| `SHOPIFY_ACCESS_TOKEN` | - | Shopify access token |
| `MOCK_MODE` | `true` | Use mock data |
| `DEBUG` | `false` | Debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

## Security Features

- **PII Masking**: Automatically masks emails and phone numbers
- **Input Validation**: Pydantic schemas validate all inputs
- **Error Handling**: Graceful error handling with user-friendly messages
- **Rate Limiting**: Built-in session management and memory limits

## Production Deployment

### Environment Setup

1. Set `DEBUG=false`
2. Set `MOCK_MODE=false` (if using real Shopify)
3. Configure proper `SECRET_KEY`
4. Set up proper logging and monitoring

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Monitoring

The `/healthz` endpoint provides:
- Application status
- Mock mode indicator
- Shopify configuration status
- Timestamp

## Troubleshooting

### Common Issues

1. **OpenAI API Key**: Ensure `OPENAI_API_KEY` is set correctly
2. **Shopify API**: Check `SHOPIFY_SHOP` and `SHOPIFY_ACCESS_TOKEN`
3. **CORS Issues**: The app includes CORS middleware for development
4. **Memory Issues**: Sessions are stored in memory (consider Redis for production)

### Debug Mode

Set `DEBUG=true` to enable:
- Detailed error messages
- Request/response logging
- Development server reload

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
