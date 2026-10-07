import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function Dashboard() {
  const [stats, setStats] = useState({
    medicines: 0,
    patients: 0,
    prescriptions: 0,
    purchases: 0,
  });

  const [expiringSoon, setExpiringSoon] = useState([]);
  const [expired, setExpired] = useState([]);
  const [recentPurchases, setRecentPurchases] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("Authentication token not found.");
        return;
      }

      const response = await fetch(`${API_URL}/dashboard`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load dashboard data.");
      }

      const data = await response.json();

      setStats({
        medicines: data.medicines || 0,
        patients: data.patients || 0,
        prescriptions: data.prescriptions || 0,
        purchases: data.purchases || 0,
      });

      setExpiringSoon(data.expiring_soon || []);
      setExpired(data.expired || []);
      setRecentPurchases(data.recent_purchases || []);
    } catch (err) {
      console.error(err);
      setError("Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateString) {
    if (!dateString) return "—";

    const date = new Date(dateString);

    return date.toLocaleDateString("en-IN");
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-state">
          Loading dashboard...
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">

      {/* HEADER */}
      <div className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p>
            Digital Medicine Management & Reminder System
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={loadDashboard}
        >
          ↻ Refresh
        </button>
      </div>

      {/* ERROR */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* STAT CARDS */}
      <div className="dashboard-grid">

        <div className="dashboard-card">
          <div className="dashboard-card-icon medicine-icon">
            💊
          </div>

          <div>
            <span>Total Medicines</span>
            <strong>{stats.medicines}</strong>
          </div>
        </div>


        <div className="dashboard-card">
          <div className="dashboard-card-icon patient-icon">
            👤
          </div>

          <div>
            <span>Total Patients</span>
            <strong>{stats.patients}</strong>
          </div>
        </div>


        <div className="dashboard-card">
          <div className="dashboard-card-icon prescription-icon">
            📋
          </div>

          <div>
            <span>Prescriptions</span>
            <strong>{stats.prescriptions}</strong>
          </div>
        </div>


        <div className="dashboard-card">
          <div className="dashboard-card-icon purchase-icon">
            🛒
          </div>

          <div>
            <span>Total Purchases</span>
            <strong>{stats.purchases}</strong>
          </div>
        </div>

      </div>


      {/* ALERT SECTION */}
      <div className="dashboard-two-column">

        {/* EXPIRING SOON */}
        <div className="dashboard-section">

          <div className="section-header">
            <div>
              <h2>⚠️ Expiring Soon</h2>
              <p>Medicines approaching their expiry date</p>
            </div>

            <span className="section-count warning-count">
              {expiringSoon.length}
            </span>
          </div>


          {expiringSoon.length === 0 ? (
            <div className="dashboard-empty">
              <div className="empty-icon">✓</div>
              <p>No medicines are expiring soon.</p>
            </div>
          ) : (
            <div className="dashboard-list">

              {expiringSoon.map((medicine) => (
                <div
                  className="dashboard-list-item warning-item"
                  key={medicine.id}
                >
                  <div>
                    <strong>
                      {medicine.medicine_name}
                    </strong>

                    <span>
                      Batch: {medicine.batch_number}
                    </span>
                  </div>

                  <div className="expiry-days warning">
                    {medicine.days_remaining} day
                    {medicine.days_remaining !== 1 ? "s" : ""}
                  </div>
                </div>
              ))}

            </div>
          )}

        </div>


        {/* EXPIRED */}
        <div className="dashboard-section">

          <div className="section-header">
            <div>
              <h2>🔴 Expired Medicines</h2>
              <p>Medicines that have passed their expiry date</p>
            </div>

            <span className="section-count expired-count">
              {expired.length}
            </span>
          </div>


          {expired.length === 0 ? (
            <div className="dashboard-empty">
              <div className="empty-icon">✓</div>
              <p>No expired medicines.</p>
            </div>
          ) : (
            <div className="dashboard-list">

              {expired.map((medicine) => (
                <div
                  className="dashboard-list-item expired-item"
                  key={medicine.id}
                >
                  <div>
                    <strong>
                      {medicine.medicine_name}
                    </strong>

                    <span>
                      Batch: {medicine.batch_number}
                    </span>
                  </div>

                  <div className="expiry-days expired">
                    Expired
                  </div>
                </div>
              ))}

            </div>
          )}

        </div>

      </div>


      {/* RECENT PURCHASES */}
      <div className="dashboard-section recent-purchases">

        <div className="section-header">
          <div>
            <h2>🛒 Recent Purchases</h2>
            <p>Latest medicine purchases recorded by the pharmacy</p>
          </div>
        </div>


        {recentPurchases.length === 0 ? (
          <div className="dashboard-empty">
            <div className="empty-icon">📦</div>
            <p>No purchases available.</p>
          </div>
        ) : (

          <div className="table-wrapper">

            <table>

              <thead>
                <tr>
                  <th>Purchase ID</th>
                  <th>Patient</th>
                  <th>Prescription</th>
                  <th>Total Amount</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody>

                {recentPurchases.map((purchase) => (
                  <tr key={purchase.id}>

                    <td>
                      <strong>
                        #{purchase.id}
                      </strong>
                    </td>

                    <td>
                      Patient #{purchase.patient_id}
                    </td>

                    <td>
                      {purchase.prescription_id
                        ? `Prescription #${purchase.prescription_id}`
                        : "—"}
                    </td>

                    <td>
                      ₹{Number(purchase.total_amount).toFixed(2)}
                    </td>

                    <td>
                      {formatDate(purchase.created_at)}
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        )}

      </div>

    </div>
  );
}

export default Dashboard;