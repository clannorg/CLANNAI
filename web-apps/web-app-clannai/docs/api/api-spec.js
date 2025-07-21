/**
 * API INTERACTIONS FOR COMPANY DASHBOARD
 * 
 * 1. FETCH SESSIONS
 * Endpoint: GET /api/sessions/all
 * Headers Required: 
 * - Authorization: Bearer {token}
 * - user-id: {userId}
 * Response Format:
 * {
 *   id: string,
 *   team_name: string,
 *   footage_url: string,
 *   status: 'PENDING' | 'REVIEWED',
 *   created_at: timestamp,
 *   uploaded_by_email: string,
 *   analyses: [
 *     {
 *       id: string,
 *       type: 'HEATMAP' | 'SPRINT_MAP' | 'GAME_MOMENTUM',
 *       image_url: string,
 *       analyst_email: string,
 *       description: string
 *     }
 *   ]
 * }[]
 * 
 * 2. UPLOAD ANALYSIS
 * Endpoint: POST /api/sessions/analysis
 * Headers Required:
 * - Authorization: Bearer {token}
 * Form Data:
 * - file: File
 * - sessionId: string
 * - type: 'HEATMAP' | 'SPRINT_MAP' | 'GAME_MOMENTUM'
 * Response Format:
 * {
 *   id: string,
 *   type: string,
 *   image_url: string,
 *   analyst_email: string
 * }
 * 
 * 3. DELETE ANALYSIS
 * Endpoint: DELETE /api/sessions/{sessionId}/analysis/{type}
 * Headers Required:
 * - Authorization: Bearer {token}
 * Response: 
 * { message: 'Analysis deleted successfully' }
 * 
 * 4. UPDATE SESSION STATUS
 * Endpoint: PUT /api/sessions/{sessionId}/status
 * Headers Required:
 * - Authorization: Bearer {token}
 * Response:
 * { status: 'PENDING' | 'REVIEWED' }
 * 
 * 5. UPDATE ANALYSIS DESCRIPTION
 * Endpoint: PUT /api/sessions/{sessionId}/description
 * Headers Required:
 * - Authorization: Bearer {token}
 * Body:
 * { description: string }
 * Response:
 * { message: 'Description updated successfully' }
 */ 