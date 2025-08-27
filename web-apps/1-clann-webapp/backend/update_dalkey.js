
const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

async function updateDalkey() {
  try {
    const events = [
  {
    "type": "kick_off",
    "timestamp": 210,
    "team": "blue",
    "description": "Player #19 kickoff, passing ball backward"
  },
  {
    "type": "free_kick",
    "timestamp": 285,
    "team": "blue",
    "description": "Free kick from outside penalty area, shot saved"
  },
  {
    "type": "shot",
    "timestamp": 285,
    "team": "blue",
    "description": "Rebound shot after free kick, goes high"
  },
  {
    "type": "corner",
    "timestamp": 315,
    "team": "blue",
    "description": "Corner kick, ball headed towards goal by #17"
  },
  {
    "type": "shot",
    "timestamp": 315,
    "team": "blue",
    "description": "Header towards goal from corner"
  },
  {
    "type": "free_kick",
    "timestamp": 345,
    "team": "blue",
    "description": "Long-range free kick"
  },
  {
    "type": "shot",
    "timestamp": 345,
    "team": "blue",
    "description": "Free kick into top right of goal"
  },
  {
    "type": "penalty",
    "timestamp": 360,
    "team": "blue",
    "description": "Penalty kick"
  },
  {
    "type": "shot",
    "timestamp": 360,
    "team": "blue",
    "description": "Penalty kick goes into net"
  },
  {
    "type": "kick_off",
    "timestamp": 420,
    "team": "blue",
    "description": "Player kicks ball from center spot"
  },
  {
    "type": "kick_off",
    "timestamp": 435,
    "team": "blue",
    "description": "Player kicks ball backwards"
  },
  {
    "type": "kick_off",
    "timestamp": 525,
    "team": "white",
    "description": "Player #11 performs kickoff backwards"
  },
  {
    "type": "shot",
    "timestamp": 585,
    "team": "blue",
    "description": "Long-range shot sails over crossbar"
  },
  {
    "type": "throw_in",
    "timestamp": 630,
    "team": "blue",
    "description": "Player takes throw-in from right sideline"
  },
  {
    "type": "foul",
    "timestamp": 690,
    "team": "white",
    "description": "Referee blows whistle for foul"
  },
  {
    "type": "free_kick",
    "timestamp": 690,
    "team": "blue",
    "description": "Long, high free kick"
  },
  {
    "type": "shot",
    "timestamp": 705,
    "team": "blue",
    "description": "Shot saved by goalkeeper"
  },
  {
    "type": "throw_in",
    "timestamp": 705,
    "team": "blue",
    "description": "Player #2 picks up ball for throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 720,
    "team": "white",
    "description": "Player throws ball from left sideline"
  },
  {
    "type": "throw_in",
    "timestamp": 735,
    "team": "blue",
    "description": "Player takes throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 735,
    "team": "blue",
    "description": "Player #4 takes long throw-in"
  },
  {
    "type": "shot",
    "timestamp": 746,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "penalty",
    "timestamp": 810,
    "team": "white",
    "description": "Penalty kick, saved by goalkeeper"
  },
  {
    "type": "shot",
    "timestamp": 870,
    "team": "blue",
    "description": "Shot blocked by defender"
  },
  {
    "type": "shot",
    "timestamp": 915,
    "team": "blue",
    "description": "Shot on goal"
  },
  {
    "type": "free_kick",
    "timestamp": 930,
    "team": "blue",
    "description": "Player #4 takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 930,
    "team": "blue",
    "description": "Free kick into top left corner"
  },
  {
    "type": "free_kick",
    "timestamp": 945,
    "team": "blue",
    "description": "Player takes free kick"
  },
  {
    "type": "throw_in",
    "timestamp": 975,
    "team": "blue",
    "description": "Player takes throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 990,
    "team": "white",
    "description": "Player throws ball from left sideline"
  },
  {
    "type": "substitution",
    "timestamp": 1005,
    "team": "white",
    "description": "Player #7 enters field"
  },
  {
    "type": "shot",
    "timestamp": 1035,
    "team": "blue",
    "description": "Shot into bottom left corner"
  },
  {
    "type": "foul",
    "timestamp": 1065,
    "team": "white",
    "description": "Sliding tackle, whistle for foul"
  },
  {
    "type": "shot",
    "timestamp": 1104,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 1110,
    "team": "blue",
    "description": "Shot into bottom left corner"
  },
  {
    "type": "shot",
    "timestamp": 1140,
    "team": "white",
    "description": "Shot from inside penalty area, saved"
  },
  {
    "type": "shot",
    "timestamp": 1155,
    "team": "blue",
    "description": "Shot blocked by defender"
  },
  {
    "type": "shot",
    "timestamp": 1155,
    "team": "blue",
    "description": "Shot goes wide of left goalpost"
  },
  {
    "type": "free_kick",
    "timestamp": 1185,
    "team": "white",
    "description": "Player takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 1187,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "throw_in",
    "timestamp": 1320,
    "team": "blue",
    "description": "Referee signals throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 1335,
    "team": "blue",
    "description": "Player throws ball into play"
  },
  {
    "type": "shot",
    "timestamp": 1352,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "throw_in",
    "timestamp": 1395,
    "team": "white",
    "description": "Player throws ball into play"
  },
  {
    "type": "shot",
    "timestamp": 1410,
    "team": "white",
    "description": "Volley shot goes into net"
  },
  {
    "type": "throw_in",
    "timestamp": 1425,
    "team": "blue",
    "description": "Player takes throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 1440,
    "team": "white",
    "description": "Awarded to Team B"
  },
  {
    "type": "kick_off",
    "timestamp": 1455,
    "team": "white",
    "description": "Player kicks off backwards"
  },
  {
    "type": "throw_in",
    "timestamp": 1485,
    "team": "blue",
    "description": "Player #4 performs throw-in"
  },
  {
    "type": "kick_off",
    "timestamp": 1515,
    "team": "white",
    "description": "Player kicks off backwards after whistle"
  },
  {
    "type": "shot",
    "timestamp": 1527,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 1530,
    "team": "white",
    "description": "Player shoots, goes wide"
  },
  {
    "type": "throw_in",
    "timestamp": 1545,
    "team": "blue",
    "description": "Player throws ball in"
  },
  {
    "type": "foul",
    "timestamp": 1560,
    "team": "blue",
    "description": "White player commits slide tackle"
  },
  {
    "type": "free_kick",
    "timestamp": 1575,
    "team": "white",
    "description": "Player takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 1580,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 1590,
    "team": "blue",
    "description": "Shot saved by goalkeeper"
  },
  {
    "type": "corner",
    "timestamp": 1605,
    "team": "white",
    "description": "Player takes corner kick"
  },
  {
    "type": "shot",
    "timestamp": 1611,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "drop_ball",
    "timestamp": 1650,
    "team": "white",
    "description": "Drop ball results in Team B possession"
  },
  {
    "type": "kick_off",
    "timestamp": 1665,
    "team": "blue",
    "description": "Player #1 kicks ball forward"
  },
  {
    "type": "throw_in",
    "timestamp": 1680,
    "team": "white",
    "description": "Referee signals throw-in"
  },
  {
    "type": "throw_in",
    "timestamp": 1695,
    "team": "white",
    "description": "Player throws ball into play"
  },
  {
    "type": "free_kick",
    "timestamp": 1725,
    "team": "white",
    "description": "Player takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 1725,
    "team": "white",
    "description": "Free kick into top right corner"
  },
  {
    "type": "free_kick",
    "timestamp": 1755,
    "team": "blue",
    "description": "Player takes free kick"
  },
  {
    "type": "shot",
    "timestamp": 1772,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2092,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2135,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2187,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "goal",
    "timestamp": 2189,
    "team": "blue",
    "description": "Goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2230,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 2426,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3288,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3314,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3460,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3618,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 3994,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4038,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4235,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4331,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4459,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4590,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4756,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4798,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4870,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 4933,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 5095,
    "team": "blue",
    "description": "Shot on goal (VEO Verified)"
  },
  {
    "type": "goal",
    "timestamp": 5096,
    "team": "blue",
    "description": "Goal (VEO Verified)"
  },
  {
    "type": "shot",
    "timestamp": 5322,
    "team": "blue",
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
    
    const result = await pool.query(
      'UPDATE games SET ai_analysis = $1, tactical_analysis = $2, status = $3 WHERE id = $4 RETURNING title',
      [events, tactical, 'analyzed', '09e614b8-6b2c-4f8a-9c3d-2e1f4a5b6c7d']
    );
    
    if (result.rows.length > 0) {
      console.log('🎉 Updated game:', result.rows[0].title);
      console.log('📊 Events:', events.length);
      console.log('🧠 Tactical analysis: YES');
      console.log('🌐 View: http://localhost:3000/games/09e614b8-6b2c-4f8a-9c3d-2e1f4a5b6c7d');
    } else {
      console.log('❌ Game not found');
    }
    
    await pool.end();
  } catch (error) {
    console.error('❌ Database error:', error.message);
  }
}

updateDalkey();
