# A2A Registry Go SDK

Go SDK for interacting with the A2A Agent Registry.

## Installation

```bash
go get github.com/a2areg/a2a-registry-sdk-go/pkg/a2areg
```

## Usage

### Basic Example

```go
package main

import (
    "fmt"
    "github.com/a2areg/a2a-registry-sdk-go/pkg/a2areg"
)

func main() {
    // Create client with API key
    client := a2areg.NewA2ARegClient(a2areg.A2ARegClientOptions{
        RegistryURL: "https://registry.example.com",
        APIKey:      "your-api-key",
    })

    // Get health status
    health, err := client.GetHealth()
    if err != nil {
        panic(err)
    }
    fmt.Println("Health:", health)

    // List agents
    agents, err := client.ListAgents(1, 20, true)
    if err != nil {
        panic(err)
    }
    fmt.Println("Agents:", agents)

    // Get specific agent
    agent, err := client.GetAgent("agent-id")
    if err != nil {
        panic(err)
    }
    fmt.Println("Agent:", agent.Name)
}
```

### OAuth Authentication

```go
client := a2areg.NewA2ARegClient(a2areg.A2ARegClientOptions{
    RegistryURL:  "https://registry.example.com",
    ClientID:     "your-client-id",
    ClientSecret: "your-client-secret",
    Scope:        "read write",
})

err := client.Authenticate()
if err != nil {
    panic(err)
}
```

### Publishing an Agent

```go
agent := &a2areg.Agent{
    Name:        "My Agent",
    Description: "A description of my agent",
    Version:     "1.0.0",
    Provider:    "my-org",
    IsPublic:    true,
    IsActive:    true,
}

published, err := client.PublishAgent(agent, true) // true = validate
if err != nil {
    panic(err)
}
fmt.Println("Published agent ID:", *published.ID)
```

## Testing

Run tests with:

```bash
go test ./...
```

