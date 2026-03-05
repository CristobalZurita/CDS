/**
 * Created by Ryan Balieiro on 08.26.2023
 * This composable will implement helper methods that manipulate DOM elements.
 */
import { useUtils } from '/src/composables/utils.js';

const utils = useUtils();

export function useLayout() {
  /**
   * @param {Boolean} enabled
   */
  const setBodyScrollEnabled = (enabled: boolean): void => {
    const body = document.body;

    if (!enabled) {
      (window as any).savedScrollY = window.scrollY;
      body.classList.add(`body-no-scroll`);
      if (utils.isIOS()) {
        body.classList.add(`position-fixed`);
      }
    } else {
      body.classList.remove(`body-no-scroll`);
      body.classList.remove(`position-fixed`);

      if ((window as any).savedScrollY) {
        window.scrollTo({
          top: (window as any).savedScrollY,
          behavior: "instant" as ScrollBehavior,
        });
        (window as any).savedScrollY = null;
      }
    }
  };

  /**
   * @param {HTMLElement} element
   * @return {boolean}
   */
  const isElementOutsideBounds = (element: HTMLElement): boolean => {
    const rect = element.getBoundingClientRect();

    return (
      rect.bottom < 0 ||
      rect.right < 0 ||
      rect.left > window.innerWidth ||
      rect.top > window.innerHeight
    );
  };

  /**
   * @param {HTMLElement} element
   * @return {boolean}
   */
  const scrollIntoView = (element: HTMLElement | null): void => {
    if (!element) {
      return;
    }

    const elNavbar = document.querySelector('.foxy-navbar-compressed');
    const navOffset = elNavbar ? (elNavbar as HTMLElement).getBoundingClientRect().height - 2 : 70;

    const elementPosition = element.getBoundingClientRect().top + window.scrollY;
    const offsetPosition = elementPosition - navOffset;

    window.scrollTo({
      top: offsetPosition,
      behavior: "smooth"
    });
  };

  return {
    setBodyScrollEnabled,
    isElementOutsideBounds,
    scrollIntoView
  };
}
