# Database Schema Documentation

## Tables Overview
- Users: Authentication and user management
- Teams: Team information and settings
- TeamMembers: Many-to-many relationship between Users and Teams
- Sessions: Game footage and analysis data

## Relationships
- A User can be part of multiple Teams (via TeamMembers)
- A Team can have multiple Users (via TeamMembers)
- A Session belongs to one Team
- A Session is uploaded by one User
- A Session can be reviewed by one User

## Metrics and Analysis
The Sessions table includes performance metrics stored as JSONB:
- total_distance: Total distance covered in km
- total_sprints: Number of sprints
- sprint_distance: Distance covered in sprints (m)
- high_intensity_sprints: Number of high-intensity sprints
- top_sprint_speed: Maximum sprint speed (m/s)

## Media Storage
The Sessions table includes URLs for media analysis:
- analysis_image1_url: URL for the first analysis image
- analysis_image2_url: URL for the second analysis image
- analysis_image3_url: URL for the third analysis image
- analysis_video1_url: URL for the first analysis video
- analysis_video2_url: URL for the second analysis video
- analysis_video3_url: URL for the third analysis video
- analysis_video4_url: URL for the fourth analysis video
- analysis_video5_url: URL for the fifth analysis video

## Teams Table
- `id`: UUID, primary key
- `name`: Team name
- `team_code`: Unique team code
- `created_at`: Timestamp of creation
- `is_premium`: Boolean indicating if the team is premium