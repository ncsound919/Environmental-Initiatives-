/**
 * Utility functions for styling
 */

/**
 * Add opacity to a hex color
 * @param hexColor - Hex color (e.g., '#10b981')
 * @param opacity - Opacity value (0-100)
 * @returns Color with opacity as hex (e.g., '#10b98120')
 */
export function withOpacity(hexColor: string, opacity: number): string {
  const opacityHex = Math.round((opacity / 100) * 255).toString(16).padStart(2, '0');
  return `${hexColor}${opacityHex}`;
}

/**
 * Project colors with common opacity variants
 */
export function getProjectColors(baseColor: string) {
  return {
    base: baseColor,
    light: withOpacity(baseColor, 12),    // 20 in hex ≈ 12%
    medium: withOpacity(baseColor, 19),   // 30 in hex ≈ 19%
    background: withOpacity(baseColor, 8), // Subtle background
  };
}
