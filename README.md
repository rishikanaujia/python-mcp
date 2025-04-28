# mcp-project
python-mcp/
│
├── README.md                        # Project overview and documentation
├── setup-mcp.sh                     # Setup script to create all files
├── requirements.txt                 # Main project dependencies
├── docker-compose.yml               # Docker configuration for all services
│
├── common/                          # Shared utilities across all components
│   ├── __init__.py
│   ├── protocol.py                  # MCP Protocol implementation
│   ├── logging_utils.py             # Logging utilities
│   └── error_handling.py            # Error handling utilities
│
├── client/                          # MCP Client implementation
│   ├── Dockerfile                   # Client container configuration
│   ├── requirements.txt             # Client-specific dependencies
│   ├── app.py                       # Main client application
│   ├── llm.py                       # LLM interface
│   ├── stdio_handler.py             # Standard I/O handler
│   ├── sse_client.py                # SSE client for notifications
│   ├── templates/                   # HTML templates
│   │   └── index.html               # Main client UI template
│   └── static/                      # Static assets
│       ├── styles.css               # CSS styles
│       └── client.js                # Client-side JavaScript
│
├── session_manager/                 # Session Manager implementation
│   ├── Dockerfile                   # Session manager container config
│   ├── requirements.txt             # Session manager dependencies
│   ├── app.py                       # Main session manager application
│   ├── dispatcher.py                # Request dispatcher
│   ├── session.py                   # Session management
│   └── notifications.py             # SSE notifications handler
│
├── servers/                         # MCP Servers implementation
│   │
│   ├── resources_server/            # Server 1: Resources
│   │   ├── Dockerfile               # Server container configuration
│   │   ├── requirements.txt         # Server dependencies
│   │   ├── app.py                   # Main server application
│   │   └── resources.py             # Resources implementation
│   │
│   ├── sampling_server/             # Server 2: Sampling
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── sampling.py              # Sampling implementation
│   │
│   ├── tools_server/                # Server 3: Tools
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── tools/                   # Tool implementations
│   │       ├── __init__.py
│   │       ├── calculator.py        # Calculator tool
│   │       ├── text_processor.py    # Text processor tool
│   │       └── data_transformer.py  # Data transformer tool
│   │
│   ├── database_server/             # Server 4: Database
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── database.py              # Database connector
│   │
│   ├── internet_server/             # Server 5: Internet
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── internet.py              # Internet connector
│   │
│   ├── roots_server/                # Server 6: Roots
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── roots.py                 # Roots implementation
│   │
│   └── prompts_server/              # Server 7: Prompts
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app.py
│       └── prompts.py               # Prompts implementation
│
└── docs/                            # Additional documentation
    ├── architecture.md              # Architecture details
    ├── api_reference.md             # API documentation
    ├── development_guide.md         # Development guidelines
    └── troubleshooting.md           # Troubleshooting guide