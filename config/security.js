require('dotenv').config();

const securityConfig = {
    // Content Security Policy
    csp: process.env.CSP_DIRECTIVES || "default-src 'self'; script-src 'self' https://tp.media https://c121.travelpayouts.com; style-src 'self' 'unsafe-inline';",
    
    // CORS Configuration
    cors: {
        origin: JSON.parse(process.env.CORS_ALLOWED_ORIGINS || '["https://akiko-adventures.web.app"]'),
        methods: ['GET', 'POST'],
        allowedHeaders: ['Content-Type', 'Authorization'],
        credentials: true
    },

    // Rate Limiting
    rateLimit: {
        windowMs: parseInt(process.env.RATE_LIMIT_DURATION || '3600') * 1000,
        max: parseInt(process.env.RATE_LIMIT_REQUESTS || '100')
    },

    // Security Headers
    headers: {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    },

    // Cookie Settings
    cookies: {
        secure: true,
        httpOnly: true,
        sameSite: 'strict'
    }
};

module.exports = securityConfig; 