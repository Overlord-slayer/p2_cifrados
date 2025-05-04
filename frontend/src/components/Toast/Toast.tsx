import React, { JSX } from "react";
import styles from "./Toast.module.css";

/**
 * Props para el componente `Toast`.
 *
 * @property {string} message - Mensaje de texto que se mostrará dentro del toast.
 * @property {"success" | "error"} [type="success"] - Tipo de mensaje (`success` o `error`) para aplicar estilos correspondientes.
 * @property {() => void} [onClose] - Función opcional que se ejecuta al hacer clic en el botón de cerrar.
 */
interface ToastProps {
  message: string;
  type?: "success" | "error";
  onClose?: () => void;
}

/**
 * Componente `Toast`.
 *
 * Muestra un mensaje emergente en pantalla que puede representar un estado de éxito o error.
 * Se estiliza dinámicamente según el tipo (`success` o `error`) usando clases CSS Modules.
 *
 * Si se proporciona una función `onClose`, el componente incluirá un botón para cerrar manualmente el toast.
 *
 * @component
 * @example
 * ```tsx
 * <Toast
 *   message="Operación realizada con éxito"
 *   type="success"
 *   onClose={() => setVisible(false)}
 * />
 * ```
 *
 * @param {ToastProps} props - Propiedades del componente.
 * @returns {JSX.Element} Elemento visual tipo notificación.
 */
export default function Toast({
  message,
  type = "success",
  onClose,
}: ToastProps): JSX.Element {
  return (
    <div className={`${styles.toast} ${styles[type]}`}>
      <span>{message}</span>
      {onClose && (
        <button onClick={onClose} className={styles.close}>
          ×
        </button>
      )}
    </div>
  );
}
