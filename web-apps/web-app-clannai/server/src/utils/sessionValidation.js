const isValidSessionUrl = (url) => {
    if (!url) return false;
    return url.includes('veo.co') ||
        url.includes('youtu.be') ||
        url.includes('youtube.com');
};

module.exports = { isValidSessionUrl }; 