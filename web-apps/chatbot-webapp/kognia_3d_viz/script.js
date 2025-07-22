import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// --- Configuration ---
const PITCH_LENGTH = 105; // Standard pitch length (e.g., meters)
const PITCH_WIDTH = 68;  // Standard pitch width
// --- NEW Constants for pitch markings/goals ---
const LINE_THICKNESS = 0.15; // No longer used for geometry, but keep in case
const PENALTY_BOX_LENGTH = 16.5;
const PENALTY_BOX_WIDTH = 40.3;
const GOAL_AREA_LENGTH = 5.5;
const GOAL_AREA_WIDTH = 18.3;
const CENTER_CIRCLE_RADIUS = 9.15;
const GOAL_HEIGHT = 2.44;
const GOAL_WIDTH = 7.32;
const GOAL_DEPTH = 1.5; // How far back the goal net structure goes (simple box for now)
const GOAL_POST_RADIUS = 0.06; // ~12cm diameter

// --- NEW Visualization Colors & Sizes ---
const PASS_COLOR = 0xffffff; // White for passes
const SHOT_COLOR = 0xff0000; // Red for shots (No longer used)
const SHOT_RADIUS = 0.6;    // Radius of the shot spheres
const TEAM1_COLOR = 0x034694; // Chelsea Blue
const TEAM2_COLOR = 0x7A263A; // West Ham Claret
const CROSS_COLOR = 0xffa500; // Orange for crosses (changed from magenta)

// --- Time/Vertical Scale ---
const MAX_TIME_MINUTES = 90;
const MAX_HEIGHT = 50; // Arbitrary height in 3D units representing 90 mins
// const TIME_SCALE = MAX_HEIGHT / (MAX_TIME_MINUTES * 60); // If needed later for mapping event time

// --- NEW: Store Team Info Globally --- 
let teamInfo = {
    team1: { uuid: null, name: "Team 1" }, 
    team2: { uuid: null, name: "Team 2" }
};

// --- Scene Setup ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111111); // Dark background

// --- NEW: Groups for events ---
const allShotsGroup = new THREE.Group(); 
const onTargetShotsGroup = new THREE.Group(); 
// const goalShotsGroup = new THREE.Group(); // Removed
const passesGroup = new THREE.Group();
const crossesGroup = new THREE.Group(); 
scene.add(allShotsGroup);
scene.add(onTargetShotsGroup);
// scene.add(goalShotsGroup); // Removed
scene.add(passesGroup);
scene.add(crossesGroup); 

const camera = new THREE.PerspectiveCamera(
    75, // Field of View
    window.innerWidth / window.innerHeight, // Aspect Ratio
    0.1, // Near clipping plane
    1000 // Far clipping plane
);
// Adjusted camera position for better pitch view
camera.position.set(0, 60, PITCH_WIDTH * 0.7); // Y-up, Z towards camera
camera.lookAt(0, 0, 0); // Look at the center of the pitch

const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('pitchCanvas'), antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);

// --- Lighting ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7); // Slightly brighter ambient
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.9); // Slightly brighter directional
directionalLight.position.set(-60, 80, 50); // Adjust light angle
directionalLight.castShadow = false; // Optional: enable shadows later if needed
scene.add(directionalLight);

// --- Controls ---
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; // Smooth camera movement
controls.dampingFactor = 0.05;
controls.screenSpacePanning = false; // Pan orthogonal to camera direction
// Adjust max polar angle slightly if needed based on new camera angle
// controls.maxPolarAngle = Math.PI / 2 - 0.05;
controls.minDistance = 20; // Increased min distance
controls.maxDistance = 200;
controls.target.set(0, 0, 0); // Ensure controls target the center

// --- Pitch Surface ---
const pitchGeometry = new THREE.PlaneGeometry(PITCH_LENGTH, PITCH_WIDTH);
const pitchMaterial = new THREE.MeshStandardMaterial({
    color: 0x228B22, // Forest Green
    side: THREE.DoubleSide
});
const pitch = new THREE.Mesh(pitchGeometry, pitchMaterial);
pitch.rotation.x = -Math.PI / 2; // Rotate plane to be flat on XZ plane
// pitch.receiveShadow = true; // Optional: enable shadows
scene.add(pitch);

// --- Pitch Lines (2D Ground + Vertical Lines + Top Connecting Lines) ---
const lineMaterial = new THREE.LineBasicMaterial({ color: 0xffffff });
const linesGroup = new THREE.Group(); // Group for all lines

const halfLength = PITCH_LENGTH / 2;
const halfWidth = PITCH_WIDTH / 2;
const groundY = 0.01; // Slightly above the pitch surface

