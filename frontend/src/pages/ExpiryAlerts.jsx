import { useEffect, useState } from "react";

function ExpiryAlerts() {
  const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // =========================================================
  // FETCH EXPIRY ALERTS
  // =========================================================

  const fetchExpiryAlerts = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");
      setSuccess("");

      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("Please login again.");
        return;
      }

      const response = await fetch(
        `${API_URL}/medicine-batches/expiry-list`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Unable to fetch expiry alerts"
        );
        return;
      }

      setAlerts(data);

      if (isRefresh) {
        setSuccess(
          "Expiry information refreshed successfully."
        );
      }
    } catch (error) {
      console.error(error);

      setError(
        "Unable to connect to MediTrack backend."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchExpiryAlerts();
  }, []);

  // =========================================================
  // STATUS CLASS
  // =========================================================

  const getStatusClass = (status) => {
    switch (status) {
      case "EXPIRED":
        return "expiry-expired";

      case "EXPIRING_SOON":
        return "expiry-soon";

      case "EXPIRY_WARNING":
        return "expiry-warning";

      default:
        return "expiry-normal";
    }
  };

  // =========================================================
  // STATUS TEXT
  // =========================================================

  const getStatusText = (status) => {
    switch (status) {
      case "EXPIRED":
        return "Expired";

      case "EXPIRING_SOON":
        return "Expiring Soon";

      case "EXPIRY_WARNING":
        return "Expiry Warning";

      default:
        return "Normal";
    }
  };

  // =========================================================
  // COUNTS
  // =========================================================

  const expiredCount = alerts.filter(
    (item) => item.status === "EXPIRED"
  ).length;

  const expiringSoonCount = alerts.filter(
    (item) => item.status === "EXPIRING_SOON"
  ).length;

  const warningCount = alerts.filter(
    (item) => item.status === "EXPIRY_WARNING"
  ).length;

  const totalAlerts =
    expiredCount +
    expiringSoonCount +
    warningCount;

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="page-container">
        <h2>⚠️ Expiry Alerts</h2>

        <p>
          Loading expiry information...
        </p>
      </div>
    );
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="page-container">

      {/* ===================================================
          PAGE HEADER
      ==================================================== */}

      <div className="page-header">

        <div>

          <h2>
            ⚠️ Expiry Alerts
          </h2>

          <p>
            Monitor medicine batches approaching
            or past their expiry date.
          </p>

        </div>

        <button
          className="primary-button"
          onClick={() =>
            fetchExpiryAlerts(true)
          }
          disabled={refreshing}
        >
          {refreshing
            ? "Refreshing..."
            : "↻ Refresh"}
        </button>

      </div>

      {/* ===================================================
          SUCCESS MESSAGE
      ==================================================== */}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      {/* ===================================================
          ERROR MESSAGE
      ==================================================== */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* ===================================================
          SUMMARY CARDS
      ==================================================== */}

      <div className="expiry-summary">

        {/* TOTAL ALERTS */}

        <div className="expiry-summary-card">

          <span className="summary-icon">
            ⚠️
          </span>

          <div>

            <strong>
              {totalAlerts}
            </strong>

            <p>
              Total Alerts
            </p>

          </div>

        </div>

        {/* EXPIRED */}

        <div className="expiry-summary-card">

          <span className="summary-icon">
            🔴
          </span>

          <div>

            <strong>
              {expiredCount}
            </strong>

            <p>
              Expired
            </p>

          </div>

        </div>

        {/* EXPIRING SOON */}

        <div className="expiry-summary-card">

          <span className="summary-icon">
            🟠
          </span>

          <div>

            <strong>
              {expiringSoonCount}
            </strong>

            <p>
              Expiring Soon
            </p>

          </div>

        </div>

        {/* 10–15 DAYS */}

        <div className="expiry-summary-card">

          <span className="summary-icon">
            🟡
          </span>

          <div>

            <strong>
              {warningCount}
            </strong>

            <p>
              10–15 Days
            </p>

          </div>

        </div>

      </div>

      {/* ===================================================
          ALERT INFORMATION
      ==================================================== */}

      <div className="expiry-info-banner">

        <span>
          💡
        </span>

        <div>

          <strong>
            Expiry Monitoring
          </strong>

          <p>
            MediTrack highlights expired medicines
            and batches approaching their recorded
            expiry dates.
          </p>

        </div>

      </div>

      {/* ===================================================
          NO ALERTS
      ==================================================== */}

      {alerts.length === 0 ? (

        <div className="empty-state">

          <div className="empty-icon">
            ✅
          </div>

          <h3>
            No expiry alerts
          </h3>

          <p>
            There are currently no medicine batches
            requiring expiry attention.
          </p>

        </div>

      ) : (

        /* =================================================
           ALERT TABLE
        ================================================== */

        <div className="medicine-table-container">

          <table className="medicine-table">

            <thead>

              <tr>

                <th>
                  Medicine
                </th>

                <th>
                  Batch Number
                </th>

                <th>
                  Expiry Date
                </th>

                <th>
                  Days Remaining
                </th>

                <th>
                  Status
                </th>

              </tr>

            </thead>

            <tbody>

              {alerts.map(
                (alert) => (

                  <tr
                    key={alert.batch_id}
                    className={getStatusClass(
                      alert.status
                    )}
                  >

                    {/* MEDICINE */}

                    <td>

                      <strong>
                        {alert.medicine_name}
                      </strong>

                    </td>

                    {/* BATCH */}

                    <td>
                      {alert.batch_number}
                    </td>

                    {/* EXPIRY DATE */}

                    <td>

                      {new Date(
                        alert.expiry_date
                      ).toLocaleDateString(
                        "en-IN"
                      )}

                    </td>

                    {/* DAYS REMAINING */}

                    <td>

                      {alert.days_remaining < 0
                        ? `${Math.abs(
                            alert.days_remaining
                          )} days ago`
                        : alert.days_remaining === 0
                        ? "Today"
                        : `${alert.days_remaining} days`}

                    </td>

                    {/* STATUS */}

                    <td>

                      <span
                        className={`expiry-badge ${getStatusClass(
                          alert.status
                        )}`}
                      >

                        {getStatusText(
                          alert.status
                        )}

                      </span>

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

        </div>

      )}

    </div>
  );
}

export default ExpiryAlerts;