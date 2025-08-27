
const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: false  // For local development
});

async function updateDalkeyForReal() {
  try {
    const events = [
  {
    "type": "kick_off",
    "timestamp": 210,
    "team": "dalkey",
    "description": "Player #19 kickoff, passing ball backward"
  },
  {
    "type": "free_kick",
    "timestamp": 285,
    "team": "dalkey",
    "description": "Free kick from outside penalty area, shot saved"
  },
  {
    "type": "shot",
    "timestamp": 285,
    "team": "dalkey",
    "description": "Rebound shot after free kick, goes high"
  },
  {
    "type": "corner",
    "timestamp": 315,
    "team": "dalkey",
    "description": "Corner kick, ball headed towards goal by #17"
  },
  {
    "type": "shot",
    "timestamp": 315,
    "team": "dalkey",
    "description": "Header towards goal from corner"
  },
  {
    "type": "free_kick",
    "timestamp": 345,
    "team": "dalkey",
    "description": "Long-range free kick"
  },
  {
    "type": "shot",
    "timestamp": 345,
    "team": "dalkey",
    "description": "Free kick into top right of goal"
  },
  {
    "type": "penalty",
    "timestamp": 360,
    "team": "dalkey",
    "description": "Penalty kick"
  },
  {
    "type": "shot",
    "timestamp": 360,
    "team": "dalkey",
    "description": "Penalty kick goes into net"
  },
  {
    "type": "kick_off",
    "timestamp": 420,
    "team": "dalkey",
    "description": "Player kicks ball from center spot"
  },
  {
    "type": "kick_off",
    "timestamp": 435,
    "team": "dalkey",
    "description": "Player kicks ball backwards"
  },
  {
    "type": "kick_off",
    "timestamp": 525,
    "team": "dalkey",
    "description": "Player #11 performs kickoff backwards"
  },
  {
    "type": "shot",
    "timestamp": 585,
    "team": "dalkey",
    "description": "Long-range shot sails over crossbar"
  },
  {
    "type": "throw_in",
    "timestamp": 630,
    "team": "dalkey",
    "description": "Player takes throw-in from right sideline"
  },
  {
    "type": "foul",
    "timestamp": 690,
    "team": "dalkey",
    "description": "Referee blows whistle for foul"
  },
  {
    "type": "free_kick",
    "timestamp": 690,
    "team": "dalkey",
    "description": "Long, high free kick"
  },
  {
    "type": "shot",
    "timestamp": 705,
    "team": "dalkey",
    "description": "Shot saved by goalkeeper"
  },
  {
    "type": "throw_in",
    "timestamp": 705,
    "team": "dalkey",
    "description": "Player #2 picks up ball for throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 720,
    "team": "dalkey",
    "description": "Player throws ball from left sideline"
  },
  {
    "type": "throw_in",
    "timestamp": 735,
    "team": "dalkey",
    "description": "Player takes throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 735,
    "team": "dalkey",
    "description": "Player #4 takes long throw-in"
  },
  {
    "type": "shot",
    "timestamp": 746,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "penalty",
    "timestamp": 810,
    "team": "dalkey",
    "description": "Penalty kick, saved by goalkeeper"
  },
  {
    "type": "shot",
    "timestamp": 870,
    "team": "dalkey",
    "description": "Shot blocked by defender"
  },
  {
    "type": "shot",
    "timestamp": 915,
    "team": "dalkey",
    "description": "Shot on goal"
  },
  {
    "type": "free_kick",
    "timestamp": 930,
    "team": "dalkey",
    "description": "Player #4 takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 930,
    "team": "dalkey",
    "description": "Free kick into top left corner"
  },
  {
    "type": "free_kick",
    "timestamp": 945,
    "team": "dalkey",
    "description": "Player takes free kick"
  },
  {
    "type": "throw_in",
    "timestamp": 975,
    "team": "dalkey",
    "description": "Player takes throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 990,
    "team": "dalkey",
    "description": "Player throws ball from left sideline"
  },
  {
    "type": "substitution",
    "timestamp": 1005,
    "team": "dalkey",
    "description": "Player #7 enters field"
  },
  {
    "type": "shot",
    "timestamp": 1035,
    "team": "dalkey",
    "description": "Shot into bottom left corner"
  },
  {
    "type": "foul",
    "timestamp": 1065,
    "team": "dalkey",
    "description": "Sliding tackle, whistle for foul"
  },
  {
    "type": "shot",
    "timestamp": 1104,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 1110,
    "team": "dalkey",
    "description": "Shot into bottom left corner"
  },
  {
    "type": "shot",
    "timestamp": 1140,
    "team": "dalkey",
    "description": "Shot from inside penalty area, saved"
  },
  {
    "type": "shot",
    "timestamp": 1155,
    "team": "dalkey",
    "description": "Shot blocked by defender"
  },
  {
    "type": "shot",
    "timestamp": 1155,
    "team": "dalkey",
    "description": "Shot goes wide of left goalpost"
  },
  {
    "type": "free_kick",
    "timestamp": 1185,
    "team": "dalkey",
    "description": "Player takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 1187,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "throw_in",
    "timestamp": 1320,
    "team": "dalkey",
    "description": "Referee signals throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 1335,
    "team": "dalkey",
    "description": "Player throws ball into play"
  },
  {
    "type": "shot",
    "timestamp": 1352,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "throw_in",
    "timestamp": 1395,
    "team": "dalkey",
    "description": "Player throws ball into play"
  },
  {
    "type": "shot",
    "timestamp": 1410,
    "team": "dalkey",
    "description": "Volley shot goes into net"
  },
  {
    "type": "throw_in",
    "timestamp": 1425,
    "team": "dalkey",
    "description": "Player takes throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 1440,
    "team": "dalkey",
    "description": "Awarded to Team B"
  },
  {
    "type": "kick_off",
    "timestamp": 1455,
    "team": "dalkey",
    "description": "Player kicks off backwards"
  },
  {
    "type": "throw_in",
    "timestamp": 1485,
    "team": "dalkey",
    "description": "Player #4 performs throw-in"
  },
  {
    "type": "kick_off",
    "timestamp": 1515,
    "team": "dalkey",
    "description": "Player kicks off backwards after whistle"
  },
  {
    "type": "shot",
    "timestamp": 1527,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 1530,
    "team": "dalkey",
    "description": "Player shoots, goes wide"
  },
  {
    "type": "throw_in",
    "timestamp": 1545,
    "team": "dalkey",
    "description": "Player throws ball in"
  },
  {
    "type": "foul",
    "timestamp": 1560,
    "team": "dalkey",
    "description": "White player commits slide tackle"
  },
  {
    "type": "free_kick",
    "timestamp": 1575,
    "team": "dalkey",
    "description": "Player takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 1580,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 1590,
    "team": "dalkey",
    "description": "Shot saved by goalkeeper"
  },
  {
    "type": "corner",
    "timestamp": 1605,
    "team": "dalkey",
    "description": "Player takes corner kick"
  },
  {
    "type": "shot",
    "timestamp": 1611,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "drop_ball",
    "timestamp": 1650,
    "team": "dalkey",
    "description": "Drop ball results in Team B possession"
  },
  {
    "type": "kick_off",
    "timestamp": 1665,
    "team": "dalkey",
    "description": "Player #1 kicks ball forward"
  },
  {
    "type": "throw_in",
    "timestamp": 1680,
    "team": "dalkey",
    "description": "Referee signals throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 1695,
    "team": "dalkey",
    "description": "Player throws ball into play"
  },
  {
    "type": "free_kick",
    "timestamp": 1725,
    "team": "dalkey",
    "description": "Player takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 1725,
    "team": "dalkey",
    "description": "Free kick into top right corner"
  },
  {
    "type": "free_kick",
    "timestamp": 1755,
    "team": "dalkey",
    "description": "Player takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 1772,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2092,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2135,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2187,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "goal",
    "timestamp": 2189,
    "team": "dalkey",
    "description": "Goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2230,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2426,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3288,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3314,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3460,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3618,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3994,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4038,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4235,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4331,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4459,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4590,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4756,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4798,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4870,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4933,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 5095,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "goal",
    "timestamp": 5096,
    "team": "dalkey",
    "description": "Goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 5322,
    "team": "dalkey",
    "description": "Shot on goal (VEO Verified)"
  }
];
    const tactical = {
  "analysis": {
    "match_summary": {
      "final_score": "Team A 2 - 0 Team B",
      "story": "Team A secured a 2-0 victory over Team B in a match dominated by Team A's attacking prowess and Team B's defensive efforts. Team A created numerous chances, converting two into goals. Team B, despite a saved penalty, struggled to generate significant attacking threat.",
      "key_moments": [
        "Team A's first goal at 36:29",
        "Team A's second goal at 84:56",
        "Team B's missed penalty at 13:30"
      ],
      "turning_points": [
        "Team A's first goal shifted momentum",
        "Team A capitalized on attacking dominance"
      ]
    },
    "team_analysis": {
      "team a": {
        "team_name": "Team A",
        "team_color": "white",
        "strengths": [
          "Dominant attacking play",
          "Creating chances from open play and set pieces",
          "Goalkeeper's penalty save"
        ],
        "weaknesses": [
          "Converting all chances",
          "Defensive vulnerabilities (as implied by penalty)"
        ],
        "key_players": [
          "Attacking players creating chances",
          "Goalkeeper with penalty save"
        ],
        "tactical_setup": "Focused on attacking play and creating opportunities through various means.",
        "performance_summary": "Team A demonstrated strong attacking capability, converting their dominance into goals. While their defense faced challenges (penalty), they secured a deserved victory."
      },
      "team b": {
        "team_name": "Team B",
        "team_color": "red and black",
        "strengths": [
          "Defensive solidity and interceptions",
          "Winning fouls and free kicks",
          "Penalty opportunity"
        ],
        "weaknesses": [
          "Lack of attacking output",
          "Inability to convert opportunities",
          "Difficulty creating chances"
        ],
        "key_players": [
          "Defensive players making interceptions and tackles",
          "Penalty taker"
        ],
        "tactical_setup": "Focused on defensive organization and attempting to contain Team A's attacks.",
        "performance_summary": "Team B displayed commendable defensive resilience but struggled to create attacking opportunities. Their inability to convert a penalty kick and generate shots contributed to their loss."
      }
    }
  },
  "tactical": {
    "insights_generated": true,
    "analysis_timestamp": "20250427-match-apr-27-2025-9bd1cf29",
    "teams_analyzed": [
      "Team A",
      "Team B"
    ]
  }
};
    const metadata = {
  "teams": {
    "red_team": {
      "name": "Dalkey",
      "jersey_color": "white"
    },
    "blue_team": {
      "name": "Corduff",
      "jersey_color": "red"
    }
  },
  "match_id": "20250427-match-apr-27-2025-9bd1cf29",
  "final_score": "Dalkey 0 - 2 Corduff",
  "v5_analysis": true
};
    
    const result = await pool.query(
      'UPDATE games SET ai_analysis = $1, tactical_analysis = $2, metadata = $3, status = $4 WHERE id = $5 RETURNING title, team_name',
      [events, tactical, metadata, 'analyzed', '50ce15ae-b083-4e93-a831-d9f950c39ee8']
    );
    
    if (result.rows.length > 0) {
      console.log('🎉 ACTUALLY Updated game:', result.rows[0].title);
      console.log('📊 Events:', events.length, 'with team names');
      console.log('🧠 Tactical analysis: YES');
      console.log('🎨 Metadata with teams structure: YES');
      console.log('🌐 View: http://localhost:3000/games/50ce15ae-b083-4e93-a831-d9f950c39ee8');
    } else {
      console.log('❌ Game not found');
    }
    
    await pool.end();
  } catch (error) {
    console.error('❌ Database error:', error.message);
  }
}

updateDalkeyForReal();