// --- Helper: Add 2D Line Segment on Ground ---
function addGroundLine(x1, z1, x2, z2) {
    const points = [];
    points.push(new THREE.Vector3(x1, groundY, z1));
    points.push(new THREE.Vector3(x2, groundY, z2));
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, lineMaterial);
    linesGroup.add(line);
}

// --- Helper: Add Single Vertical Line ---
function addVerticalLine(x, z) {
    const points = [];
    points.push(new THREE.Vector3(x, 0, z)); // Start at ground
    points.push(new THREE.Vector3(x, MAX_HEIGHT, z)); // Go up to max height
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, lineMaterial);
    linesGroup.add(line);
}

// --- Helper: Add Horizontal Line Segment at Top ---
function addTopLine(x1, z1, x2, z2) {
    const points = [];
    points.push(new THREE.Vector3(x1, MAX_HEIGHT, z1));
    points.push(new THREE.Vector3(x2, MAX_HEIGHT, z2));
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, lineMaterial);
    linesGroup.add(line);
}

// --- Helper: Add Ground, Vertical, and Top lines for a segment ---
function addCompleteSegment(x1, z1, x2, z2) {
    addGroundLine(x1, z1, x2, z2);
    addVerticalLine(x1, z1); // Add vertical at start point
    addVerticalLine(x2, z2); // Add vertical at end point
    addTopLine(x1, z1, x2, z2); // Connect the top points
}

// --- Draw Lines ---

// Outer boundary
addCompleteSegment(-halfLength, -halfWidth, halfLength, -halfWidth); // Bottom sideline
addCompleteSegment(-halfLength, halfWidth, halfLength, halfWidth);   // Top sideline
addCompleteSegment(-halfLength, -halfWidth, -halfLength, halfWidth); // Left goal line
addCompleteSegment(halfLength, -halfWidth, halfLength, halfWidth);   // Right goal line

// Center line
addCompleteSegment(0, -halfWidth, 0, halfWidth);

// Center circle
const circlePoints = new THREE.Path().absarc(0, 0, CENTER_CIRCLE_RADIUS, 0, Math.PI * 2, false).getPoints(8); // Keep points for defining top/bottom loops
const groundCircleVectors = [];
const topCircleVectors = [];

// Add only two vertical lines where circle meets center line
addVerticalLine(0, CENTER_CIRCLE_RADIUS);
addVerticalLine(0, -CENTER_CIRCLE_RADIUS);

// Still generate vectors for the ground and top loops using the points
circlePoints.forEach(p => {
    groundCircleVectors.push(new THREE.Vector3(p.x, groundY, p.y));
    topCircleVectors.push(new THREE.Vector3(p.x, MAX_HEIGHT, p.y));
});

// Draw the ground circle line
const groundCircleGeometry = new THREE.BufferGeometry().setFromPoints(groundCircleVectors);
const groundCenterCircle = new THREE.LineLoop(groundCircleGeometry, lineMaterial);
linesGroup.add(groundCenterCircle);
// Draw the top circle line
const topCircleGeometry = new THREE.BufferGeometry().setFromPoints(topCircleVectors);
const topCenterCircle = new THREE.LineLoop(topCircleGeometry, lineMaterial);
linesGroup.add(topCenterCircle);

// Penalty Boxes
const pbZ = PENALTY_BOX_WIDTH / 2;
const pbX_left_goal = -halfLength;
const pbX_left_front = -halfLength + PENALTY_BOX_LENGTH;
const pbX_right_goal = halfLength;
const pbX_right_front = halfLength - PENALTY_BOX_LENGTH;

// Left Box - Draw segments completely (ground, verticals, top)
addCompleteSegment(pbX_left_goal, -pbZ, pbX_left_front, -pbZ); // Bottom side
addCompleteSegment(pbX_left_goal, pbZ, pbX_left_front, pbZ);   // Top side
addCompleteSegment(pbX_left_front, -pbZ, pbX_left_front, pbZ); // Front side

// Right Box
addCompleteSegment(pbX_right_goal, -pbZ, pbX_right_front, -pbZ); // Bottom side
addCompleteSegment(pbX_right_goal, pbZ, pbX_right_front, pbZ);   // Top side
addCompleteSegment(pbX_right_front, -pbZ, pbX_right_front, pbZ); // Front side

// Goal Areas
const gaZ = GOAL_AREA_WIDTH / 2;
const gaX_left_front = -halfLength + GOAL_AREA_LENGTH;
const gaX_right_front = halfLength - GOAL_AREA_LENGTH;

