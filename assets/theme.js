/**
 * Theme JavaScript
 * 
 * This file provides all the interactive functionality for the theme. It handles:
 * - Cart AJAX updates: Add, update, and remove items from cart without page reload
 * - Variant selection: Dynamic price and image updates when product variants change
 * - Mobile menu: Toggle functionality for mobile navigation
 * - Form validation: Client-side validation with real-time feedback
 * - Notifications: Success and error messages for user actions
 * - Loading states: Visual feedback during async operations
 * 
 * All functions are namespaced under window.Theme for external access.
 * The code uses modern JavaScript (ES6+) and includes error handling.
 */

(function() {
  'use strict';

  // ============================================
  // Cart Functionality
  // ============================================

  /**
   * Add product to cart via AJAX
   */
  async function addToCart(formData) {
    try {
      const response = await fetch('/cart/add.js', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.description || 'Failed to add item to cart');
      }

      const item = await response.json();
      updateCartCount();
      showNotification('Item added to cart', 'success');
      return item;
    } catch (error) {
      showNotification(error.message || 'Error adding item to cart', 'error');
      throw error;
    }
  }

  /**
   * Update cart item quantity
   */
  async function updateCartItem(key, quantity) {
    try {
      const response = await fetch('/cart/change.js', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: key,
          quantity: quantity
        })
      });

      if (!response.ok) {
        throw new Error('Failed to update cart');
      }

      const cart = await response.json();
      updateCartUI(cart);
      return cart;
    } catch (error) {
      showNotification('Error updating cart', 'error');
      throw error;
    }
  }

  /**
   * Remove item from cart
   */
  async function removeCartItem(key) {
    try {
      const response = await fetch('/cart/change.js', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: key,
          quantity: 0
        })
      });

      if (!response.ok) {
        throw new Error('Failed to remove item');
      }

      const cart = await response.json();
      updateCartUI(cart);
      showNotification('Item removed from cart', 'success');
      return cart;
    } catch (error) {
      showNotification('Error removing item', 'error');
      throw error;
    }
  }

  /**
   * Get current cart
   */
  async function getCart() {
    try {
      const response = await fetch('/cart.js');
      if (!response.ok) throw new Error('Failed to fetch cart');
      return await response.json();
    } catch (error) {
      console.error('Cart fetch error:', error);
      return null;
    }
  }

  /**
   * Update cart count in header
   */
  async function updateCartCount() {
    const cart = await getCart();
    if (cart) {
      const cartCountElements = document.querySelectorAll('[data-cart-count]');
      cartCountElements.forEach(el => {
        el.textContent = cart.item_count || 0;
        el.style.display = cart.item_count > 0 ? 'inline' : 'none';
      });
    }
  }

  /**
   * Update cart UI (for cart page)
   */
  function updateCartUI(cart) {
    if (window.location.pathname === '/cart') {
      // Reload cart page to show updated cart
      window.location.reload();
    } else {
      updateCartCount();
    }
  }

  // ============================================
  // Product Variant Selection
  // ============================================

  /**
   * Handle variant selection changes
   */
  function initVariantSelection() {
    const variantSelects = document.querySelectorAll('[name="id"]');
    
    variantSelects.forEach(select => {
      select.addEventListener('change', async function() {
        const variantId = this.value;
        await updateVariantInfo(variantId);
      });
    });

    // Handle radio buttons for variant options
    const variantInputs = document.querySelectorAll('input[type="radio"][name^="option"]');
    variantInputs.forEach(input => {
      input.addEventListener('change', function() {
        updateVariantFromOptions();
      });
    });
  }

  /**
   * Update variant price and availability
   */
  async function updateVariantInfo(variantId) {
    try {
      const product = window.productData;
      if (!product) return;

      const variant = product.variants.find(v => v.id == variantId);
      if (!variant) return;

      // Update price
      const priceElements = document.querySelectorAll('[data-product-price]');
      priceElements.forEach(el => {
        el.textContent = formatMoney(variant.price);
      });

      // Update compare at price
      if (variant.compare_at_price && variant.compare_at_price > variant.price) {
        const comparePriceElements = document.querySelectorAll('[data-compare-price]');
        comparePriceElements.forEach(el => {
          el.textContent = formatMoney(variant.compare_at_price);
          el.style.display = 'inline';
        });
      } else {
        document.querySelectorAll('[data-compare-price]').forEach(el => {
          el.style.display = 'none';
        });
      }

      // Update availability
      const addToCartBtn = document.querySelector('[data-add-to-cart]');
      if (addToCartBtn) {
        if (variant.available) {
          addToCartBtn.disabled = false;
          addToCartBtn.textContent = 'Add to cart';
        } else {
          addToCartBtn.disabled = true;
          addToCartBtn.textContent = 'Sold out';
        }
      }

      // Update variant image if available
      if (variant.featured_image) {
        const mainImage = document.querySelector('[data-product-image]');
        if (mainImage) {
          mainImage.src = variant.featured_image.src;
          mainImage.alt = variant.featured_image.alt || product.title;
        }
      }
    } catch (error) {
      console.error('Variant update error:', error);
    }
  }

  /**
   * Update variant from option selections
   */
  function updateVariantFromOptions() {
    const selectedOptions = {};
    document.querySelectorAll('input[type="radio"][name^="option"]:checked').forEach(input => {
      const optionName = input.name.replace('option', '');
      selectedOptions[optionName] = input.value;
    });

    // Find matching variant
    const product = window.productData;
    if (!product) return;

    const variant = product.variants.find(v => {
      return Object.keys(selectedOptions).every(opt => {
        return v.options[parseInt(opt) - 1] === selectedOptions[opt];
      });
    });

    if (variant) {
      const variantSelect = document.querySelector('[name="id"]');
      if (variantSelect) {
        variantSelect.value = variant.id;
        variantSelect.dispatchEvent(new Event('change'));
      }
    }
  }

  // ============================================
  // Mobile Menu
  // ============================================

  /**
   * Initialize mobile menu toggle
   */
  function initMobileMenu() {
    const menuToggle = document.querySelector('[data-mobile-menu-toggle]');
    const menuClose = document.querySelector('[data-mobile-menu-close]');
    const menu = document.querySelector('[data-mobile-menu]');
    const body = document.body;

    if (!menuToggle || !menu) return;

    menuToggle.addEventListener('click', function(e) {
      e.preventDefault();
      openMobileMenu();
    });

    if (menuClose) {
      menuClose.addEventListener('click', function(e) {
        e.preventDefault();
        closeMobileMenu();
      });
    }

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
      if (menu.classList.contains('is-open') && 
          !menu.contains(e.target) && 
          !menuToggle.contains(e.target)) {
        closeMobileMenu();
      }
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && menu.classList.contains('is-open')) {
        closeMobileMenu();
      }
    });
  }

  function openMobileMenu() {
    const menu = document.querySelector('[data-mobile-menu]');
    const body = document.body;
    if (menu) {
      menu.classList.add('is-open');
      body.classList.add('menu-open');
      body.style.overflow = 'hidden';
    }
  }

  function closeMobileMenu() {
    const menu = document.querySelector('[data-mobile-menu]');
    const body = document.body;
    if (menu) {
      menu.classList.remove('is-open');
      body.classList.remove('menu-open');
      body.style.overflow = '';
    }
  }

  // ============================================
  // Form Validation
  // ============================================

  /**
   * Initialize form validation
   */
  function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
      form.addEventListener('submit', function(e) {
        if (!validateForm(this)) {
          e.preventDefault();
        }
      });

      // Real-time validation
      const inputs = form.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        input.addEventListener('blur', function() {
          validateField(this);
        });
      });
    });
  }

  /**
   * Validate entire form
   */
  function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');

    inputs.forEach(input => {
      if (!validateField(input)) {
        isValid = false;
      }
    });

    return isValid;
  }

  /**
   * Validate individual field
   */
  function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Remove existing error
    removeFieldError(field);

    // Required validation
    if (field.hasAttribute('required') && !value) {
      isValid = false;
      errorMessage = 'This field is required';
    }

    // Email validation
    if (field.type === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
      }
    }

    // Phone validation
    if (field.type === 'tel' && value) {
      const phoneRegex = /^[\d\s\-\+\(\)]+$/;
      if (!phoneRegex.test(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid phone number';
      }
    }

    // Show error if invalid
    if (!isValid) {
      showFieldError(field, errorMessage);
    } else {
      field.classList.remove('error');
      field.classList.add('success');
    }

    return isValid;
  }

  /**
   * Show field error
   */
  function showFieldError(field, message) {
    field.classList.add('error');
    field.classList.remove('success');

    const errorElement = document.createElement('span');
    errorElement.className = 'form-error-message';
    errorElement.textContent = message;
    errorElement.id = field.id + '-error';

    field.parentNode.appendChild(errorElement);
  }

  /**
   * Remove field error
   */
  function removeFieldError(field) {
    field.classList.remove('error', 'success');
    const errorElement = field.parentNode.querySelector('#' + field.id + '-error');
    if (errorElement) {
      errorElement.remove();
    }
  }

  // ============================================
  // Notifications
  // ============================================

  /**
   * Show notification message
   */
  function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.setAttribute('role', 'alert');
    notification.textContent = message;

    document.body.appendChild(notification);

    // Trigger animation
    setTimeout(() => notification.classList.add('is-visible'), 10);

    // Remove after delay
    setTimeout(() => {
      notification.classList.remove('is-visible');
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  // ============================================
  // Utility Functions
  // ============================================

  /**
   * Format money (basic implementation)
   */
  function formatMoney(cents) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: window.Shopify?.currency?.active || 'USD'
    }).format(cents / 100);
  }

  /**
   * Debounce function
   */
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // ============================================
  // Product Form Handlers
  // ============================================

  /**
   * Handle product form submission
   */
  function initProductForms() {
    const productForms = document.querySelectorAll('form[action*="/cart/add"]');
    
    productForms.forEach(form => {
      form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
        const originalText = submitButton?.textContent;
        
        // Show loading state
        if (submitButton) {
          submitButton.disabled = true;
          submitButton.textContent = 'Adding...';
        }

        try {
          const formData = new FormData(form);
          const data = {
            id: formData.get('id'),
            quantity: parseInt(formData.get('quantity') || 1)
          };

          await addToCart(data);
        } catch (error) {
          console.error('Add to cart error:', error);
        } finally {
          // Restore button
          if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = originalText || 'Add to cart';
          }
        }
      });
    });
  }

  // ============================================
  // Cart Page Handlers
  // ============================================

  /**
   * Initialize cart page functionality
   */
  function initCartPage() {
    // Quantity updates
    const quantityInputs = document.querySelectorAll('[data-cart-quantity]');
    quantityInputs.forEach(input => {
      input.addEventListener('change', async function() {
        const key = this.dataset.cartKey;
        const quantity = parseInt(this.value);
        
        if (quantity < 1) {
          if (confirm('Remove this item from cart?')) {
            await removeCartItem(key);
          } else {
            this.value = 1;
          }
        } else {
          await updateCartItem(key, quantity);
        }
      });
    });

    // Remove buttons
    const removeButtons = document.querySelectorAll('[data-cart-remove]');
    removeButtons.forEach(button => {
      button.addEventListener('click', async function(e) {
        e.preventDefault();
        const key = this.dataset.cartKey;
        if (confirm('Remove this item from cart?')) {
          await removeCartItem(key);
        }
      });
    });
  }

  // ============================================
  // Initialize Everything
  // ============================================

  /**
   * Initialize all functionality when DOM is ready
   */
  function init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
      return;
    }

    // Initialize features
    initVariantSelection();
    initMobileMenu();
    initFormValidation();
    initProductForms();
    
    if (window.location.pathname === '/cart') {
      initCartPage();
    }

    // Update cart count on load
    updateCartCount();
  }

  // Start initialization
  init();

  // Export functions for external use
  window.Theme = {
    addToCart,
    updateCartItem,
    removeCartItem,
    getCart,
    updateCartCount,
    showNotification
  };

})();

