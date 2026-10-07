import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [selectedNotification, setSelectedNotification] = useState(null);
  const [sendingId, setSendingId] = useState(null);
  const [generating, setGenerating] = useState(false);

  const getToken = () => {
    return localStorage.getItem("access_token");
  };

  const getHeaders = () => {
    const token = getToken();

    return {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    };
  };

  // --------------------------------------------------
  // LOAD NOTIFICATIONS
  // --------------------------------------------------

  const loadNotifications = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/notifications`, {
        method: "GET",
        headers: getHeaders(),
      });

      if (!response.ok) {
        throw new Error("Failed to load notifications");
      }

      const data = await response.json();

      setNotifications(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Load notifications error:", error);
      setError(error.message || "Failed to load notifications");
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // INITIAL LOAD
  // --------------------------------------------------

  useEffect(() => {
    loadNotifications();
  }, []);

  // --------------------------------------------------
  // GENERATE EXPIRY NOTIFICATIONS
  // --------------------------------------------------

  const generateExpiryNotifications = async () => {
    try {
      setGenerating(true);
      setMessage("");
      setError("");

      const response = await fetch(
        `${API_URL}/notifications/generate-expiry`,
        {
          method: "POST",
          headers: getHeaders(),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to generate expiry notifications"
        );
      }

      setMessage(
        data.message ||
          `Generated ${
            Array.isArray(data) ? data.length : 0
          } expiry notification(s).`
      );

      await loadNotifications();
    } catch (error) {
      console.error("Generate expiry notifications error:", error);
      setError(
        error.message || "Failed to generate expiry notifications"
      );
    } finally {
      setGenerating(false);
    }
  };

  // --------------------------------------------------
  // VIEW NOTIFICATION DETAILS
  // --------------------------------------------------

  const viewNotification = async (notificationId) => {
    try {
      setError("");

      const response = await fetch(
        `${API_URL}/notifications/${notificationId}`,
        {
          method: "GET",
          headers: getHeaders(),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load notification details"
        );
      }

      setSelectedNotification(data);
    } catch (error) {
      console.error("View notification error:", error);
      setError(
        error.message || "Failed to load notification details"
      );
    }
  };

  // --------------------------------------------------
  // SEND EMAIL
  // --------------------------------------------------

  const sendEmail = async (notificationId) => {
    try {
      setSendingId(notificationId);
      setMessage("");
      setError("");

      const response = await fetch(
        `${API_URL}/notifications/${notificationId}/send-email`,
        {
          method: "POST",
          headers: getHeaders(),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to send email notification"
        );
      }

      setMessage(
        data.message || "Email notification sent successfully."
      );

      await loadNotifications();

      // Refresh selected notification if it is open
      if (selectedNotification?.id === notificationId) {
        await viewNotification(notificationId);
      }
    } catch (error) {
      console.error("Send email error:", error);
      setError(
        error.message || "Failed to send email notification"
      );
    } finally {
      setSendingId(null);
    }
  };

  // --------------------------------------------------
  // STATUS CLASS
  // --------------------------------------------------

  const getStatusClass = (status) => {
    if (!status) return "notification-status";

    const normalizedStatus = status.toUpperCase();

    if (normalizedStatus === "SENT") {
      return "notification-status sent";
    }

    if (normalizedStatus === "PENDING") {
      return "notification-status pending";
    }

    if (normalizedStatus === "FAILED") {
      return "notification-status failed";
    }

    return "notification-status";
  };

  // --------------------------------------------------
  // CHANNEL ICON
  // --------------------------------------------------

  const getChannelIcon = (channel) => {
    if (!channel) return "🔔";

    const normalizedChannel = channel.toUpperCase();

    if (normalizedChannel === "EMAIL") {
      return "📧";
    }

    if (normalizedChannel === "SMS") {
      return "📱";
    }

    if (normalizedChannel === "WHATSAPP") {
      return "💬";
    }

    return "🔔";
  };

  // --------------------------------------------------
  // DATE FORMAT
  // --------------------------------------------------

  const formatDate = (dateValue) => {
    if (!dateValue) return "—";

    try {
      return new Date(dateValue).toLocaleString();
    } catch {
      return dateValue;
    }
  };

  // --------------------------------------------------
  // RENDER
  // --------------------------------------------------

  return (
    <div className="notifications-page">
      {/* HEADER */}

      <div className="notifications-header">
        <div>
          <h1>Notifications</h1>

          <p>
            Manage medicine expiry notifications and patient
            communication.
          </p>
        </div>

        <button
          className="notification-generate-btn"
          onClick={generateExpiryNotifications}
          disabled={generating}
        >
          {generating
            ? "Generating..."
            : "🔔 Generate Expiry Notifications"}
        </button>
      </div>

      {/* SUCCESS MESSAGE */}

      {message && (
        <div className="notification-message success">
          ✓ {message}
        </div>
      )}

      {/* ERROR MESSAGE */}

      {error && (
        <div className="notification-message error">
          ✕ {error}
        </div>
      )}

      {/* SUMMARY CARDS */}

      <div className="notification-summary">
        <div className="notification-summary-card">
          <div className="summary-icon">🔔</div>

          <div>
            <span>Total Notifications</span>
            <strong>{notifications.length}</strong>
          </div>
        </div>

        <div className="notification-summary-card">
          <div className="summary-icon pending-icon">⏳</div>

          <div>
            <span>Pending</span>

            <strong>
              {
                notifications.filter(
                  (item) =>
                    item.status?.toUpperCase() === "PENDING"
                ).length
              }
            </strong>
          </div>
        </div>

        <div className="notification-summary-card">
          <div className="summary-icon sent-icon">✓</div>

          <div>
            <span>Sent</span>

            <strong>
              {
                notifications.filter(
                  (item) =>
                    item.status?.toUpperCase() === "SENT"
                ).length
              }
            </strong>
          </div>
        </div>

        <div className="notification-summary-card">
          <div className="summary-icon failed-icon">!</div>

          <div>
            <span>Failed</span>

            <strong>
              {
                notifications.filter(
                  (item) =>
                    item.status?.toUpperCase() === "FAILED"
                ).length
              }
            </strong>
          </div>
        </div>
      </div>

      {/* NOTIFICATION LIST */}

      <div className="notifications-section">
        <div className="section-heading">
          <div>
            <h2>Notification History</h2>

            <p>
              View and manage expiry-related notifications.
            </p>
          </div>

          <button
            className="refresh-notifications-btn"
            onClick={loadNotifications}
            disabled={loading}
          >
            ↻ Refresh
          </button>
        </div>

        {loading ? (
          <div className="notifications-empty">
            <div className="notification-loader">
              Loading notifications...
            </div>
          </div>
        ) : notifications.length === 0 ? (
          <div className="notifications-empty">
            <div className="empty-notification-icon">🔔</div>

            <h3>No Notifications Yet</h3>

            <p>
              No notifications have been generated yet.
              Click <strong>Generate Expiry Notifications</strong>{" "}
              to check for medicines approaching expiry.
            </p>
          </div>
        ) : (
          <div className="notifications-table-wrapper">
            <table className="notifications-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Channel</th>
                  <th>Patient</th>
                  <th>Medicine</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {notifications.map((notification) => (
                  <tr key={notification.id}>
                    <td>
                      <strong>#{notification.id}</strong>
                    </td>

                    <td>
                      <span className="notification-channel">
                        {getChannelIcon(notification.channel)}
                        {notification.channel || "—"}
                      </span>
                    </td>

                    <td>
                      {notification.patient_id
                        ? `Patient #${notification.patient_id}`
                        : "—"}
                    </td>

                    <td>
                      {notification.medicine_id
                        ? `Medicine #${notification.medicine_id}`
                        : "—"}
                    </td>

                    <td>
                      <span
                        className={getStatusClass(
                          notification.status
                        )}
                      >
                        {notification.status || "UNKNOWN"}
                      </span>
                    </td>

                    <td>
                      {formatDate(notification.created_at)}
                    </td>

                    <td>
                      <div className="notification-actions">
                        <button
                          className="view-notification-btn"
                          onClick={() =>
                            viewNotification(notification.id)
                          }
                        >
                          View
                        </button>

                        {notification.channel?.toUpperCase() ===
                          "EMAIL" &&
                          notification.status?.toUpperCase() ===
                            "PENDING" && (
                            <button
                              className="send-email-btn"
                              onClick={() =>
                                sendEmail(notification.id)
                              }
                              disabled={
                                sendingId === notification.id
                              }
                            >
                              {sendingId === notification.id
                                ? "Sending..."
                                : "Send Email"}
                            </button>
                          )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* DETAIL MODAL */}

      {selectedNotification && (
        <div
          className="notification-modal-overlay"
          onClick={() => setSelectedNotification(null)}
        >
          <div
            className="notification-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="notification-modal-header">
              <div>
                <h2>Notification Details</h2>

                <p>
                  Notification #
                  {selectedNotification.id}
                </p>
              </div>

              <button
                className="notification-modal-close"
                onClick={() =>
                  setSelectedNotification(null)
                }
              >
                ×
              </button>
            </div>

            <div className="notification-details">
              <div className="detail-row">
                <span>ID</span>
                <strong>
                  #{selectedNotification.id}
                </strong>
              </div>

              <div className="detail-row">
                <span>Patient ID</span>
                <strong>
                  {selectedNotification.patient_id ?? "—"}
                </strong>
              </div>

              <div className="detail-row">
                <span>Medicine ID</span>
                <strong>
                  {selectedNotification.medicine_id ?? "—"}
                </strong>
              </div>

              <div className="detail-row">
                <span>Channel</span>
                <strong>
                  {getChannelIcon(
                    selectedNotification.channel
                  )}{" "}
                  {selectedNotification.channel || "—"}
                </strong>
              </div>

              <div className="detail-row">
                <span>Status</span>

                <span
                  className={getStatusClass(
                    selectedNotification.status
                  )}
                >
                  {selectedNotification.status || "UNKNOWN"}
                </span>
              </div>

              <div className="detail-row">
                <span>Created At</span>

                <strong>
                  {formatDate(
                    selectedNotification.created_at
                  )}
                </strong>
              </div>

              {selectedNotification.sent_at && (
                <div className="detail-row">
                  <span>Sent At</span>

                  <strong>
                    {formatDate(
                      selectedNotification.sent_at
                    )}
                  </strong>
                </div>
              )}

              {selectedNotification.message && (
                <div className="notification-content">
                  <span>Message</span>

                  <p>
                    {selectedNotification.message}
                  </p>
                </div>
              )}
            </div>

            {selectedNotification.channel?.toUpperCase() ===
              "EMAIL" &&
              selectedNotification.status?.toUpperCase() ===
                "PENDING" && (
                <div className="notification-modal-footer">
                  <button
                    className="send-email-btn large"
                    onClick={() =>
                      sendEmail(selectedNotification.id)
                    }
                    disabled={
                      sendingId === selectedNotification.id
                    }
                  >
                    {sendingId === selectedNotification.id
                      ? "Sending Email..."
                      : "📧 Send Email"}
                  </button>
                </div>
              )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Notifications;