import React, { useState, useEffect } from 'react';
import teamService from '../services/teamService';

function TeamColorManager({ teamId, isAdmin, onColorsUpdated }) {
  const [colors, setColors] = useState({
    home_color: '#D1FB7A',
    away_color: '#1B365D'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [editingColor, setEditingColor] = useState(null); // 'home' or 'away'

  const colorPresets = [
    { name: 'Clann Green', value: '#D1FB7A' },
    { name: 'Team Green', value: '#016F32' },
    { name: 'Navy Blue', value: '#1B365D' },
    { name: 'Royal Blue', value: '#0047AB' },
    { name: 'Maroon', value: '#7A263A' },
    { name: 'Forest Green', value: '#228B22' },
    { name: 'Deep Purple', value: '#4B0082' },
    { name: 'Orange', value: '#FF6B35' },
    { name: 'Red', value: '#DC143C' },
    { name: 'Black', value: '#2C2C2C' },
    { name: 'Gold', value: '#FFD700' },
    { name: 'Silver', value: '#C0C0C0' }
  ];

  useEffect(() => {
    if (teamId) {
      fetchTeamColors();
    }
  }, [teamId]);

  const fetchTeamColors = async () => {
    try {
      setLoading(true);
      const teamData = await teamService.getTeamColors(teamId);
      setColors({
        home_color: teamData.home_color || '#D1FB7A',
        away_color: teamData.away_color || '#1B365D'
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleColorUpdate = async (colorType, newColor) => {
    if (!isAdmin) {
      setError('Only team admins can change colors');
      return;
    }

    try {
      setLoading(true);
      const updateData = {
        [colorType]: newColor
      };
      
      const updatedTeam = await teamService.updateTeamColors(teamId, updateData);
      
      setColors({
        home_color: updatedTeam.home_color,
        away_color: updatedTeam.away_color
      });
      
      if (onColorsUpdated) {
        onColorsUpdated(updatedTeam);
      }
      
      setShowColorPicker(false);
      setEditingColor(null);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const openColorPicker = (colorType) => {
    if (!isAdmin) {
      setError('Only team admins can change colors');
      return;
    }
    setEditingColor(colorType);
    setShowColorPicker(true);
    setError(null);
  };

  if (loading && !colors.home_color) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="flex space-x-4">
            <div className="h-12 bg-gray-200 rounded w-24"></div>
            <div className="h-12 bg-gray-200 rounded w-24"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-gray-900">Team Colors</h3>
        {!isAdmin && (
          <span className="text-sm text-gray-500">Admin only</span>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Home Color */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Home Color
          </label>
          <div 
            className={`w-full h-16 rounded-lg border-2 flex items-center justify-center cursor-pointer transition-all ${
              isAdmin 
                ? 'border-gray-300 hover:border-gray-400' 
                : 'border-gray-200 cursor-not-allowed opacity-75'
            }`}
            style={{ backgroundColor: colors.home_color }}
            onClick={() => openColorPicker('home_color')}
          >
            <span className="text-white font-medium drop-shadow-lg">
              {colors.home_color}
            </span>
          </div>
        </div>

        {/* Away Color */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Away Color
          </label>
          <div 
            className={`w-full h-16 rounded-lg border-2 flex items-center justify-center cursor-pointer transition-all ${
              isAdmin 
                ? 'border-gray-300 hover:border-gray-400' 
                : 'border-gray-200 cursor-not-allowed opacity-75'
            }`}
            style={{ backgroundColor: colors.away_color }}
            onClick={() => openColorPicker('away_color')}
          >
            <span className="text-white font-medium drop-shadow-lg">
              {colors.away_color}
            </span>
          </div>
        </div>
      </div>

      {/* Color Picker Modal */}
      {showColorPicker && editingColor && isAdmin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-semibold">
                Choose {editingColor === 'home_color' ? 'Home' : 'Away'} Color
              </h4>
              <button
                onClick={() => {
                  setShowColorPicker(false);
                  setEditingColor(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            {/* Color Presets */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              {colorPresets.map((preset) => (
                <button
                  key={preset.name}
                  className="h-12 rounded-lg border-2 border-gray-300 hover:border-gray-400 transition-all flex items-center justify-center text-xs font-medium text-white drop-shadow"
                  style={{ backgroundColor: preset.value }}
                  onClick={() => handleColorUpdate(editingColor, preset.value)}
                  title={preset.name}
                >
                  {preset.name}
                </button>
              ))}
            </div>

            {/* Custom Color Input */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Color (Hex)
              </label>
              <div className="flex gap-2">
                <input
                  type="color"
                  className="w-12 h-10 rounded border border-gray-300"
                  value={colors[editingColor]}
                  onChange={(e) => {
                    setColors(prev => ({
                      ...prev,
                      [editingColor]: e.target.value
                    }));
                  }}
                />
                <input
                  type="text"
                  className="flex-1 p-2 border border-gray-300 rounded"
                  placeholder="#FFFFFF"
                  value={colors[editingColor]}
                  onChange={(e) => {
                    setColors(prev => ({
                      ...prev,
                      [editingColor]: e.target.value
                    }));
                  }}
                />
                <button
                  onClick={() => handleColorUpdate(editingColor, colors[editingColor])}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                  disabled={loading}
                >
                  Apply
                </button>
              </div>
            </div>

            {/* Preview */}
            <div className="text-center">
              <div 
                className="w-full h-12 rounded-lg flex items-center justify-center mx-auto"
                style={{ backgroundColor: colors[editingColor] }}
              >
                <span className="text-white font-medium drop-shadow">
                  Preview
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TeamColorManager;