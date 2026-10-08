import { useEffect, useState } from "react";

import Dashboard from "./pages/Dashboard";
import Medicines from "./pages/Medicines";
import MedicineBatches from "./pages/MedicineBatches";
import ExpiryAlerts from "./pages/ExpiryAlerts";
import Purchases from "./pages/Purchases";
import Prescriptions from "./pages/Prescriptions";
import Notifications from "./pages/Notifications";

import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [checkingLogin, setCheckingLogin] = useState(true);

  // =====================================================
  // CHECK EXISTING LOGIN
  // =====================================================

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setCheckingLogin(false);
      return;
    }

    fetch(`${API_URL}/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (response) => {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Session expired");
        }

        setUser(data.user);
        setCurrentPage("dashboard");
      })
      .catch((error) => {
        console.error(error);
        localStorage.removeItem("access_token");
        setUser(null);
      })
      .finally(() => {
        setCheckingLogin(false);
      });
  }, []);

  // =====================================================
  // LOGIN
  // =====================================================

  const handleLogin = async (e) => {
    e.preventDefault();

    setMessage("Logging in...");

    try {
      const formData = new URLSearchParams();

      formData.append("username", email);
      formData.append("password", password);

      const loginResponse = await fetch(
        `${API_URL}/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
          body: formData,
        }
      );

      const loginData = await loginResponse.json();

      if (!loginResponse.ok) {
        setMessage(
          loginData.detail || "Login failed"
        );
        return;
      }

      // Store JWT
      localStorage.setItem(
        "access_token",
        loginData.access_token
      );

      // Get logged-in user
      const profileResponse = await fetch(
        `${API_URL}/auth/me`,
        {
          method: "GET",
          headers: {
            Authorization:
              `Bearer ${loginData.access_token}`,
          },
        }
      );

      const profileData =
        await profileResponse.json();

      if (!profileResponse.ok) {
        setMessage(
          profileData.detail ||
            "Unable to get user profile"
        );
        return;
      }

      setUser(profileData.user);
      setCurrentPage("dashboard");
      setMessage("");

      setEmail("");
      setPassword("");
      setShowPassword(false);
    } catch (error) {
      console.error(error);

      setMessage(
        "Unable to connect to MediTrack backend."
      );
    }
  };

  // =====================================================
  // LOGOUT
  // =====================================================

  const handleLogout = () => {
    localStorage.removeItem("access_token");

    setUser(null);
    setCurrentPage("dashboard");
    setEmail("");
    setPassword("");
    setShowPassword(false);
    setMessage("");
  };

  // =====================================================
  // NAVIGATION
  // =====================================================

  const navigateTo = (page) => {
    setCurrentPage(page);
  };

  // =====================================================
  // LOADING SESSION
  // =====================================================

  if (checkingLogin) {
    return (
      <div className="app">
        <div className="loading-state">
          Checking MediTrack session...
        </div>
      </div>
    );
  }

  // =====================================================
  // LOGIN PAGE
  // =====================================================

  if (!user) {
    return (
      <div className="login-page">
        <div className="login-shell">

          {/* =================================================
              LOGIN BRAND PANEL
          ================================================= */}

          <section className="login-brand-panel">

            <div className="brand-header">

              <div className="brand-logo">
                💊
              </div>

              <div className="brand-title-wrapper">

                <div className="brand-name">
                  MediTrack
                </div>

                <div className="brand-tag">
                  DIGITAL MEDICINE MANAGEMENT
                </div>

              </div>

            </div>

            <div className="brand-content">

              <div className="brand-badge">
                <span className="status-dot"></span>
                Pharmacy Care Platform
              </div>

              <h1>
                Your medicines.
                <br />
                <span>Your records.</span>
                <br />
                Your peace of mind.
              </h1>

              <p>
                Manage medicines, prescriptions, batches,
                purchases and expiry information from one
                secure platform.
              </p>

              <div className="brand-features">

                <div className="brand-feature">

                  <span className="feature-icon">
                    ✓
                  </span>

                  <div>
                    <strong>
                      Secure Medicine Records
                    </strong>

                    <small>
                      Keep important medicine information
                      organized.
                    </small>
                  </div>

                </div>

                <div className="brand-feature">

                  <span className="feature-icon">
                    ✓
                  </span>

                  <div>
                    <strong>
                      Batch &amp; Expiry Tracking
                    </strong>

                    <small>
                      Track medicine batches and expiry
                      dates easily.
                    </small>
                  </div>

                </div>

                <div className="brand-feature">

                  <span className="feature-icon">
                    ✓
                  </span>

                  <div>
                    <strong>
                      Smart Notifications
                    </strong>

                    <small>
                      Stay informed about important expiry
                      reminders.
                    </small>
                  </div>

                </div>

              </div>

            </div>

            <div className="brand-footer">

              <span>
                © {new Date().getFullYear()} MediTrack
              </span>

              <span>
                Digital Medicine Management System
              </span>

            </div>

          </section>

          {/* =================================================
              LOGIN FORM PANEL
          ================================================= */}

          <section className="login-form-panel">

            <div className="login-form-card">

              <div className="mobile-logo">

                <div className="mobile-logo-icon">
                  💊
                </div>

                <span>
                  MediTrack
                </span>

              </div>

              <div className="login-icon">
                🔐
              </div>

              <div className="login-eyebrow">
                PHARMACY PORTAL
              </div>

              <h2>
                Welcome back
              </h2>

              <p className="login-description">
                Sign in to continue to your MediTrack
                dashboard.
              </p>

              {message && (
                <div
                  className={`login-alert ${
                    message === "Logging in..."
                      ? "login-alert-info"
                      : "login-alert-error"
                  }`}
                >
                  <span>
                    {message === "Logging in..."
                      ? "⏳"
                      : "⚠️"}
                  </span>

                  {message}
                </div>
              )}

              <form
                onSubmit={handleLogin}
                className="modern-login-form"
              >

                {/* EMAIL */}

                <div className="modern-input-group">

                  <label htmlFor="login-email">
                    Email address
                  </label>

                  <div className="modern-input-wrapper">

                    <span className="input-icon">
                      ✉
                    </span>

                    <input
                      id="login-email"
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) =>
                        setEmail(e.target.value)
                      }
                      autoComplete="email"
                      required
                    />

                  </div>

                </div>

                {/* PASSWORD */}

                <div className="modern-input-group">

                  <div className="password-label-row">

                    <label htmlFor="login-password">
                      Password
                    </label>

                    <span>
                      Secure login
                    </span>

                  </div>

                  <div className="modern-input-wrapper">

                    <span className="input-icon">
                      🔒
                    </span>

                    <input
                      id="login-password"
                      type={
                        showPassword
                          ? "text"
                          : "password"
                      }
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) =>
                        setPassword(e.target.value)
                      }
                      autoComplete="current-password"
                      required
                    />

                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() =>
                        setShowPassword(
                          !showPassword
                        )
                      }
                      aria-label={
                        showPassword
                          ? "Hide password"
                          : "Show password"
                      }
                    >
                      {showPassword
                        ? "Hide"
                        : "Show"}
                    </button>

                  </div>

                </div>

                {/* LOGIN BUTTON */}

                <button
                  type="submit"
                  className="modern-login-button"
                  disabled={
                    message === "Logging in..."
                  }
                >

                  <span>
                    {message === "Logging in..."
                      ? "Signing in..."
                      : "Sign in"}
                  </span>

                  <span className="login-arrow">
                    →
                  </span>

                </button>

              </form>

              <div className="login-security">

                <span className="security-icon">
                  🔒
                </span>

                <span>
                  Protected by MediTrack authentication
                </span>

              </div>

              <div className="login-bottom-text">
                Secure medicine management made simple.
              </div>

            </div>

          </section>

        </div>
      </div>
    );
  }

  // =====================================================
  // PHARMACY APPLICATION
  // =====================================================

  if (user.role !== "PHARMACY") {
    return (
      <div className="app">

        <div className="login-card">

          <div className="logo">
            ⚠️
          </div>

          <h1>
            Access Restricted
          </h1>

          <p className="subtitle">
            This portal is currently available
            for pharmacy users.
          </p>

          <button
            className="login-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </div>
    );
  }

  // =====================================================
  // MAIN APPLICATION
  // =====================================================

  return (
    <div className="app-layout">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside className="sidebar">

        {/* LOGO */}

        <div className="sidebar-logo">

          <div className="sidebar-logo-icon">
            💊
          </div>

          <div>

            <h2>
              MediTrack
            </h2>

            <span>
              Pharmacy
            </span>

          </div>

        </div>

        {/* NAVIGATION */}

        <nav className="sidebar-nav">

          {/* DASHBOARD */}

          <button
            className={
              currentPage === "dashboard"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              navigateTo("dashboard")
            }
          >

            <span className="nav-icon">
              🏠
            </span>

            <span>
              Dashboard
            </span>

          </button>

          {/* MEDICINES */}

          <button
            className={
              currentPage === "medicines"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              navigateTo("medicines")
            }
          >

            <span className="nav-icon">
              💊
            </span>

            <span>
              Medicines
            </span>

          </button>

          {/* BATCHES */}

          <button
            className={
              currentPage === "batches"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              navigateTo("batches")
            }
          >

            <span className="nav-icon">
              📦
            </span>

            <span>
              Medicine Batches
            </span>

          </button>

          {/* EXPIRY */}

          <button
            className={
              currentPage === "expiry-alerts"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              navigateTo("expiry-alerts")
            }
          >

            <span className="nav-icon">
              ⚠️
            </span>

            <span>
              Expiry Alerts
            </span>

          </button>

          {/* PRESCRIPTIONS */}

          <button
            className={
              currentPage === "prescriptions"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              navigateTo("prescriptions")
            }
          >

            <span className="nav-icon">
              📋
            </span>

            <span>
              Prescriptions
            </span>

          </button>

          {/* PURCHASES */}

          <button
            className={
              currentPage === "purchases"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              navigateTo("purchases")
            }
          >

            <span className="nav-icon">
              🛒
            </span>

            <span>
              Purchases
            </span>

          </button>

          {/* NOTIFICATIONS */}

          <button
            className={
              currentPage === "notifications"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              navigateTo("notifications")
            }
          >

            <span className="nav-icon">
              🔔
            </span>

            <span>
              Notifications
            </span>

          </button>

          {/* PROFILE */}

          <button
            className={
              currentPage === "profile"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() =>
              navigateTo("profile")
            }
          >

            <span className="nav-icon">
              👤
            </span>

            <span>
              Profile
            </span>

          </button>

        </nav>

        {/* SIDEBAR BOTTOM */}

        <div className="sidebar-bottom">

          <div className="sidebar-user">

            <div className="sidebar-user-avatar">

              {user.name
                ? user.name.charAt(0).toUpperCase()
                : "P"}

            </div>

            <div className="sidebar-user-info">

              <strong>
                {user.name}
              </strong>

              <span>
                Pharmacy
              </span>

            </div>

          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >

            <span>
              🚪
            </span>

            Logout

          </button>

        </div>

      </aside>

      {/* =================================================
          MAIN CONTENT
      ================================================= */}

      <main className="main-content">

        {/* ===============================================
            DASHBOARD
        =============================================== */}

        {currentPage === "dashboard" && (
          <Dashboard />
        )}

        {/* ===============================================
            MEDICINES
        =============================================== */}

        {currentPage === "medicines" && (
          <div className="page-container">

            <div className="page-header">

              <div>

                <h1>
                  Medicines
                </h1>

                <p>
                  Manage medicines available
                  in your pharmacy.
                </p>

              </div>

            </div>

            <Medicines />

          </div>
        )}

        {/* ===============================================
            MEDICINE BATCHES
        =============================================== */}

        {currentPage === "batches" && (
          <div className="page-container">

            <div className="page-header">

              <div>

                <h1>
                  Medicine Batches
                </h1>

                <p>
                  Manage batch numbers,
                  manufacturing dates and expiry dates.
                </p>

              </div>

            </div>

            <MedicineBatches />

          </div>
        )}

        {/* ===============================================
            EXPIRY ALERTS
        =============================================== */}

        {currentPage === "expiry-alerts" && (
          <div className="page-container">

            <div className="page-header">

              <div>

                <h1>
                  Expiry Alerts
                </h1>

                <p>
                  Monitor medicines approaching
                  or past their expiry date.
                </p>

              </div>

            </div>

            <ExpiryAlerts />

          </div>
        )}

        {/* ===============================================
            PRESCRIPTIONS
        =============================================== */}

        {currentPage === "prescriptions" && (
          <div className="page-container">

            <div className="page-header">

              <div>

                <h1>
                  Prescriptions
                </h1>

                <p>
                  Create and manage patient
                  prescriptions.
                </p>

              </div>

            </div>

            <Prescriptions />

          </div>
        )}

        {/* ===============================================
            PURCHASES
        =============================================== */}

        {currentPage === "purchases" && (
          <div className="page-container">

            <div className="page-header">

              <div>

                <h1>
                  Purchases
                </h1>

                <p>
                  Manage patient purchases,
                  prescription links and medicine batches.
                </p>

              </div>

            </div>

            <Purchases />

          </div>
        )}

        {/* ===============================================
            NOTIFICATIONS
        =============================================== */}

        {currentPage === "notifications" && (
          <div className="page-container">

            <div className="page-header">

              <div>

                <h1>
                  Notifications
                </h1>

                <p>
                  Manage medicine expiry
                  notifications and patient communication.
                </p>

              </div>

            </div>

            <Notifications />

          </div>
        )}

        {/* ===============================================
            PROFILE
        =============================================== */}

        {currentPage === "profile" && (
          <div className="page-container">

            <div className="page-header">

              <div>

                <h1>
                  Profile
                </h1>

                <p>
                  View your MediTrack account details.
                </p>

              </div>

            </div>

            <div className="card profile-details">

              <div className="profile-row">

                <span>
                  Name
                </span>

                <strong>
                  {user.name || "—"}
                </strong>

              </div>

              <div className="profile-row">

                <span>
                  Email
                </span>

                <strong>
                  {user.email || "—"}
                </strong>

              </div>

              <div className="profile-row">

                <span>
                  Phone
                </span>

                <strong>
                  {user.phone || "—"}
                </strong>

              </div>

              <div className="profile-row">

                <span>
                  Role
                </span>

                <strong>
                  {user.role || "—"}
                </strong>

              </div>

              <div className="profile-row">

                <span>
                  Account Status
                </span>

                <strong>
                  {user.is_active
                    ? "Active"
                    : "Inactive"}
                </strong>

              </div>

            </div>

          </div>
        )}

      </main>

    </div>
  );
}

export default App; 