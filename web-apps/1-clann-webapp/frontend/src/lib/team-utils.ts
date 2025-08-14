// Team utility functions for dynamic team colors and names

export interface TeamInfo {
  name: string
  jersey_color: string
}

export interface TeamMetadata {
  red_team: TeamInfo
  blue_team: TeamInfo
}

/**
 * Convert jersey color description to CSS classes
 */
export const getTeamColorClass = (jerseyColor: string): string => {
  const color = jerseyColor.toLowerCase().trim()
  
  switch (color) {
    case 'yellow':
      return 'bg-yellow-500 text-black border-yellow-600'
    case 'blue':
    case 'all blue':
    case 'navy blue':
      return 'bg-blue-500 text-white border-blue-600'
    case 'red':
    case 'all red':
      return 'bg-red-500 text-white border-red-600'
    case 'green':
    case 'all green':
      return 'bg-green-500 text-white border-green-600'
    case 'white':
    case 'all white':
      return 'bg-white text-black border-gray-300'
    case 'black':
    case 'all black':
      return 'bg-black text-white border-gray-600'
    case 'orange':
      return 'bg-orange-500 text-white border-orange-600'
    case 'purple':
      return 'bg-purple-500 text-white border-purple-600'
    default:
      // Fallback to gray for unknown colors
      return 'bg-gray-500 text-white border-gray-600'
  }
}

/**
 * Get team information from game metadata with fallbacks
 */
export const getTeamInfo = (game: any): { redTeam: TeamInfo, blueTeam: TeamInfo } => {
  const redTeam: TeamInfo = game.metadata?.teams?.red_team || {
    name: 'Red Team',
    jersey_color: 'red'
  }
  
  const blueTeam: TeamInfo = game.metadata?.teams?.blue_team || {
    name: 'Blue Team', 
    jersey_color: 'blue'
  }
  
  return { redTeam, blueTeam }
}

/**
 * Get team color class by team type (red/blue)
 */
export const getTeamColorByType = (game: any, teamType: 'red' | 'blue'): string => {
  const { redTeam, blueTeam } = getTeamInfo(game)
  
  if (teamType === 'red') {
    return getTeamColorClass(redTeam.jersey_color)
  } else {
    return getTeamColorClass(blueTeam.jersey_color)
  }
}

/**
 * Get team name by team type (red/blue)
 */
export const getTeamNameByType = (game: any, teamType: 'red' | 'blue'): string => {
  const { redTeam, blueTeam } = getTeamInfo(game)
  
  return teamType === 'red' ? redTeam.name : blueTeam.name
}