// Left Area
addCompleteSegment(pbX_left_goal, -gaZ, gaX_left_front, -gaZ); // Bottom side
addCompleteSegment(pbX_left_goal, gaZ, gaX_left_front, gaZ);   // Top side
addCompleteSegment(gaX_left_front, -gaZ, gaX_left_front, gaZ); // Front side

// Right Area
addCompleteSegment(pbX_right_goal, -gaZ, gaX_right_front, -gaZ); // Bottom side
addCompleteSegment(pbX_right_goal, gaZ, gaX_right_front, gaZ);   // Top side
addCompleteSegment(gaX_right_front, -gaZ, gaX_right_front, gaZ); // Front side

// Penalty Spots (on ground only)
const spotRadius = 0.15;
const spotGeometry = new THREE.CircleGeometry(spotRadius, 16);
spotGeometry.rotateX(-Math.PI / 2);
const spotMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide });
const leftSpot = new THREE.Mesh(spotGeometry.clone(), spotMaterial);
leftSpot.position.set(-halfLength + 11, groundY + 0.01, 0);
linesGroup.add(leftSpot);
const rightSpot = new THREE.Mesh(spotGeometry.clone(), spotMaterial);
rightSpot.position.set(halfLength - 11, groundY + 0.01, 0);
linesGroup.add(rightSpot);

// Add the lines group to the scene
scene.add(linesGroup);

// --- Goals ---
const goalMaterial = new THREE.MeshStandardMaterial({ color: 0xdddddd });
const goalsGroup = new THREE.Group();

function createGoal(side) { // side = -1 for left, 1 for right
    const goal = new THREE.Group();
    const postHeight = GOAL_HEIGHT; // Use actual goal height
    const crossbarLength = GOAL_WIDTH;
    const goalX = side * (halfLength); // Position goal on the goal line

    const goalPostMaterial = goalMaterial;

    // Use CylinderGeometry for posts and crossbar for a round look
    const postGeometry = new THREE.CylinderGeometry(GOAL_POST_RADIUS, GOAL_POST_RADIUS, postHeight, 16);
    const crossbarGeometry = new THREE.CylinderGeometry(GOAL_POST_RADIUS, GOAL_POST_RADIUS, crossbarLength, 16);
    crossbarGeometry.rotateX(Math.PI / 2); // Rotate to be horizontal

    // Posts
    const post1 = new THREE.Mesh(postGeometry, goalPostMaterial);
    post1.position.set(goalX, postHeight / 2, -crossbarLength / 2); // Centered vertically
    goal.add(post1);

    const post2 = new THREE.Mesh(postGeometry, goalPostMaterial);
    post2.position.set(goalX, postHeight / 2, crossbarLength / 2); // Centered vertically
    goal.add(post2);

    // Crossbar
    const crossbar = new THREE.Mesh(crossbarGeometry, goalPostMaterial);
    crossbar.position.set(goalX, postHeight, 0); // Positioned at Y = postHeight
    goal.add(crossbar);

    // Optional simple back netting structure (thin cylinders)
    // ... (keep if desired, ensure Y positions are relative to ground)

    goalsGroup.add(goal);
}
createGoal(-1); // Left goal
createGoal(1);  // Right goal
scene.add(goalsGroup);

// --- Helper Function to Create Text Sprites for Time Markers ---
function createTimeMarker(text, yPosition) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const fontSize = 20; // Smaller font size
    context.font = `Bold ${fontSize}px Arial`;
    const textWidth = context.measureText(text).width;

    // Adjust canvas size based on text
    canvas.width = textWidth + 20; // Add some padding
    canvas.height = fontSize + 10;

    // Re-apply font after canvas resize
    context.font = `Bold ${fontSize}px Arial`;
    context.fillStyle = "rgba(255, 255, 255, 0.95)"; // White text
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);

    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;

    const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthTest: false // Render on top if needed, but can look weird
    });

    const sprite = new THREE.Sprite(material);

    // Scale the sprite - adjust as needed
    const spriteScale = 5;
    sprite.scale.set((canvas.width / canvas.height) * spriteScale, spriteScale, 1);

    // Position the sprite
    const xOffset = PITCH_LENGTH / 2 + 5; // Place just outside the right goal line
    const zOffset = PITCH_WIDTH / 2 + 5;  // Place just outside the top (back-right) sideline
    sprite.position.set(xOffset, yPosition, zOffset);

    return sprite;
}

// --- Add Time Markers to Scene ---
const y_0_min = 0; // Ground level
const y_45_min = (45 / MAX_TIME_MINUTES) * MAX_HEIGHT;
const y_90_min = MAX_HEIGHT; // Top level

