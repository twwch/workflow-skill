# HTTP Request (`http-request`)

## Purpose
Make HTTP requests to external APIs with configurable method, headers, parameters, body, authentication, and timeout.

## Core Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `method` | `Method` | Yes | HTTP method: `get`, `post`, `head`, `patch`, `put`, `delete` |
| `url` | `string` | Yes | The request URL (supports variable interpolation) |
| `headers` | `string` | Yes | Request headers as a newline-separated `key:value` string |
| `params` | `string` | Yes | Query parameters as a newline-separated `key:value` string |
| `body` | `Body` | Yes | Request body configuration |
| `authorization` | `Authorization` | Yes | Authentication configuration |
| `timeout` | `Timeout` | No | Timeout settings for connect, read, write |

## Full Schema

### HttpNodeType (extends CommonNodeType)

```typescript
{
  // --- CommonNodeType fields ---
  title: string                    // Display name of the node
  desc: string                     // Description of the node
  type: 'http-request'             // BlockEnum.HttpRequest

  // --- HTTP-specific fields ---
  variables: Variable[]            // Input variable mappings
  method: Method                   // HTTP method
  url: string                      // Request URL
  headers: string                  // Headers as key:value lines
  params: string                   // Query params as key:value lines
  body: Body                       // Request body
  authorization: Authorization     // Auth configuration
  timeout: Timeout                 // Timeout settings
  ssl_verify?: boolean             // Whether to verify SSL certificates (default: true)

  // --- Optional CommonNodeType fields ---
  error_strategy?: ErrorHandleTypeEnum
  retry_config?: {
    retry_enabled: boolean
    max_retries: number
    retry_interval: number
  }
}
```

### Method (enum)
| Value | Description |
|-------|-------------|
| `get` | HTTP GET |
| `post` | HTTP POST |
| `head` | HTTP HEAD |
| `patch` | HTTP PATCH |
| `put` | HTTP PUT |
| `delete` | HTTP DELETE |

### Body
```typescript
{
  type: BodyType       // Body encoding type
  data: BodyPayload    // Body content (string form is deprecated)
}
```

### BodyType (enum)
| Value | Description |
|-------|-------------|
| `none` | No body |
| `form-data` | Multipart form data |
| `x-www-form-urlencoded` | URL-encoded form |
| `raw-text` | Raw text body |
| `json` | JSON body |
| `binary` | Binary file upload |

### BodyPayload
An array of payload entries:
```typescript
{
  id?: string                  // Optional unique identifier
  key?: string                 // Field name (for form types)
  type: BodyPayloadValueType   // 'text' or 'file'
  file?: ValueSelector         // File reference when type is 'file' (string[])
  value?: string               // Text content when type is 'text'
}[]
```

### Authorization
```typescript
{
  type: AuthorizationType      // 'no-auth' or 'api-key'
  config?: {
    type: APIType              // 'basic', 'bearer', or 'custom'
    api_key: string            // The API key or token value
    header?: string            // Custom header name (when APIType is 'custom')
  } | null
}
```

### AuthorizationType (enum)
| Value | Description |
|-------|-------------|
| `no-auth` | No authentication |
| `api-key` | API key authentication |

### APIType (enum)
| Value | Description |
|-------|-------------|
| `basic` | Basic authentication |
| `bearer` | Bearer token |
| `custom` | Custom header-based auth |

### Timeout
```typescript
{
  connect?: number              // Connection timeout in ms
  read?: number                 // Read timeout in ms
  write?: number                // Write timeout in ms
  max_connect_timeout?: number  // Max connection timeout boundary
  max_read_timeout?: number     // Max read timeout boundary
  max_write_timeout?: number    // Max write timeout boundary
}
```

### Variable
```typescript
{
  variable: string            // Variable name used in URL/headers/params/body interpolation
  value_selector: string[]    // Reference path: [nodeId, ...keyPath]
  value_type?: VarType        // Optional type hint
  required?: boolean          // Whether the variable is required
}
```

## Variable Reference Rules

**Inputs:** Variables defined in the `variables` array can be interpolated into `url`, `headers`, `params`, and `body` fields using template syntax (e.g., `{{#nodeId.variable#}}`). Each variable maps to an upstream node output via `value_selector`.

**Outputs:** The HTTP Request node produces the following output variables for downstream consumption:
- `body` (string) -- response body text
- `status_code` (number) -- HTTP status code
- `headers` (object) -- response headers

Downstream nodes reference these as `[thisNodeId, "body"]`, etc.

## Default Values
```json
{
  "variables": [],
  "method": "get",
  "url": "",
  "authorization": {
    "type": "no-auth",
    "config": null
  },
  "headers": "",
  "params": "",
  "body": {
    "type": "none",
    "data": []
  },
  "ssl_verify": true,
  "timeout": {
    "max_connect_timeout": 0,
    "max_read_timeout": 0,
    "max_write_timeout": 0
  },
  "retry_config": {
    "retry_enabled": true,
    "max_retries": 3,
    "retry_interval": 100
  }
}
```

## Validation Rules
- `url` must be non-empty
- When `body.type` is `binary`, the first entry in `body.data` must have a non-empty `file` reference

## Example Snippet

```yaml
- data:
    title: Call API
    desc: Fetch data from external API
    type: http-request
    method: get
    url: "https://api.example.com/data?q={{#start_node_id.query#}}"
    headers: "Content-Type:application/json"
    params: ""
    body:
      type: none
      data: []
    authorization:
      type: no-auth
      config: null
    timeout:
      max_connect_timeout: 0
      max_read_timeout: 0
      max_write_timeout: 0
    ssl_verify: true
    variables:
      - variable: query
        value_selector:
          - "start_node_id"
          - query
  id: http-node-1
  position:
    x: 400
    y: 200
```
