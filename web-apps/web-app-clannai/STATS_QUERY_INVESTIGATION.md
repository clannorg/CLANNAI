# Stats Query Investigation Report

## Current System Overview
- Web app with React frontend and Node/Express backend
- PostgreSQL database hosted on AWS RDS
- Same database used for both local and production
- Stats query works locally but fails in production

## Database Structure
- Users table with roles and relationships
- Teams table with subscription status
- Sessions table with analysis status
- TeamMembers linking users and teams

## The Problem
Stats endpoint fails in production but works locally, while simpler queries work in both environments.

### Working Queries (Both Environments)
- Simple CRUD operations
- Single table queries
- Basic joins
- Team member management
- Session uploads

### Failing Query (Production Only)
Complex stats calculation with:
- Common Table Expressions (CTE)
- Multiple subqueries
- Pattern matching (LIKE)
- Aggregations across tables

## Environment Differences

### Local Environment
- Direct database connection
- No API gateway
- No load balancers
- Faster query response

### Production Environment
- AWS infrastructure layers
- API gateway timeouts
- Load balancer timeouts
- SSL overhead
- Network latency

## Root Cause Analysis
1. Query Complexity
   - Multiple subqueries increase execution time
   - Pattern matching is resource intensive
   - Cross-table joins add overhead

2. Infrastructure Impact
   - Production timeouts before query completes
   - Added latency from AWS services
   - SSL negotiation overhead

3. Connection Handling
   - Local connections more resilient
   - Production has additional security layers

## Recommended Solution Approach

1. Query Optimization
   - Split complex query into smaller parts
   - Pre-calculate common values
   - Optimize join operations
   - Consider materialized views

2. Infrastructure Adjustments
   - Review timeout settings
   - Consider query caching
   - Optimize connection pooling

3. Monitoring & Debugging
   - Add query timing metrics
   - Log execution plans
   - Monitor connection pool status

4. Alternative Approaches
   - Background job to pre-calculate stats
   - Cached results with periodic updates
   - Denormalized stats table

## Success Metrics
- Query completes within timeout limits
- Consistent results between environments
- Maintained data accuracy
- Improved response times

## Risk Assessment
- Query optimization might affect accuracy
- Caching could lead to stale data
- Infrastructure changes need careful testing

## Next Steps
1. Implement query timing logs
2. Test query execution plans
3. Evaluate caching strategies
4. Review infrastructure timeouts
5. Consider background calculation job

This approach focuses on understanding and optimizing the existing system rather than making major architectural changes.