const marker0 = createTimeMarker("0 min", y_0_min + 1); // Slightly above ground
const marker45 = createTimeMarker("45 min", y_45_min);
const marker90 = createTimeMarker("90 min", y_90_min - 1); // Slightly below top

scene.add(marker0);
scene.add(marker45);
scene.add(marker90);

// --- Simple Data Loading Test ---
async function testLoadData() {
    const TACTICAL_DATA_PATH = '/input_data/td.json'; // Absolute path from server root (kognia)
    console.log(`Attempting to load data from ${TACTICAL_DATA_PATH}...`);
    try {
        const response = await fetch(TACTICAL_DATA_PATH);
        console.log(`Fetch response status: ${response.status}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // Try to parse it as JSON to confirm it's valid
        const jsonData = await response.json(); 
        console.log("Data loaded and parsed successfully!");
        // Optional: Log a small part of the data to verify content
        // console.log("Sample data (metadata):", jsonData.metadata);
    } catch (error) {
        console.error('Data loading test failed:', error);
    }
}

// --- Data Loading and Processing Functions ---

// Map pitch coordinates and frame to 3D world coordinates
function mapTo3D(pitchX, pitchZ, frame, currentMaxFrame, pitchLength, pitchWidth, teamUuid) {
    // Needs access to MAX_HEIGHT, teamInfo

    let finalX = pitchX;
    let finalZ = pitchZ;

    // --- Flip coordinates for Team 2 --- 
    // Check if teamInfo is populated and the uuid matches team2
    if (teamInfo && teamInfo.team2 && teamInfo.team2.uuid && teamUuid === teamInfo.team2.uuid) {
        finalX = -pitchX; // Negate X
        finalZ = -pitchZ; // Negate Z
        // Optional: Log the flip for verification
        // if (Math.random() < 0.01) console.log(`Flipping coords for Team 2 (${teamUuid})`); 
    }
    // ----------------------------------

    const worldX = finalX; // Use potentially flipped coordinate
    const worldZ = finalZ; // Use potentially flipped coordinate
    const timeRatio = (currentMaxFrame > 0) ? Math.max(0, Math.min(1, frame / currentMaxFrame)) : 0;
    const worldY = timeRatio * MAX_HEIGHT;

    // Optional: Clamp coordinates to pitch bounds if needed after flipping
    // worldX = Math.max(-pitchLength/2, Math.min(pitchLength/2, worldX));
    // worldZ = Math.max(-pitchWidth/2, Math.min(pitchWidth/2, worldZ));

    return new THREE.Vector3(worldX, worldY, worldZ);
}

// Visualize the loaded tactical data
function visualizeTacticalData(events, currentMaxFrame, pitchLength, pitchWidth) {
    // Needs access to scene, passesGroup, allShotsGroup, onTargetShotsGroup, crossesGroup, etc.
    // --- Clear previous groups --- 
    while(allShotsGroup.children.length > 0) { allShotsGroup.remove(allShotsGroup.children[0]); }
    while(onTargetShotsGroup.children.length > 0) { onTargetShotsGroup.remove(onTargetShotsGroup.children[0]); }
    // while(goalShotsGroup.children.length > 0) { goalShotsGroup.remove(goalShotsGroup.children[0]); } // Removed
    while(passesGroup.children.length > 0) { passesGroup.remove(passesGroup.children[0]); }
    while(crossesGroup.children.length > 0) { crossesGroup.remove(crossesGroup.children[0]); } 

    const shotGeometry = new THREE.SphereGeometry(SHOT_RADIUS, 8, 4); 

    // --- Identify Team UUIDs & Update Legend --- 
    const teamUuids = new Set();
    events.forEach(event => {
        if (event && event.team_uuid) { // Check any event with a team_uuid
            teamUuids.add(event.team_uuid);
        }
    });
    // Assign UUIDs based on global teamInfo (which should be populated by loadTacticalData)
    // This assumes the UUIDs found match those in teamInfo
    if (teamInfo.team1.uuid && teamUuids.has(teamInfo.team1.uuid)) {
        console.log(`DEBUG: Confirmed ${teamInfo.team1.name} UUID: ${teamInfo.team1.uuid}`);
    } else {
        // Fallback if metadata names weren't loaded or UUIDs don't match
        const [uuid1, uuid2] = Array.from(teamUuids);
        teamInfo.team1.uuid = uuid1;
        teamInfo.team2.uuid = uuid2; 
        console.warn(`WARN: Using dynamically found UUIDs. Team1=${uuid1 || 'N/A'}, Team2=${uuid2 || 'N/A'}`);
    }
   
    let passesPlotted = 0, shotsPlotted = 0, onTargetPlotted = 0, /*goalsPlotted = 0,*/ crossesPlotted = 0; // Update counters
    console.log(`Processing ${events.length} events...`);

    events.forEach((event, index) => {
        if (!event || !event.metrics || event.start_frame === undefined || event.start_frame === null || !event.team_uuid) return;
        
        let isPass = false, isShot = false, isCross = false;
        let plottedThisEvent = false; // Use this if needed within blocks

        // --- Process Crosses (E59 with M02) --- 
        if (event.type === 'E59') {
            const m02Metric = event.metrics.find(m => m && m.type === 'M02');
            if (m02Metric && Array.isArray(m02Metric.value) && m02Metric.value.length === 2 && 
                Array.isArray(m02Metric.value[0]) && m02Metric.value[0].length === 2 &&
                Array.isArray(m02Metric.value[1]) && m02Metric.value[1].length === 2)
            {
                const [x1, z1] = m02Metric.value[0];
                const [x2, z2] = m02Metric.value[1];
                const startFrame = event.start_frame;
                const endFrame = event.end_frame !== null && event.end_frame !== undefined ? event.end_frame : startFrame;
                const startPos = mapTo3D(x1, z1, startFrame, currentMaxFrame, pitchLength, pitchWidth, event.team_uuid);
                const endPos = mapTo3D(x2, z2, endFrame, currentMaxFrame, pitchLength, pitchWidth, event.team_uuid);
                const crossGeometry = new THREE.BufferGeometry().setFromPoints([startPos, endPos]);
                // Need to compute line distances for dashed lines: crossGeometry.computeLineDistances();
                const teamColor = event.team_uuid === teamInfo.team1.uuid ? TEAM1_COLOR : event.team_uuid === teamInfo.team2.uuid ? TEAM2_COLOR : 0x808080;
                const crossMaterial = new THREE.LineBasicMaterial({ color: teamColor });
                const crossLine = new THREE.Line(crossGeometry, crossMaterial);
                crossesGroup.add(crossLine);
                crossesPlotted++;
                isCross = true;
                plottedThisEvent = true; // Mark as plotted if needed by outer logic
            }
        }

        // --- Process Passes (M02, not Crosses) --- 
        if (!isCross) { // Only if not already plotted as a cross
            const passMetric = event.metrics.find(m => m.type === 'M02');
            if (passMetric && event.team_uuid) { 
                // --- Check the CORRECT structure: Array of 2 Arrays, each with 2 numbers ---
                if (Array.isArray(passMetric.value) && passMetric.value.length === 2 && 
                    Array.isArray(passMetric.value[0]) && passMetric.value[0].length === 2 &&
                    Array.isArray(passMetric.value[1]) && passMetric.value[1].length === 2) 
                { 
                    // Destructure correctly from nested arrays
                    const [x1, z1] = passMetric.value[0];
                    const [x2, z2] = passMetric.value[1];

                    // Determine team color based on event.team_uuid
                    let teamColor;
                    if (event.team_uuid === teamInfo.team1.uuid) { // Compare with stored UUID
                        teamColor = TEAM1_COLOR;
                    } else if (event.team_uuid === teamInfo.team2.uuid) { // Compare with stored UUID
                        teamColor = TEAM2_COLOR;
                    } else {
                        teamColor = 0x808080; // Default grey
                    }
                    const passMaterial = new THREE.LineBasicMaterial({ color: teamColor }); // Create material with team color

                    const startFrame = event.start_frame;
                    const endFrame = event.end_frame !== null && event.end_frame !== undefined ? event.end_frame : startFrame;
                    const startPos = mapTo3D(x1, z1, startFrame, currentMaxFrame, pitchLength, pitchWidth, event.team_uuid);
                    const endPos = mapTo3D(x2, z2, endFrame, currentMaxFrame, pitchLength, pitchWidth, event.team_uuid);
                    const passGeometry = new THREE.BufferGeometry().setFromPoints([startPos, endPos]);
                    passesGroup.add(new THREE.Line(passGeometry, passMaterial)); // Add to passesGroup using team material
                    passesPlotted++;
                    isPass = true;
                    plottedThisEvent = true;
                } else {
                    // Log if structure is not as expected
                    console.log(`DEBUG M02 value structure incorrect [Event ${index}]. Value:`, JSON.stringify(passMetric.value));
                }
            }
        }

        // --- Process Shots (M23) --- 
        const shotMetric = event.metrics.find(m => m && m.type === 'M23');
        if (shotMetric && event.team_uuid) { 
            if (shotMetric.value && 
                Array.isArray(shotMetric.value) &&
                shotMetric.value.length > 0 &&
                Array.isArray(shotMetric.value[0]) &&
                shotMetric.value[0].length === 2)
            {
                const [x, z] = shotMetric.value[0];
                
                // Determine TEAM color only
                let teamColor;
                if (event.team_uuid === teamInfo.team1.uuid) {
                    teamColor = TEAM1_COLOR;
                } else if (event.team_uuid === teamInfo.team2.uuid) {
                    teamColor = TEAM2_COLOR;
                } else {
                    teamColor = 0x808080; // Default grey
                }
                const shotMaterial = new THREE.MeshBasicMaterial({ color: teamColor });
                
                // Create the sphere
                const startFrame = event.start_frame;
                if (startFrame !== undefined && startFrame !== null) {
                    const shotPos = mapTo3D(x, z, startFrame, currentMaxFrame, pitchLength, pitchWidth, event.team_uuid);
                    const shotSphere = new THREE.Mesh(shotGeometry, shotMaterial);
                    shotSphere.position.copy(shotPos);

                    // Always add to allShotsGroup
                    allShotsGroup.add(shotSphere);
                    shotsPlotted++; 
                    isShot = true;

                    // Check outcome for other groups
                    const outcomeMetric = event.metrics.find(m => m && m.type === 'M37');
                    let outcome = null;
                    if (outcomeMetric && Array.isArray(outcomeMetric.value) && outcomeMetric.value.length > 0) {
                        outcome = outcomeMetric.value[0];
                    }

                    // Add CLONE to onTarget group if relevant
                    if (outcome === 'goal' || outcome === 'on_target') {
                        onTargetShotsGroup.add(shotSphere.clone());
                        onTargetPlotted++; 
                    }
                } 
            } 
        }
    });
    
    console.log(`Finished processing. Visualized ${passesPlotted} Passes, ${shotsPlotted} Shots (${onTargetPlotted} On Target), ${crossesPlotted} Crosses.`); // Update log

    // --- Set Initial View Based on Available Options --- 
    const viewOptions = Array.from(document.querySelectorAll('.view-option')); // Re-query options
    const initialView = viewOptions[currentViewIndex]?.getAttribute('data-view') || 'none'; 
    setActiveView(currentViewIndex); 
}

// --- Helper Function to Update Legend ---
/*
function updateLegend(team1Name, team2Name) { 
    const legendDiv = document.getElementById('legend');
    if (!legendDiv) return;

    let legendHTML = '<h4>Legend</h4>';
    if (team1Name) {
        legendHTML += `<div><span class="legend-color team1"></span> ${team1Name}</div>`;
    }
    if (team2Name) {
        legendHTML += `<div><span class="legend-color team2"></span> ${team2Name}</div>`;
    }
    // Remove outcome colors
    legendDiv.innerHTML = legendHTML;
}
*/

// Load and process the tactical data
async function loadTacticalData() {
    // Define necessary constants INSIDE the function or ensure they are accessible globally
    const TACTICAL_DATA_PATH = '/input_data/td.json'; // Correct absolute path from server root
    const FRAME_RATE = 25; // Assumption
    const DEFAULT_PITCH_LENGTH = 105; // Fallback
    const DEFAULT_PITCH_WIDTH = 68;   // Fallback
    const MAX_TIME_MINUTES = 90;    // For potential fallback scaling
    // Needs access to scene, passesGroup (global or passed), mapTo3D, visualizeTacticalData
    
    console.log(`Attempting full data load from ${TACTICAL_DATA_PATH}...`);
    try {
        const response = await fetch(TACTICAL_DATA_PATH);
        console.log(`Fetch response status: ${response.status}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const tacticalData = await response.json();
        console.log("Full tactical data loaded and parsed.");

        const dataMetadata = tacticalData.metadata;
        const events = tacticalData.data;
        if (!dataMetadata || !events) throw new Error("Invalid data structure");

        // --- Store Team Info from Metadata ---
        if (dataMetadata.home_team && dataMetadata.home_team.uuid && dataMetadata.home_team.name) {
            teamInfo.team1 = { uuid: dataMetadata.home_team.uuid, name: dataMetadata.home_team.name };
        }
        if (dataMetadata.away_team && dataMetadata.away_team.uuid && dataMetadata.away_team.name) {
            teamInfo.team2 = { uuid: dataMetadata.away_team.uuid, name: dataMetadata.away_team.name };
        }
        console.log("Stored Team Info:", JSON.stringify(teamInfo));
        // --------------------------------------

        // --- Populate Match Title & Color ---
        const matchTitleDiv = document.getElementById('match-title');
        if (matchTitleDiv && teamInfo.team1.name !== "Team 1" && teamInfo.team2.name !== "Team 2") {
            matchTitleDiv.textContent = `${teamInfo.team1.name} vs ${teamInfo.team2.name}`;
            // Apply gradient background based on updated hex colors
            const color1Hex = `#${TEAM1_COLOR.toString(16).padStart(6, '0')}`;
            const color2Hex = `#${TEAM2_COLOR.toString(16).padStart(6, '0')}`;
            matchTitleDiv.style.background = `linear-gradient(to right, ${color1Hex} 50%, ${color2Hex} 50%)`;
            matchTitleDiv.style.color = '#FFFFFF'; // Ensure text is white and readable
        } else if (matchTitleDiv) {
            matchTitleDiv.textContent = "Match Visualization"; // Fallback title
            matchTitleDiv.style.background = 'rgba(0, 0, 0, 0.7)'; // Fallback background
            matchTitleDiv.style.color = '#FFFFFF';
        }
        // --------------------------

        const pitchLength = dataMetadata.pitch_length || DEFAULT_PITCH_LENGTH;
        const pitchWidth = dataMetadata.pitch_width || DEFAULT_PITCH_WIDTH;

        // Check if pitch dimensions differ from constants; maybe update visualization if needed?
        // We might need to pass pitchLength/Width to visualizeTacticalData if mapTo3D needs them

        let maxFrame = events.reduce((max, event) => Math.max(max, event.end_frame !== null && event.end_frame !== undefined ? event.end_frame : event.start_frame || 0), 0);
        if (maxFrame === 0) {
            console.warn("Could not determine max frame. Estimating...");
            maxFrame = MAX_TIME_MINUTES * 60 * FRAME_RATE;
        }
        console.log(`Data contains frames up to: ${maxFrame}`);

        // Call the visualization function with the loaded data
        visualizeTacticalData(events, maxFrame, pitchLength, pitchWidth);

    } catch (error) {
        console.error('Failed during full data load/processing:', error);
    }
}

// --- Helper Function to Update View ---
function updateView(viewType) {
    // Set all to false initially
    passesGroup.visible = false;
    allShotsGroup.visible = false;
    onTargetShotsGroup.visible = false;
    // goalShotsGroup.visible = false; // Removed
    crossesGroup.visible = false;

    switch (viewType) {
        case 'none':
            // All remain false
            break;
        case 'passes':
            passesGroup.visible = true;
            break;
        case 'shots_all': 
            allShotsGroup.visible = true;
            break;
        case 'shots_on_target': 
            onTargetShotsGroup.visible = true;
            break;
        case 'crosses': 
            crossesGroup.visible = true;
            break;
        default:
            // All remain false
            break;
    }
    console.log(`View updated to: ${viewType}`);
}

// --- Throttling Function ---
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// --- State for Scrollable View Control ---
let currentViewIndex = 0; // Start at 'None'
let viewOptions = []; // Initialize as empty, populate after DOM loaded
const viewControlsDiv = document.getElementById('view-controls');
const optionsListDiv = document.getElementById('options-list');

// --- Function to Set Active View (UI and 3D) ---
function setActiveView(index) {
    if (index < 0 || index >= viewOptions.length || !viewControlsDiv || !optionsListDiv) return;

    const targetOption = viewOptions[index];
    
    // Update visual highlight state
    viewOptions.forEach((option, i) => {
        option.classList.toggle('active-view', i === index);
    });

    // Calculate vertical shift to center the target option
    const containerHeight = viewControlsDiv.clientHeight;
    const listTopOffset = optionsListDiv.offsetTop; // Should be 0 relative to parent if no margin/padding
    const optionTop = targetOption.offsetTop; // Relative to list container
    const optionHeight = targetOption.clientHeight;
    
    // Target position for the top of the option to center it
    const targetTop = (containerHeight / 2) - (optionHeight / 2);
    // How much to shift the entire list
    const translateY = targetTop - optionTop;

    // Apply the transform to the inner list
    optionsListDiv.style.transform = `translateY(${translateY}px)`;

    // Update 3D visibility
    const selectedViewType = targetOption.getAttribute('data-view');
    updateView(selectedViewType);
    
    currentViewIndex = index; // Update current index state
}

// --- Initialize View Options After DOM Load ---
function initializeViewOptions() {
    viewOptions = Array.from(document.querySelectorAll('.view-option')); // Re-query available options
    if (viewControlsDiv && viewOptions.length > 0 && optionsListDiv) {
        viewControlsDiv.addEventListener('wheel', throttledScrollHandler, { passive: false });
        // Ensure initial index is valid for the potentially shorter list
        currentViewIndex = Math.min(currentViewIndex, viewOptions.length - 1);
        setActiveView(currentViewIndex); 
    } else {
        console.error("Could not find view control elements for scroll listener during init.");
    }
}

// --- Wheel Event Listener --- 
const handleScroll = (event) => {
    event.preventDefault(); // Prevent page scrolling

    let newIndex = currentViewIndex;
    if (event.deltaY < 0) {
        // Scroll Up
        newIndex--;
    } else if (event.deltaY > 0) {
        // Scroll Down
        newIndex++;
    }

    // Clamp index within bounds [0, viewOptions.length - 1]
    newIndex = Math.max(0, Math.min(newIndex, viewOptions.length - 1));

    if (newIndex !== currentViewIndex) {
        setActiveView(newIndex);
    }
};
const throttledScrollHandler = throttle(handleScroll, 200);

// --- Event Listeners ---
window.addEventListener('resize', () => {
    // Needs access to camera, renderer
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}, false);

// --- Animation Loop ---
function animate() {
    // Needs access to controls, renderer, scene, camera
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// --- Main Execution ---
// Ensure global 'eventsGroup' is declared if visualizeTacticalData needs to remove the old one - REMOVED
// let eventsGroup; 

loadTacticalData().then(() => {
     initializeViewOptions();
}); 
animate();

// --- Chatbot Functionality ---

// Get DOM elements for chat
const chatbox = document.getElementById('chatbox');
const chatInput = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');
const chatHeader = document.querySelector('#chatbot-container h2'); // Get the H2 element
const backendUrl = 'http://localhost:3000/api/chat'; // Your backend URL

// Function to add a message to the chatbox
function addMessageToChatbox(message, sender) { // sender is 'user' or 'bot'
    if (!chatbox) {
        console.error("Chatbox element not found!");
        return;
    }
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', `${sender}-message`);
    messageElement.textContent = message; // Use textContent for security
    chatbox.appendChild(messageElement);
    // Scroll to the bottom
    chatbox.scrollTop = chatbox.scrollHeight;
}

// Function to send message to backend and display response
async function sendMessage() {
    if (!chatInput || !chatbox) {
         console.error("Chat input or chatbox element not found!");
         return;
    }
    const messageText = chatInput.value.trim();
    if (!messageText) return; // Don't send empty messages

    addMessageToChatbox(messageText, 'user');
    chatInput.value = ''; // Clear input field
    chatInput.disabled = true; // Disable input while waiting
    sendButton.disabled = true;

    // Add a temporary 'thinking' message
    const thinkingMessage = document.createElement('div');
    thinkingMessage.classList.add('chat-message', 'bot-message', 'thinking');
    thinkingMessage.textContent = 'Analyst is thinking...';
    chatbox.appendChild(thinkingMessage);
    chatbox.scrollTop = chatbox.scrollHeight;

    try {
        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: messageText }),
        });

        // Remove thinking message
        chatbox.removeChild(thinkingMessage);

        if (!response.ok) {
            // Try to parse error JSON, otherwise use status text
            let errorMsg = `Error: ${response.statusText}`;
            try {
                const errorData = await response.json();
                errorMsg = errorData.error || errorData.reply || errorMsg;
                console.error('Error from backend:', response.status, errorData);
            } catch (e) {
                console.error('Error from backend (non-JSON response): ', response.status, await response.text());
            }
            addMessageToChatbox(errorMsg, 'bot');
        } else {
            const data = await response.json();
            addMessageToChatbox(data.reply, 'bot');
            // Update chat header if model name is received
            if (data.model && chatHeader) {
                chatHeader.textContent = `Gemini (${data.model})`;
            }
        }

    } catch (error) {
        console.error('Error sending message:', error);
        // Remove thinking message if it exists
        const thinking = chatbox.querySelector('.thinking');
        if (thinking) {
             chatbox.removeChild(thinking);
        }
        addMessageToChatbox('Could not connect to the analyst. Please ensure the backend server is running and reachable.', 'bot');
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.focus(); // Set focus back to input field
    }
}

// Event Listeners (check if elements exist first)
if (sendButton) {
    sendButton.addEventListener('click', sendMessage);
} else {
    console.error("Send button not found!");
}

if (chatInput) {
    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
} else {
     console.error("Chat input not found!");
}

// Add an initial greeting from the bot if chatbox exists
if (chatbox) {
    // Set initial header text (optional)
    if (chatHeader) {
        chatHeader.textContent = 'Gemini Game Analyst';
    }
    addMessageToChatbox('Hello! Ask me anything about the Chelsea vs West Ham game.', 'bot');
} else {
    console.error("Cannot add initial message: Chatbox not found!");
}

// --- End Chatbot Functionality ---