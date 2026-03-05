import gsap from 'gsap';

// Animation presets for consistent animations across the app
export const animations = {
  // Entrance animations
  fadeIn: (element, options = {}) => {
    const defaults = { opacity: 0, duration: 0.6, ease: 'power2.out' };
    return gsap.from(element, { ...defaults, ...options });
  },
  
  slideInLeft: (element, options = {}) => {
    const defaults = { x: -100, opacity: 0, duration: 0.6, ease: 'power2.out' };
    return gsap.from(element, { ...defaults, ...options });
  },
  
  slideInRight: (element, options = {}) => {
    const defaults = { x: 100, opacity: 0, duration: 0.6, ease: 'power2.out' };
    return gsap.from(element, { ...defaults, ...options });
  },
  
  slideInUp: (element, options = {}) => {
    const defaults = { y: 50, opacity: 0, duration: 0.6, ease: 'power2.out' };
    return gsap.from(element, { ...defaults, ...options });
  },
  
  slideInDown: (element, options = {}) => {
    const defaults = { y: -50, opacity: 0, duration: 0.6, ease: 'power2.out' };
    return gsap.from(element, { ...defaults, ...options });
  },
  
  scaleIn: (element, options = {}) => {
    const defaults = { scale: 0, opacity: 0, duration: 0.8, ease: 'back.out(1.7)' };
    return gsap.from(element, { ...defaults, ...options });
  },
  
  rotateIn: (element, options = {}) => {
    const defaults = { scale: 0, rotation: 360, opacity: 0, duration: 1, ease: 'back.out(1.7)' };
    return gsap.from(element, { ...defaults, ...options });
  },
  
  // Stagger animations
  staggerFadeIn: (elements, options = {}) => {
    const defaults = { opacity: 0, y: 30, duration: 0.6, stagger: 0.1, ease: 'power2.out' };
    return gsap.from(elements, { ...defaults, ...options });
  },
  
  staggerSlideIn: (elements, options = {}) => {
    const defaults = { x: -100, opacity: 0, duration: 0.6, stagger: 0.15, ease: 'power2.out' };
    return gsap.from(elements, { ...defaults, ...options });
  },
  
  // Interaction animations
  hoverLift: (element) => {
    return gsap.to(element, { 
      y: -5, 
      boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
      duration: 0.3,
      ease: 'power2.out'
    });
  },
  
  hoverScale: (element, scale = 1.05) => {
    return gsap.to(element, { 
      scale, 
      duration: 0.3,
      ease: 'power2.out'
    });
  },
  
  clickScale: (element) => {
    return gsap.timeline()
      .to(element, { scale: 0.95, duration: 0.1 })
      .to(element, { scale: 1, duration: 0.2, ease: 'elastic.out(1, 0.5)' });
  },
  
  shake: (element) => {
    return gsap.to(element, { 
      x: [-10, 10, -10, 10, 0],
      duration: 0.5,
      ease: 'power2.inOut'
    });
  },
  
  pulse: (element, options = {}) => {
    const defaults = { 
      scale: [1, 1.1, 1],
      duration: 0.6,
      repeat: -1,
      ease: 'power2.inOut'
    };
    return gsap.to(element, { ...defaults, ...options });
  },
  
  // Loading animations
  spin: (element) => {
    return gsap.to(element, {
      rotation: 360,
      duration: 1,
      repeat: -1,
      ease: 'linear'
    });
  },
  
  typingDots: (elements) => {
    return gsap.to(elements, {
      y: -10,
      stagger: 0.2,
      repeat: -1,
      yoyo: true,
      duration: 0.5,
      ease: 'power2.inOut'
    });
  },
  
  // Progress animations
  progressBar: (element, progress) => {
    return gsap.to(element, {
      width: `${progress}%`,
      duration: 0.5,
      ease: 'power2.out'
    });
  },
  
  // Scroll animations
  scrollToBottom: (container) => {
    return gsap.to(container, {
      scrollTop: container.scrollHeight,
      duration: 0.5,
      ease: 'power2.inOut'
    });
  },
  
  // Special effects
  glowPulse: (element) => {
    return gsap.to(element, {
      boxShadow: [
        '0 0 20px rgba(245, 203, 125, 0.3)',
        '0 0 40px rgba(245, 203, 125, 0.6)',
        '0 0 20px rgba(245, 203, 125, 0.3)'
      ],
      duration: 2,
      repeat: -1,
      ease: 'power2.inOut'
    });
  },
  
  confetti: (elements) => {
    return gsap.from(elements, {
      y: -100,
      opacity: 0,
      rotation: () => Math.random() * 360,
      stagger: 0.05,
      duration: 2,
      ease: 'power2.out'
    });
  },
  
  // Exit animations
  fadeOut: (element, options = {}) => {
    const defaults = { opacity: 0, duration: 0.3, ease: 'power2.in' };
    return gsap.to(element, { ...defaults, ...options });
  },
  
  scaleOut: (element, options = {}) => {
    const defaults = { scale: 0, opacity: 0, duration: 0.3, ease: 'power2.in' };
    return gsap.to(element, { ...defaults, ...options });
  },
};

// Timeline helpers
export const createTimeline = (options = {}) => {
  return gsap.timeline(options);
};

// Scroll trigger setup (if needed)
export const setupScrollTrigger = (element, animation, options = {}) => {
  return gsap.from(element, {
    ...animation,
    scrollTrigger: {
      trigger: element,
      start: 'top 80%',
      end: 'bottom 20%',
      toggleActions: 'play none none reverse',
      ...options,
    },
  });
};

export default animations;
