/**
 * Logger seguro para desarrollo
 * Redacta información sensible automáticamente
 */

const SENSITIVE_KEYS = new Set([
  "password",
  "totp",
  "totp_code",
  "totp_secret",
  "qr_code_base64",
  "access_token",
  "refresh_token",
  "secret",
  "privateKey",
  "private_key"
]);

/**
 * Redacta valores sensibles en objetos
 */
function redact(obj: unknown): unknown {
  if (obj === null || obj === undefined) return obj;
  if (typeof obj !== "object") return obj;
  
  return JSON.parse(
    JSON.stringify(obj, (key, value) => {
      if (SENSITIVE_KEYS.has(key)) {
        return "***REDACTED***";
      }
      return value;
    })
  );
}

/**
 * Log solo en desarrollo, con redacción automática de información sensible
 */
export function devLog(...args: unknown[]): void {
  if (import.meta.env.MODE !== "production") {
    const redactedArgs = args.map(arg => 
      typeof arg === "object" && arg !== null ? redact(arg) : arg
    );
    console.log(...redactedArgs);
  }
}

/**
 * Warning en desarrollo y producción, con redacción
 */
export function devWarn(...args: unknown[]): void {
  const redactedArgs = args.map(arg => 
    typeof arg === "object" && arg !== null ? redact(arg) : arg
  );
  console.warn(...redactedArgs);
}

/**
 * Error siempre registrado, con redacción
 */
export function devError(...args: unknown[]): void {
  const redactedArgs = args.map(arg => 
    typeof arg === "object" && arg !== null ? redact(arg) : arg
  );
  console.error(...redactedArgs);
}
