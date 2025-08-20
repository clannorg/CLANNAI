const express = require('express');
const router = express.Router();
const { Pool } = require('pg');
const { createHLSJob, getJobStatus } = require('../utils/mediaconvert');

// Database connection
const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT || 5432,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Convert game video to HLS
router.post('/convert/:gameId', async (req, res) => {
  const { gameId } = req.params;
  
  try {
    // Get game details
    const gameResult = await pool.query('SELECT * FROM games WHERE id = $1', [gameId]);
    if (gameResult.rows.length === 0) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    const game = gameResult.rows[0];
    if (!game.s3_url) {
      return res.status(400).json({ error: 'Game has no video URL' });
    }

    // Check if HLS conversion already exists or is in progress
    const existingHLS = await pool.query(
      'SELECT * FROM hls_conversions WHERE game_id = $1 ORDER BY created_at DESC LIMIT 1',
      [gameId]
    );

    if (existingHLS.rows.length > 0) {
      const existing = existingHLS.rows[0];
      if (existing.status === 'COMPLETE') {
        return res.json({
          message: 'HLS conversion already exists',
          hlsUrl: existing.hls_url,
          status: existing.status
        });
      } else if (existing.status === 'IN_PROGRESS') {
        // Check current status
        const jobStatus = await getJobStatus(existing.job_id);
        await pool.query(
          'UPDATE hls_conversions SET status = $1, progress = $2 WHERE id = $3',
          [jobStatus.status, jobStatus.progress, existing.id]
        );
        
        return res.json({
          message: 'HLS conversion in progress',
          jobId: existing.job_id,
          status: jobStatus.status,
          progress: jobStatus.progress
        });
      }
    }

    // Create HLS conversion job
    const outputPath = `hls/${gameId}`;
    const jobResult = await createHLSJob(game.s3_url, outputPath, gameId);
    
    // Store job details in database
    const hlsUrl = `${jobResult.outputPath}index.m3u8`;
    await pool.query(
      `INSERT INTO hls_conversions (game_id, job_id, status, hls_url, output_path, created_at) 
       VALUES ($1, $2, $3, $4, $5, NOW())`,
      [gameId, jobResult.jobId, 'IN_PROGRESS', hlsUrl, outputPath]
    );

    res.json({
      message: 'HLS conversion started',
      jobId: jobResult.jobId,
      status: 'IN_PROGRESS',
      estimatedTime: '5-10 minutes'
    });

  } catch (error) {
    console.error('Error starting HLS conversion:', error);
    res.status(500).json({ error: 'Failed to start HLS conversion' });
  }
});

// Check conversion status
router.get('/status/:gameId', async (req, res) => {
  const { gameId } = req.params;
  
  try {
    const result = await pool.query(
      'SELECT * FROM hls_conversions WHERE game_id = $1 ORDER BY created_at DESC LIMIT 1',
      [gameId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'No HLS conversion found for this game' });
    }

    const conversion = result.rows[0];
    
    if (conversion.status === 'IN_PROGRESS') {
      // Get latest status from MediaConvert
      const jobStatus = await getJobStatus(conversion.job_id);
      
      // Update database
      await pool.query(
        'UPDATE hls_conversions SET status = $1, progress = $2, updated_at = NOW() WHERE id = $3',
        [jobStatus.status, jobStatus.progress, conversion.id]
      );
      
      res.json({
        status: jobStatus.status,
        progress: jobStatus.progress,
        hlsUrl: jobStatus.status === 'COMPLETE' ? conversion.hls_url : null
      });
    } else {
      res.json({
        status: conversion.status,
        progress: conversion.progress || 100,
        hlsUrl: conversion.status === 'COMPLETE' ? conversion.hls_url : null
      });
    }

  } catch (error) {
    console.error('Error checking HLS status:', error);
    res.status(500).json({ error: 'Failed to check HLS status' });
  }
});

// Get HLS URL for a game
router.get('/url/:gameId', async (req, res) => {
  const { gameId } = req.params;
  
  try {
    const result = await pool.query(
      'SELECT hls_url FROM hls_conversions WHERE game_id = $1 AND status = $2 ORDER BY created_at DESC LIMIT 1',
      [gameId, 'COMPLETE']
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'No completed HLS conversion found' });
    }

    res.json({
      hlsUrl: result.rows[0].hls_url,
      available: true
    });

  } catch (error) {
    console.error('Error getting HLS URL:', error);
    res.status(500).json({ error: 'Failed to get HLS URL' });
  }
});

module.exports = router;