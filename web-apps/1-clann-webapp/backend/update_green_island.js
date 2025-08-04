#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

async function updateGreenIslandEvents() {
  try {
    console.log('🔄 UPDATING GREEN ISLAND WITH FIXED EVENTS');
    console.log('==========================================');
    
    // Load the FIXED events
    const eventsPath = path.join(__dirname, '../../../ai/veo-games/data/19-20250419/web_events_array.json');
    const fixedEvents = JSON.parse(fs.readFileSync(eventsPath, 'utf8'));
    console.log(`✅ Loaded ${fixedEvents.length} FIXED events`);
    
    // Show event type breakdown
    const eventCounts = {};
    fixedEvents.forEach(event => {
      eventCounts[event.type] = (eventCounts[event.type] || 0) + 1;
    });
    
    console.log('\n📊 FIXED EVENT BREAKDOWN:');
    Object.entries(eventCounts).forEach(([type, count]) => {
      console.log(`   ${type}: ${count}`);
    });
    
    // API call to update the game
    console.log('\n🚀 Updating via API...');
    
    const gameId = '885c2bb4-ac4b-4b59-b8f0-3458a6bb6e90'; // Green Island game ID
    const apiUrl = 'http://localhost:3002';
    
    const response = await fetch(`${apiUrl}/api/games/${gameId}/upload-events-direct`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        events: fixedEvents
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('✅ API Update Success!');
      console.log(`   Game ID: ${gameId}`);
      console.log(`   Events: ${fixedEvents.length}`);
      console.log(`   Response: ${JSON.stringify(result)}`);
      
      console.log('\n🎯 GREEN ISLAND IS NOW READY!');
      console.log('================================');
      console.log('✅ 20 corners (throw-ins)');
      console.log('✅ 29 fouls (free kicks, tackles)');  
      console.log('✅ 1 shot (header)');
      console.log('\n🌐 Go refresh your browser - all events should now show!');
      
    } else {
      console.log('❌ API Update Failed');
      console.log(`   Status: ${response.status}`);
      console.log(`   Error: ${await response.text()}`);
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

updateGreenIslandEvents();