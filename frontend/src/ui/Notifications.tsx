import React from "react";

interface NotificationProps {
  success?: string | null;
  error?: string | null;
  errors?: string[];
}

const Notification: React.FC<NotificationProps> = ({ success, error, errors }) => {
  if (!success && !error && (!errors || errors.length === 0)) return null;

  return (
    <div style={{ marginBottom: 20 }}>
      {success && (
        <div
          style={{
            background: "#f0fdf4",
            border: "1px solid #bbf7d0",
            borderRadius: 8,
            padding: "10px 16px",
            color: "#15803d",
            fontSize: 13,
            marginBottom: 8,
          }}
        >
          {success}
        </div>
      )}

      {error && (
        <div
          style={{
            background: "#fff1f2",
            border: "1px solid #fecdd3",
            borderRadius: 8,
            padding: "10px 16px",
            color: "#be123c",
            fontSize: 13,
            marginBottom: 8,
          }}
        >
          {error}
        </div>
      )}

      {errors && errors.length > 0 && (
        <div
          style={{
            background: "#fff1f2",
            border: "1px solid #fecdd3",
            borderRadius: 8,
            padding: "10px 16px",
            color: "#be123c",
            fontSize: 13,
          }}
        >
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {errors.map((msg, i) => (
              <li key={i}>{msg}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Notification;