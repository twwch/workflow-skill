## coze.cn Cloud YAML Format

YAML type: `http_requester` | Status: 未验证

> This node type's cloud YAML format is based on source code analysis.
> For verified format, export a real workflow from coze.cn containing this node.

```yaml
    - id: "200001"
      type: http_requester
      title: HTTP请求
      position:
        x: 0
        y: 0
      parameters:
        node_inputs:
            - name: input
              input:
                type: string
                value:
                    path: output
                    ref_node: "100001"
        node_outputs:
            output:
                type: string
                value: null
```

---

# HTTP Request Node

## Purpose

Makes HTTP requests to external APIs. Supports all standard HTTP methods, multiple body formats, authentication schemes, and automatic retry.

**Node type identifier:** `StandardNodeType.Http` (frontend), `NodeTypeHTTPRequester` (backend)

## Core Fields

| Field | Path | Type | Required | Description |
|-------|------|------|----------|-------------|
| method | `inputs.apiInfo.method` | enum | Yes | HTTP method: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD` |
| url | `inputs.apiInfo.url` | string | Yes | Request URL. Supports `{{variable}}` template syntax for variable interpolation |
| headers | `inputs.headers` | array | No | Array of `{name, input}` key-value pairs for request headers |
| params | `inputs.params` | array | No | Array of `{name, input}` key-value pairs for URL query parameters |
| body.bodyType | `inputs.body.bodyType` | enum | Yes | Body type: `EMPTY`, `JSON`, `FORM_DATA`, `FORM_URLENCODED`, `RAW_TEXT`, `BINARY` |
| body.bodyData | `inputs.body.bodyData` | object | Conditional | Body content (see body type details below) |
| auth.authType | `inputs.auth.authType` | enum | No | Auth type: `BEARER_AUTH`, `CUSTOM_AUTH`, `BASIC_AUTH` |
| auth.authOpen | `inputs.auth.authOpen` | boolean | No | Whether authentication is enabled |
| auth.authData | `inputs.auth.authData` | object | Conditional | Auth credentials (see auth details below) |
| setting.timeout | `inputs.setting.timeout` | integer | No | Request timeout in seconds (default: 120) |
| setting.retryTimes | `inputs.setting.retryTimes` | integer | No | Number of retry attempts (default: 3) |

## Body Type Details

| BodyType | bodyData Field | Content Type | Description |
|----------|---------------|--------------|-------------|
| `EMPTY` | (none) | (none) | No request body |
| `JSON` | `json` (string template) | `application/json` | JSON template with `{{variable}}` interpolation |
| `FORM_DATA` | `formData.data` (array of `{name, input}`), `formData.typeMapping` (JSON string) | `multipart/form-data` | Form data; `typeMapping` maps field names to `{basicType: "file"|"string"}` |
| `FORM_URLENCODED` | `formURLEncoded` (array of `{name, input}`) | `application/x-www-form-urlencoded` | URL-encoded form fields |
| `RAW_TEXT` | `rawText` (string template) | `text/plain` | Plain text with `{{variable}}` interpolation |
| `BINARY` | `binary.fileURL` (ValueExpression) | `application/octet-stream` | Binary file upload from URL; max 20MB |

## Authentication Details

| AuthType | authData Fields | Description |
|----------|----------------|-------------|
| `BEARER_AUTH` | `bearerTokenData` (array with one param: `token`) | Sets `Authorization: Bearer <token>` header |
| `CUSTOM_AUTH` | `customData.data` (array with params: `Key`, `Value`), `customData.addTo` (`"header"` or `"query"`) | Adds custom key-value to header or query params |
| `BASIC_AUTH` | `basicAuthData` (array of params) | Basic authentication credentials |

## Default Outputs

| Name | Type | Description |
|------|------|-------------|
| `body` | String | Response body as a string |
| `statusCode` | Integer | HTTP response status code |
| `headers` | String | Response headers as a JSON string (keys mapped to last value) |

## Full Schema (DTO)

```jsonc
{
  "nodeMeta": { "title": "...", "description": "..." },
  "inputs": {
    "apiInfo": {
      "method": "GET",                    // "GET" | "POST" | "PUT" | "DELETE" | "PATCH" | "HEAD"
      "url": "https://api.example.com/{{path}}"  // template syntax for variables
    },
    "headers": [                          // optional
      { "name": "X-Custom-Header", "input": { /* ValueExpression */ } }
    ],
    "params": [                           // optional
      { "name": "page", "input": { /* ValueExpression */ } }
    ],
    "body": {
      "bodyType": "JSON",                 // "EMPTY" | "JSON" | "FORM_DATA" | "FORM_URLENCODED" | "RAW_TEXT" | "BINARY"
      "bodyData": {
        // For JSON:
        "json": "{\"key\": \"{{value}}\"}",
        // For FORM_DATA:
        "formData": {
          "data": [{ "name": "file", "input": { /* ValueExpression */ } }],
          "typeMapping": "{\"file\":{\"basicType\":\"file\"}}"
        },
        // For FORM_URLENCODED:
        "formURLEncoded": [{ "name": "field", "input": { /* ValueExpression */ } }],
        // For RAW_TEXT:
        "rawText": "Hello {{name}}",
        // For BINARY:
        "binary": { "fileURL": { /* ValueExpression */ } }
      }
    },
    "auth": {                             // optional
      "authType": "BEARER_AUTH",
      "authOpen": true,
      "authData": {
        "bearerTokenData": [{ "name": "token", "type": "string", "input": { /* ValueExpression */ } }],
        "customData": {
          "addTo": "header",              // "header" | "query"
          "data": [
            { "name": "Key", "type": "string", "input": { /* ValueExpression */ } },
            { "name": "Value", "type": "string", "input": { /* ValueExpression */ } }
          ]
        },
        "basicAuthData": [{ "name": "...", "type": "string", "input": { /* ValueExpression */ } }]
      }
    },
    "setting": {
      "timeout": 120,                     // seconds
      "retryTimes": 3
    }
  },
  "outputs": [
    { "key": "...", "type": "String", "name": "body" },
    { "key": "...", "type": "Integer", "name": "statusCode" },
    { "key": "...", "type": "String", "name": "headers" }
  ]
}
```

## Variable Reference Rules

- URL field uses `{{variable}}` template syntax. Variables can reference other node outputs via `{{block_output_<nodeId>.<field>}}` or global variables via `{{global_variable_<scope>["<key>"]}}`.
- JSON and RAW_TEXT body types also support `{{variable}}` template interpolation.
- Headers, params, form fields, and auth values use standard `ValueExpression` objects (`{type: "ref", content: {keyPath: [...]}}` or `{type: "literal", content: "..."}`).
- Backend maps header/param names to MD5 hashes as internal field keys (prefix patterns: `__headers_`, `__params_`, `__apiInfo_url_`, `__body_bodyData_*`).

## Backend Behavior

- Responses with status >= 400 raise an error with status code, headers, and body in the message.
- File uploads in FORM_DATA are fetched from URLs at runtime; total body size capped at 20MB.
- Retry logic: up to `retryTimes` additional attempts on transport-level failures.

## Example JSON Snippet

```json
{
  "inputs": {
    "apiInfo": {
      "method": "POST",
      "url": "https://api.example.com/v1/data"
    },
    "headers": [
      {
        "name": "Content-Type",
        "input": { "type": "literal", "content": "application/json" }
      }
    ],
    "params": [],
    "body": {
      "bodyType": "JSON",
      "bodyData": {
        "json": "{\"query\": \"{{block_output_node1.text}}\"}"
      }
    },
    "auth": {
      "authType": "BEARER_AUTH",
      "authOpen": true,
      "authData": {
        "bearerTokenData": [
          {
            "name": "token",
            "type": "string",
            "input": { "type": "ref", "content": { "keyPath": ["start_node", "api_key"] } }
          }
        ]
      }
    },
    "setting": {
      "timeout": 30,
      "retryTimes": 2
    }
  }
}
```

## Source Files

- Frontend: `source/coze-studio/frontend/packages/workflow/playground/src/node-registries/http/`
- Backend: `source/coze-studio/backend/domain/workflow/internal/nodes/httprequester/`
