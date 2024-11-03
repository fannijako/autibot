# Chatbot Release Notes

## v2.0.0

### New Features

#### Conversation Management
- **Chat History**: Implemented per-user conversation tracking
  - Automatic message timestamping
  - Intelligent history cleanup
  - Configurable message limits
  - Memory-efficient storage

#### New Commands
- `!clear_history`: Erases your current conversation history
- `!show_history`: Displays your active conversation thread

#### Enhanced Context Management
- Improved conversation coherence through:
  - RAG (Retrieval-Augmented Generation) integration
  - Contextual awareness from chat history
  - Natural conversation flow maintenance

### Technical Specifications

#### History Management
- **Expiration Rules**:
  - Messages automatically expire after 1 hour
  - Maximum 10 messages per user (configurable)
  - Automatic cleanup of expired messages

#### Storage Implementation
- In-memory storage system
  - Lightweight and fast
  - Dynamic memory management
  - Session-based persistence

### Important Notes

#### Usage Guidelines
1. Start chatting naturally - history is maintained automatically
2. View your conversation thread with `!show_history`
3. Reset your conversation using `!clear_history`

#### Limitations
- History is not persistent across bot restarts
- Memory usage scales with active user count

### Getting Started
Simply start a conversation with the bot - no additional setup required. Use the provided commands to manage your chat history as needed.

## v1.0.0

### Initial Release Features

#### Core Functionality
- Basic chatbot interactions
- Command-based interface
- Single-message context

#### RAG Integration
- Document-based knowledge retrieval
- Basic context injection
- Query-based information extraction

#### Commands
- Basic utility commands
- Help system
- Error handling

### Technical Details
- Stateless operation
- Simple request/response model
- No conversation persistence

### Limitations
- No conversation history
- Limited context awareness
- Single-turn interactions only

---
*For technical support or feature requests, please contact the development team.*