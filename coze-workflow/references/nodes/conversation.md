# Conversation Nodes

## Purpose

A family of nodes for managing persistent conversations and messages within a workflow application. These nodes enable workflows to create, list, delete conversations, read conversation history, and create/list messages. They are **only available in application (app) scenarios**, not in agent scenarios. Backend node types: `CreateConversation`, `ConversationList`, `ConversationHistory`, `ClearConversationHistory`, `ConversationDelete`, `CreateMessage`, `MessageList`.

## Node Types Overview

| Node Type | Backend Type | Description |
|-----------|-------------|-------------|
| Create Conversation | `CreateConversation` | Creates or retrieves a conversation by name |
| Conversation List | `ConversationList` | Lists all conversations for the current user/app |
| Conversation History | `ConversationHistory` | Retrieves recent message rounds from a conversation |
| Clear Conversation History | `ClearConversationHistory` | Clears all messages in a conversation |
| Delete Conversation | `ConversationDelete` | Deletes a dynamically-created conversation |
| Create Message | `CreateMessage` | Creates a new message in a conversation |
| Message List | `MessageList` | Lists messages with pagination |

---

## Create Conversation

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversationName` | `string` | Yes | Name of the conversation to create or retrieve |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `isSuccess` | `boolean` | Whether the operation succeeded |
| `conversationId` | `integer` | ID of the created or existing conversation |
| `isExisted` | `boolean` | Whether the conversation already existed |

---

## Conversation List

### Inputs

No input parameters required.

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `conversationList` | `Array<Object>` | List of conversation objects |
| `conversationList[].conversationName` | `string` | Conversation name |
| `conversationList[].conversationId` | `string` | Conversation ID (as string) |

---

## Conversation History

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversationName` | `string` | Yes | Name of the conversation |
| `rounds` | `integer` | Yes | Number of recent rounds to retrieve |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `messageList` | `Array<Object>` | List of message objects |
| `messageList[].role` | `string` | Message role (`"user"` or `"assistant"`) |
| `messageList[].content` | `string` | Message content text |

---

## Clear Conversation History

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversationName` | `string` | Yes | Name of the conversation to clear |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `isSuccess` | `boolean` | Whether the operation succeeded |

---

## Delete Conversation

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversationName` | `string` | Yes | Name of the conversation to delete |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `isSuccess` | `boolean` | Whether the operation succeeded |

### Constraints
- Only dynamically-created conversations (created through nodes) can be deleted.
- Static/template-based conversations cannot be deleted and will return an error.

---

## Create Message

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversationName` | `string` | Yes | Target conversation name |
| `role` | `"user"` \| `"assistant"` | Yes | Message role |
| `content` | `string` | Yes | Message content text |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `isSuccess` | `boolean` | Whether the operation succeeded |
| `message` | `Object` | Created message details |
| `message.messageId` | `string` | Message ID |
| `message.role` | `string` | Message role |
| `message.contentType` | `string` | Content type (always `"text"`) |
| `message.content` | `string` | Message content |

### Behavior
- For `user` role messages: automatically creates a new run (conversation round).
- For `assistant` role messages in the same conversation: reuses the current run ID.
- In agent scenarios, only the `Default` conversation is allowed.

---

## Message List

### Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversationName` | `string` | Yes | Target conversation name |
| `limit` | `integer` | No | Max messages to return (1-50, default: 50) |
| `beforeId` | `string` | No | Fetch messages before this message ID |
| `afterId` | `string` | No | Fetch messages after this message ID |

### Outputs

| Field | Type | Description |
|-------|------|-------------|
| `messageList` | `Array<Object>` | List of message objects |
| `messageList[].messageId` | `string` | Message ID |
| `messageList[].role` | `string` | Message role |
| `messageList[].contentType` | `string` | Content type |
| `messageList[].content` | `string` | Message content |
| `firstId` | `string` | First message ID in the result |
| `lastId` | `string` | Last message ID in the result |
| `hasMore` | `boolean` | Whether more messages are available |

### Constraints
- `beforeId` and `afterId` cannot be used simultaneously.

---

## Common Constraints

- All conversation nodes require an `appID` in the execution context (not available in pure agent scenarios).
- Conversation names map to either **static** (template-defined) or **dynamic** (node-created) conversations.
- Operations are scoped to the current user and connector.

## Example JSON Snippet

### Create Message
```json
{
  "data": {
    "inputs": {
      "inputParameters": [
        {
          "name": "conversationName",
          "input": { "type": "literal", "value": { "type": "string", "content": "support-chat" } }
        },
        {
          "name": "role",
          "input": { "type": "literal", "value": { "type": "string", "content": "assistant" } }
        },
        {
          "name": "content",
          "input": { "type": "ref", "content": "", "value": { "type": "reference", "content": "{{llm_node.output}}" } }
        }
      ]
    },
    "outputs": [
      { "name": "isSuccess", "type": "Boolean" },
      {
        "name": "message",
        "type": "Object",
        "children": [
          { "name": "messageId", "type": "String" },
          { "name": "role", "type": "String" },
          { "name": "contentType", "type": "String" },
          { "name": "content", "type": "String" }
        ]
      }
    ]
  }
}
```
