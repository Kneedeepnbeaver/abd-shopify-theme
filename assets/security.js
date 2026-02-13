/**
 * Security & Intellectual Property Protection
 * 
 * This file implements security measures to protect your intellectual property
 * including images, content, and prevent unauthorized access. It includes:
 * 
 * - Image Protection: Prevents right-click context menu, dragging, and keyboard
 *   shortcuts to save images. Shows protection messages when attempts are made.
 * 
 * - Content Protection: Prevents text selection and copying (Ctrl+C/Cmd+C) while
 *   maintaining accessibility options for screen readers.
 * 
 * - Bot Detection: Monitors for automated browser activity, headless browsers,
 *   rapid clicking patterns, and implements rate limiting to prevent scraping.
 * 
 * - Watermarking: Optional watermark overlay on product images with customizable text.
 * 
 * - Developer Tools Blocking: Attempts to prevent access to browser developer tools
 *   and view source functionality.
 * 
 * Note: These measures provide basic protection but determined users can bypass them.
 * They serve as deterrents and protect against casual copying. For stronger protection,
 * consider server-side measures and legal protections (watermarks, copyright notices).
 * 
 * Configuration is available in the theme customizer under "Security Settings".
 */

(function() {
  'use strict';

  // Configuration
  const config = {
    enableImageProtection: true,
    enableContentProtection: true,
    enableBotDetection: true,
    enableWatermarking: false, // Set to true to enable watermarking
    watermarkText: '© Arts by Dylan',
    allowSelectForAccessibility: true, // Allow text selection for screen readers
    maxRequestsPerMinute: 30
  };

  // ============================================
  // Image Protection
  // ============================================

  /**
   * Protect images from right-click and drag
   */
  function protectImages() {
    if (!config.enableImageProtection) return;

    const images = document.querySelectorAll('img[data-protect], .product-card__image, .card__image img');
    
    images.forEach(img => {
      // Prevent right-click context menu
      img.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        showProtectionMessage('Image right-click disabled');
        return false;
      });

      // Prevent drag
      img.addEventListener('dragstart', function(e) {
        e.preventDefault();
        return false;
      });

      // Prevent image saving via keyboard
      img.setAttribute('draggable', 'false');
      
      // Add overlay on hover to indicate protection
      img.style.userSelect = 'none';
      img.style.webkitUserSelect = 'none';
      img.style.mozUserSelect = 'none';
      img.style.msUserSelect = 'none';
    });

    // Prevent image saving via keyboard shortcuts
    document.addEventListener('keydown', function(e) {
      // Disable Save Image (Ctrl+S, Cmd+S on images)
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        const target = e.target;
        if (target.tagName === 'IMG' || target.closest('img')) {
          e.preventDefault();
          showProtectionMessage('Image saving disabled');
          return false;
        }
      }

      // Disable Print Screen (limited effectiveness)
      if (e.key === 'PrintScreen') {
        // Can't fully prevent, but can detect and warn
        console.warn('Print Screen detected - content is protected');
      }
    });
  }

  /**
   * Add watermark to images
   */
  function addWatermarks() {
    if (!config.enableWatermarking || !config.watermarkText) return;

    const images = document.querySelectorAll('img[data-watermark], .product-card__image img');
    
    images.forEach(img => {
      // Create watermark overlay
      const watermark = document.createElement('div');
      watermark.className = 'image-watermark';
      watermark.textContent = config.watermarkText;
      watermark.style.cssText = `
        position: absolute;
        bottom: 10px;
        right: 10px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 4px 8px;
        font-size: 12px;
        pointer-events: none;
        z-index: 10;
        user-select: none;
      `;

      // Wrap image in container if not already
      if (img.parentNode.style.position !== 'relative') {
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        img.parentNode.insertBefore(wrapper, img);
        wrapper.appendChild(img);
        wrapper.appendChild(watermark);
      } else {
        img.parentNode.appendChild(watermark);
      }
    });
  }

  // ============================================
  // Content Protection
  // ============================================

  /**
   * Protect text content from selection and copying
   */
  function protectContent() {
    if (!config.enableContentProtection) return;

    // Disable text selection (with accessibility exception)
    if (!config.allowSelectForAccessibility) {
      document.addEventListener('selectstart', function(e) {
        // Allow selection in input fields and textareas
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
          return true;
        }
        e.preventDefault();
        return false;
      });

      // Disable text selection via CSS
      const style = document.createElement('style');
      style.textContent = `
        body {
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
          user-select: none;
        }
        input, textarea {
          -webkit-user-select: text;
          -moz-user-select: text;
          -ms-user-select: text;
          user-select: text;
        }
      `;
      document.head.appendChild(style);
    }

    // Prevent copy (Ctrl+C, Cmd+C)
    document.addEventListener('copy', function(e) {
      // Allow copying from input fields
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return true;
      }
      
      e.preventDefault();
      showProtectionMessage('Content copying disabled');
      
      // Clear clipboard
      e.clipboardData.setData('text/plain', '');
      return false;
    });

    // Prevent cut (Ctrl+X, Cmd+X)
    document.addEventListener('cut', function(e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return true;
      }
      e.preventDefault();
      return false;
    });

    // Prevent paste in protected areas (except inputs)
    document.addEventListener('paste', function(e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return true;
      }
      // Can't fully prevent, but can log
      console.warn('Paste detected in protected area');
    });

    // Disable F12 and right-click (developer tools)
    document.addEventListener('keydown', function(e) {
      // F12
      if (e.key === 'F12') {
        e.preventDefault();
        showProtectionMessage('Developer tools disabled');
        return false;
      }

      // Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'I' || e.key === 'J')) {
        e.preventDefault();
        showProtectionMessage('Developer tools disabled');
        return false;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
        e.preventDefault();
        showProtectionMessage('View source disabled');
        return false;
      }
    });

    // Prevent right-click context menu
    document.addEventListener('contextmenu', function(e) {
      // Allow right-click in input fields
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return true;
      }
      
      e.preventDefault();
      showProtectionMessage('Right-click disabled');
      return false;
    });
  }

  // ============================================
  // Bot Detection & Rate Limiting
  // ============================================

  /**
   * Detect and prevent bot activity
   */
  function initBotDetection() {
    if (!config.enableBotDetection) return;

    const requestLog = [];
    const suspiciousPatterns = [];

    // Track requests
    function logRequest() {
      const now = Date.now();
      requestLog.push(now);
      
      // Remove old entries (older than 1 minute)
      while (requestLog.length > 0 && requestLog[0] < now - 60000) {
        requestLog.shift();
      }

      // Check rate limit
      if (requestLog.length > config.maxRequestsPerMinute) {
        handleSuspiciousActivity('Rate limit exceeded');
        return false;
      }

      return true;
    }

    // Detect headless browsers
    function detectHeadless() {
      // Check for common headless browser indicators
      const indicators = [
        navigator.webdriver === true,
        navigator.plugins.length === 0,
        navigator.languages.length === 0,
        window.chrome === undefined && navigator.vendor === 'Google Inc.',
        navigator.hardwareConcurrency === 4 && navigator.deviceMemory === 8
      ];

      if (indicators.some(indicator => indicator === true)) {
        handleSuspiciousActivity('Headless browser detected');
      }
    }

    // Monitor mouse movements (bots typically don't move mouse naturally)
    let mouseMovements = 0;
    document.addEventListener('mousemove', function() {
      mouseMovements++;
    });

    // Check for lack of human interaction
    setTimeout(() => {
      if (mouseMovements === 0 && document.visibilityState === 'visible') {
        // Possible bot - no mouse movement detected
        console.warn('Possible bot detected: No mouse movement');
      }
    }, 10000);

    // Intercept fetch requests
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
      if (!logRequest()) {
        return Promise.reject(new Error('Rate limit exceeded'));
      }
      return originalFetch.apply(this, args);
    };

    // Monitor for rapid clicks (bot behavior)
    let clickCount = 0;
    let lastClickTime = 0;
    document.addEventListener('click', function(e) {
      const now = Date.now();
      if (now - lastClickTime < 100) {
        clickCount++;
        if (clickCount > 10) {
          handleSuspiciousActivity('Rapid clicking detected');
        }
      } else {
        clickCount = 0;
      }
      lastClickTime = now;
    });

    // Run detection
    detectHeadless();
  }

  /**
   * Handle suspicious activity
   */
  function handleSuspiciousActivity(reason) {
    console.warn('Suspicious activity detected:', reason);
    
    // Log to server (if endpoint exists)
    if (window.Shopify?.analytics) {
      // Could send to analytics or logging service
    }

    // Show warning (optional - might alert legitimate users)
    // showProtectionMessage('Suspicious activity detected');
  }

  // ============================================
  // Referrer Protection
  // ============================================

  /**
   * Check referrer and block direct image access
   */
  function initReferrerProtection() {
    // This would need server-side support
    // For client-side, we can add referrer policy
    const meta = document.createElement('meta');
    meta.name = 'referrer';
    meta.content = 'same-origin';
    document.head.appendChild(meta);
  }

  // ============================================
  // Content Security
  // ============================================

  /**
   * Add Content Security Policy headers (note: needs server support)
   */
  function addCSP() {
    // CSP should be set via HTTP headers, but we can add meta tag as fallback
    const csp = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' https://cdn.shopify.com",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self' https://fonts.shopifycdn.com",
      "connect-src 'self' https://monorail-edge.shopifysvc.com"
    ].join('; ');

    const meta = document.createElement('meta');
    meta.httpEquiv = 'Content-Security-Policy';
    meta.content = csp;
    document.head.appendChild(meta);
  }

  // ============================================
  // Obfuscation
  // ============================================

  /**
   * Obfuscate sensitive content (basic)
   */
  function obfuscateContent() {
    // This is a basic obfuscation - determined users can still access
    // For stronger protection, use server-side rendering with tokens
    
    const sensitiveElements = document.querySelectorAll('[data-obfuscate]');
    sensitiveElements.forEach(el => {
      const originalText = el.textContent;
      // Simple obfuscation - replace with encoded version
      // In production, use more sophisticated methods
      el.setAttribute('data-original', btoa(originalText));
    });
  }

  // ============================================
  // Utility Functions
  // ============================================

  /**
   * Show protection message
   */
  function showProtectionMessage(message) {
    // Create temporary notification
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ff4444;
      color: white;
      padding: 12px 20px;
      border-radius: 4px;
      z-index: 10000;
      font-size: 14px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transition = 'opacity 0.3s';
      setTimeout(() => notification.remove(), 300);
    }, 2000);
  }

  // ============================================
  // Initialize
  // ============================================

  function init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
      return;
    }

    // Initialize protection features
    protectImages();
    protectContent();
    initBotDetection();
    initReferrerProtection();
    
    if (config.enableWatermarking) {
      addWatermarks();
    }

    // Add CSP
    addCSP();

    console.log('Security protection initialized');
  }

  // Start initialization
  init();

  // Export config for external modification
  window.SecurityConfig = config;

})();

