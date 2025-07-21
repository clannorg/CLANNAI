# Technical Stack & Development Guide

## Web Platform
- **React** 
  - Web-first development
  - TypeScript support
  - Compatible with AWS Amplify
  - Great IDE support in VS Code/Cursor

## Backend
- **AWS Amplify**
  - Built-in CI/CD
  - Easy AWS service integration
  - GraphQL API generation
  - Authentication flows

## Database
- **PostgreSQL on AWS RDS**
  - Matches our schema
  - Strong type safety
  - Excellent query performance
  - AWS managed service

## API Layer
- **AWS AppSync** (GraphQL)
  - Auto-generated from schema
  - Real-time subscriptions
  - Type-safe operations
  - Built-in with Amplify

## Storage
- **AWS S3**
  - For analysis images
  - Video URL storage
  - Managed through Amplify

## Development Tools
- **Cursor IDE**
  - AI-powered completions
  - TypeScript support
  - Git integration
  - Claude Sonnet integration

## Language & Type System
- **TypeScript**
  - IDE support
  - Type safety
  - AI assistance
  - React support

## Development Planning

### GraphQL Schema
We need to define the GraphQL schema that AppSync will use, based on our PostgreSQL schema.

### AWS Infrastructure Setup
- Amplify configuration files
- RDS security groups
- S3 bucket policies


### Type Definitions
Need TypeScript interfaces for:
- Database models
- API responses
- State management
- Component props

### Testing Strategy
1. Unit Tests
   - Components
   - Hooks
   - Utilities

2. Integration Tests
   - API integration
   - Authentication flows
   - File uploads

3. E2E Tests
   - User journeys
   - Admin workflows
   - Analysis workflows

### Error Handling
- Global error boundary
- API error responses
- Form validation
- Authentication errors

### Security Considerations
- CORS policies
- JWT token management
- S3 bucket access
- RDS access patterns

### Deployment Process
1. AWS Configuration
2. Database Migration
3. Environment Setup
4. CI/CD Pipeline