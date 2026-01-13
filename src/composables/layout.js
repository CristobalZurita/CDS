/**
 * Layout utility functions
 */

export function useLayout() {
  const getBreakpoint = () => {
    const width = window.innerWidth
    if (width < 576) return 'xs'
    if (width < 768) return 'sm'
    if (width < 992) return 'md'
    if (width < 1200) return 'lg'
    if (width < 1400) return 'xl'
    return 'xxl'
  }

  const isMobile = () => window.innerWidth < 768
  const isTablet = () => window.innerWidth >= 768 && window.innerWidth < 992
  const isDesktop = () => window.innerWidth >= 992

  const setBodyScrollEnabled = (enabled) => {
    if (enabled) {
      document.body.style.overflow = 'auto'
      document.documentElement.style.overflow = 'auto'
    } else {
      document.body.style.overflow = 'hidden'
      document.documentElement.style.overflow = 'hidden'
    }
  }

  return {
    getBreakpoint,
    isMobile,
    isTablet,
    isDesktop,
    setBodyScrollEnabled
  }
}
