# Feedback Feature Integration Guide

## Overview
This guide explains how to integrate the thumbs up/down feedback feature between your React frontend and FastAPI backend.

## Backend Setup

### 1. Database Table
The `feedback` table should already exist in your PostgreSQL database with the following structure:

```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    feedback VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. API Endpoint
**Endpoint:** `POST /api/feedback`

**Request Body:**
```json
{
  "query": "What is the total capacity in Maharashtra?",
  "response": "The total capacity is 450 MW.",
  "feedback": "thumbs_up",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_id": 123
}
```

**Feedback Values:**
- `thumbs_up` - Positive feedback
- `thumbs_down` - Negative feedback

## Frontend Integration

### 1. Update Your Message Component

```typescript
import { ThumbsUp, ThumbsDown, Copy } from 'lucide-react';
import { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const MessageComponent = ({ message, userQuery }) => {
  const [feedbackGiven, setFeedbackGiven] = useState<'up' | 'down' | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submitFeedback = async (feedbackType: 'thumbs_up' | 'thumbs_down') => {
    setIsSubmitting(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userQuery,
          response: message.content,
          feedback: feedbackType,
        }),
      });

      if (response.ok) {
        setFeedbackGiven(feedbackType === 'thumbs_up' ? 'up' : 'down');
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      {/* Message content */}
      <div>{message.content}</div>
      
      {/* Feedback buttons */}
      <div className="flex items-center gap-2 mt-2">
        <button
          onClick={() => submitFeedback('thumbs_up')}
          disabled={isSubmitting || feedbackGiven !== null}
          className={feedbackGiven === 'up' ? 'text-emerald-400' : 'text-gray-500'}
        >
          <ThumbsUp className="w-4 h-4" />
        </button>
        
        <button
          onClick={() => submitFeedback('thumbs_down')}
          disabled={isSubmitting || feedbackGiven !== null}
          className={feedbackGiven === 'down' ? 'text-red-400' : 'text-gray-500'}
        >
          <ThumbsDown className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
```

### 2. Track User Queries

Make sure to store the user query that led to each assistant response:

```typescript
const [messages, setMessages] = useState([]);

const sendMessage = async (userQuery: string) => {
  // Add user message
  const userMessage = {
    id: generateId(),
    role: 'user',
    content: userQuery,
    timestamp: new Date(),
  };
  setMessages(prev => [...prev, userMessage]);

  // Get assistant response
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: userQuery, session_id: sessionId }),
  });

  const data = await response.json();

  // Add assistant message with reference to user query
  const assistantMessage = {
    id: generateId(),
    role: 'assistant',
    content: data.content,
    timestamp: new Date(),
    userQuery: userQuery, // Store the query for feedback
  };
  setMessages(prev => [...prev, assistantMessage]);
};
```

## Testing

### 1. Start the Backend
```bash
python main.py
```

### 2. Test the Endpoint
```bash
python test_feedback_endpoint.py
```

### 3. Verify in Database
```sql
SELECT * FROM feedback ORDER BY created_at DESC LIMIT 10;
```

## Features

✅ Thumbs up/down feedback buttons
✅ Stores query, response, and feedback type
✅ Prevents duplicate feedback (disabled after submission)
✅ Visual feedback with color changes
✅ Error handling
✅ Optional session_id and user_id tracking

## Next Steps

Consider adding:
- Analytics dashboard to view feedback trends
- Feedback comments/reasons
- Feedback export functionality
- Email notifications for negative feedback
- A/B testing based on feedback data

## Troubleshooting

**Issue:** CORS errors
**Solution:** Make sure your backend CORS settings include your frontend URL (already configured for localhost:5173)

**Issue:** Database connection errors
**Solution:** Verify the feedback table exists and your database credentials are correct in `.env`

**Issue:** Feedback not saving
**Solution:** Check the backend logs in `app.log` for detailed error messages
