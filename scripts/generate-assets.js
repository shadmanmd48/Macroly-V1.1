const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const assetsDir = path.join(__dirname, '..', 'assets');
if (!fs.existsSync(assetsDir)) {
  fs.mkdirSync(assetsDir, { recursive: true });
}

// 1. Full Icon SVG (1024x1024)
const iconSvg = `
<svg width="1024" height="1024" viewBox="0 0 1024 1024" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="squircleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#182c21" />
      <stop offset="100%" stop-color="#090f0b" />
    </linearGradient>
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#86efac" />
      <stop offset="50%" stop-color="#4ade80" />
      <stop offset="100%" stop-color="#22c55e" />
    </linearGradient>
    <linearGradient id="leafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#bbf7d0" />
      <stop offset="100%" stop-color="#34d399" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#22c55e" flood-opacity="0.4" />
    </filter>
  </defs>
  <rect width="1024" height="1024" rx="220" fill="url(#squircleGrad)" stroke="#4ade80" stroke-width="12" stroke-opacity="0.3" />
  
  <g transform="translate(180, 180) scale(16.6)" filter="url(#glow)">
    <!-- Sprouting Leaf -->
    <g transform="translate(22, 6) scale(0.62)">
      <path d="M4 14 C4 6 11 1 18 0 C18 7 13 14 4 14 Z" fill="url(#leafGrad)" />
      <path d="M5.5 12.5 Q11 7 16 2" stroke="#166534" stroke-width="1.3" stroke-linecap="round" />
    </g>
    <!-- Rounded 'm' Glyph -->
    <path d="M8 29 V19 C8 15 11 12.5 14.5 12.5 C18 12.5 20 15 20 19 V29 M20 19 C20 15 23 12.5 26.5 12.5 C30 12.5 32 15 32 19 V29"
          stroke="url(#greenGrad)" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
  </g>
</svg>
`;

// 2. Icon Foreground SVG (adaptive icon safe zone)
const iconForegroundSvg = `
<svg width="1024" height="1024" viewBox="0 0 1024 1024" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#86efac" />
      <stop offset="50%" stop-color="#4ade80" />
      <stop offset="100%" stop-color="#22c55e" />
    </linearGradient>
    <linearGradient id="leafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#bbf7d0" />
      <stop offset="100%" stop-color="#34d399" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#22c55e" flood-opacity="0.4" />
    </filter>
  </defs>
  
  <g transform="translate(240, 240) scale(13.6)" filter="url(#glow)">
    <!-- Sprouting Leaf -->
    <g transform="translate(22, 6) scale(0.62)">
      <path d="M4 14 C4 6 11 1 18 0 C18 7 13 14 4 14 Z" fill="url(#leafGrad)" />
      <path d="M5.5 12.5 Q11 7 16 2" stroke="#166534" stroke-width="1.3" stroke-linecap="round" />
    </g>
    <!-- Rounded 'm' Glyph -->
    <path d="M8 29 V19 C8 15 11 12.5 14.5 12.5 C18 12.5 20 15 20 19 V29 M20 19 C20 15 23 12.5 26.5 12.5 C30 12.5 32 15 32 19 V29"
          stroke="url(#greenGrad)" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
  </g>
</svg>
`;

// 3. Icon Background SVG (adaptive icon background)
const iconBackgroundSvg = `
<svg width="1024" height="1024" viewBox="0 0 1024 1024" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#14241b" />
      <stop offset="100%" stop-color="#080e0a" />
    </linearGradient>
  </defs>
  <rect width="1024" height="1024" fill="url(#bgGrad)" />
</svg>
`;

// 4. Splash Screen SVG (2732x2732)
const splashSvg = `
<svg width="2732" height="2732" viewBox="0 0 2732 2732" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="splashBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f1b14" />
      <stop offset="50%" stop-color="#090f0b" />
      <stop offset="100%" stop-color="#050806" />
    </linearGradient>
    <linearGradient id="squircleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1c3326" />
      <stop offset="100%" stop-color="#0a120c" />
    </linearGradient>
    <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#86efac" />
      <stop offset="50%" stop-color="#4ade80" />
      <stop offset="100%" stop-color="#22c55e" />
    </linearGradient>
    <linearGradient id="leafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#bbf7d0" />
      <stop offset="100%" stop-color="#34d399" />
    </linearGradient>
    <filter id="splashGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="24" flood-color="#22c55e" flood-opacity="0.45" />
    </filter>
  </defs>
  <rect width="2732" height="2732" fill="url(#splashBg)" />
  
  <!-- Centered Logo Card -->
  <g transform="translate(1086, 960)">
    <rect width="560" height="560" rx="140" fill="url(#squircleGrad)" stroke="#4ade80" stroke-width="8" stroke-opacity="0.35" />
    
    <g transform="translate(80, 80) scale(10)" filter="url(#splashGlow)">
      <!-- Sprouting Leaf -->
      <g transform="translate(22, 6) scale(0.62)">
        <path d="M4 14 C4 6 11 1 18 0 C18 7 13 14 4 14 Z" fill="url(#leafGrad)" />
        <path d="M5.5 12.5 Q11 7 16 2" stroke="#166534" stroke-width="1.3" stroke-linecap="round" />
      </g>
      <!-- Rounded 'm' Glyph -->
      <path d="M8 29 V19 C8 15 11 12.5 14.5 12.5 C18 12.5 20 15 20 19 V29 M20 19 C20 15 23 12.5 26.5 12.5 C30 12.5 32 15 32 19 V29"
            stroke="url(#greenGrad)" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" />
      </g>
  </g>
  
  <!-- Text Brand -->
  <text x="1366" y="1640" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="72" font-weight="800" fill="#f0fdf4" letter-spacing="8">MACROLY</text>
  <text x="1366" y="1710" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="34" font-weight="500" fill="#86efac" letter-spacing="2">AI Nutrition &amp; Macro Tracker</text>
</svg>
`;

async function main() {
  console.log('Generating asset PNGs...');
  
  await sharp(Buffer.from(iconSvg)).png().toFile(path.join(assetsDir, 'icon-only.png'));
  await sharp(Buffer.from(iconSvg)).png().toFile(path.join(assetsDir, 'logo.png'));
  await sharp(Buffer.from(iconForegroundSvg)).png().toFile(path.join(assetsDir, 'icon-foreground.png'));
  await sharp(Buffer.from(iconBackgroundSvg)).png().toFile(path.join(assetsDir, 'icon-background.png'));
  await sharp(Buffer.from(splashSvg)).png().toFile(path.join(assetsDir, 'splash.png'));
  await sharp(Buffer.from(splashSvg)).png().toFile(path.join(assetsDir, 'splash-dark.png'));
  
  console.log('Generated all source PNGs in assets/ successfully.');
}

main().catch(err => {
  console.error('Asset generation error:', err);
  process.exit(1);
});
