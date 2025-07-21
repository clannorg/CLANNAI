# ClannAI Entity Documentation

## Overview
This document provides a comprehensive overview of all entities in the ClannAI system, their properties, relationships, and current statistics.

## Core Entities

### 1. Users
The Users entity represents all individuals who can access the system.

#### Properties
- `id` (UUID): Unique identifier
- `email` (String): Unique email address
- `password_hash` (String): Hashed password
- `role` (Enum): 
  - `USER`: Regular user
  - `COMPANY_MEMBER`: Company staff member
- `created_at` (Timestamp): Account creation date
- `updated_at` (Timestamp): Last update date

#### Current Statistics
- 1 COMPANY_MEMBER (thomas@clannai.com)
- 55 regular users

### 2. Teams
Teams represent groups of users who can collaborate on session analysis.

#### Properties
- `id` (UUID): Unique identifier
- `name` (String): Team name
- `team_code` (String): Unique team code for invites
- `subscription_status` (Enum):
  - `FREE`: Basic access
  - `TRIAL`: Trial period access
  - `PREMIUM`: Full access
- `trial_ends_at` (Timestamp): End date of trial period
- `created_at` (Timestamp): Team creation date
- `updated_at` (Timestamp): Last update date

#### Relationships
- Has many Users through TeamMembers
- Has many Sessions

### 3. Team Members
Team Members is a junction entity that manages the relationship between Users and Teams.

#### Properties
- `team_id` (UUID): Reference to Team
- `user_id` (UUID): Reference to User
- `role` (Enum):
  - `ADMIN`: Team administrator
  - `MEMBER`: Regular team member
- `joined_at` (Timestamp): When the user joined the team

#### Relationships
- Links Users to Teams
- Enables many-to-many relationship between Users and Teams

### 4. Sessions
Sessions represent individual training or game analysis sessions.

#### Properties
- `id` (UUID): Unique identifier
- `team_id` (UUID): Reference to Team
- `footage_url` (String): URL to session footage
- `status` (Enum):
  - `PENDING`: Awaiting analysis
  - `REVIEWED`: Analysis completed
- `uploaded_by` (UUID): Reference to User who uploaded
- `reviewed_by` (UUID): Reference to User who reviewed
- `analysis_image1_url` (String): Heatmap URL
- `analysis_image2_url` (String): Sprint map URL
- `analysis_image3_url` (String): Game momentum URL
- `analysis_video1_url` through `analysis_video5_url` (String): Analysis video URLs
- `created_at` (Timestamp): Session creation date
- `updated_at` (Timestamp): Last update date

#### Current Statistics
- 14 total sessions
- 11 PENDING
- 3 REVIEWED

## Entity Relationships

### Key Relationships
1. User -> Teams: Many-to-Many through TeamMembers
2. Team -> Sessions: One-to-Many
3. Session -> User (uploaded_by): Many-to-One
4. Session -> User (reviewed_by): Many-to-One

### Important Constraints
1. Users must have unique emails
2. Teams must have unique team_codes
3. Sessions must belong to a team
4. Analysis URLs can be null
5. Session status must be either 'PENDING' or 'REVIEWED'

## Feature-Specific Fields

### Team Management
- `team_code`: Used for team invites
- `subscription_status`: Controls access level
- `trial_ends_at`: Manages trial period

### Analysis Tracking
- `status`: Tracks analysis state
- `uploaded_by`: Tracks who submitted the footage
- `reviewed_by`: Tracks which analyst processed it
- `analysis_urls`: Store S3 links to analysis files

### User Access Control
- `user.role`: Controls dashboard access
- `team_member.role`: Controls team permissions 