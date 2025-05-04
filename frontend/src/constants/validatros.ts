/**
 * Valida si una cadena es un correo electrónico con formato válido.
 *
 * Utiliza una expresión regular para comprobar que el string:
 * - contiene texto antes y después del símbolo `@`,
 * - y contiene al menos un punto (`.`) después del dominio.
 *
 * Esta función no garantiza que el correo exista, solo que cumple con una estructura válida general.
 *
 * @param {string} email - Cadena que se desea validar como correo electrónico.
 * @returns {boolean} `true` si el formato es válido, `false` en caso contrario.
 *
 * @example
 * ```ts
 * validateEmail("usuario@example.com"); // true
 * validateEmail("sin-arroba.com");      // false
 * ```
 */
export const validateEmail = (email: string): boolean =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
