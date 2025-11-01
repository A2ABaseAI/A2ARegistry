# A2A Registry Java SDK

Java SDK for interacting with the A2A Agent Registry.

## Installation

### Maven

Add to your `pom.xml`:

```xml
<dependency>
    <groupId>com.a2areg</groupId>
    <artifactId>a2a-registry-sdk-java</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Gradle

```gradle
dependencies {
    implementation 'com.a2areg:a2a-registry-sdk-java:1.0.0'
}
```

## Usage

### Basic Example

```java
import com.a2areg.sdk.A2ARegClient;
import com.a2areg.sdk.exceptions.A2AError;

public class Example {
    public static void main(String[] args) {
        // Create client with API key
        A2ARegClient client = new A2ARegClient("https://registry.example.com", "your-api-key");

        try {
            // Get health status
            Map<String, Object> health = client.getHealth();
            System.out.println("Health: " + health);

            // List agents
            Map<String, Object> agents = client.listAgents(1, 20, true);
            System.out.println("Agents: " + agents);

            // Get specific agent
            Agent agent = client.getAgent("agent-id");
            System.out.println("Agent: " + agent.getName());
        } catch (A2AError e) {
            e.printStackTrace();
        }
    }
}
```

### OAuth Authentication

```java
A2ARegClient client = new A2ARegClient(
    "https://registry.example.com",
    "your-client-id",
    "your-client-secret"
);

try {
    client.authenticate();
} catch (AuthenticationError e) {
    e.printStackTrace();
}
```

### Publishing an Agent

```java
Agent agent = new Agent();
agent.setName("My Agent");
agent.setDescription("A description of my agent");
agent.setVersion("1.0.0");
agent.setProvider("my-org");
agent.setIsPublic(true);
agent.setIsActive(true);

try {
    Agent published = client.publishAgent(agent, true); // true = validate
    System.out.println("Published agent ID: " + published.getId());
} catch (A2AError e) {
    e.printStackTrace();
}
```

## Testing

Run tests with:

```bash
mvn test
```

