import { useEffect, useState } from "react";

function Medicines() {
 const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const emptyForm = {
    medicine_name: "",
    generic_name: "",
    strength: "",
    dosage_form: "",
    manufacturer: "",
  };

  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  const [editingMedicine, setEditingMedicine] = useState(null);

  const [formData, setFormData] = useState(emptyForm);

  // =========================================================
  // FETCH MEDICINES
  // =========================================================

  const fetchMedicines = async () => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("Please login again.");
        return;
      }

      const response = await fetch(`${API_URL}/medicines`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Unable to fetch medicines");
        return;
      }

      setMedicines(data);
    } catch (error) {
      console.error(error);
      setError("Unable to connect to MediTrack backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMedicines();
  }, []);

  // =========================================================
  // FORM INPUT CHANGE
  // =========================================================

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // =========================================================
  // OPEN ADD FORM
  // =========================================================

  const openAddForm = () => {
    setEditingMedicine(null);
    setFormData(emptyForm);
    setError("");
    setSuccess("");
    setShowForm(true);
  };

  // =========================================================
  // OPEN EDIT FORM
  // =========================================================

  const openEditForm = (medicine) => {
    setEditingMedicine(medicine);

    setFormData({
      medicine_name: medicine.medicine_name || "",
      generic_name: medicine.generic_name || "",
      strength: medicine.strength || "",
      dosage_form: medicine.dosage_form || "",
      manufacturer: medicine.manufacturer || "",
    });

    setError("");
    setSuccess("");
    setShowForm(true);

    // Scroll to form
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // =========================================================
  // CLOSE FORM
  // =========================================================

  const closeForm = () => {
    setShowForm(false);
    setEditingMedicine(null);
    setFormData(emptyForm);
    setError("");
  };

  // =========================================================
  // ADD / UPDATE MEDICINE
  // =========================================================

  const handleSubmit = async (e) => {
    e.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("Please login again.");
        return;
      }

      const isEditing = editingMedicine !== null;

      const url = isEditing
        ? `${API_URL}/medicines/${editingMedicine.id}`
        : `${API_URL}/medicines`;

      const method = isEditing ? "PUT" : "POST";

      const response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            (isEditing
              ? "Unable to update medicine"
              : "Unable to add medicine")
        );
        return;
      }

      // =====================================================
      // UPDATE EXISTING MEDICINE IN TABLE
      // =====================================================

      if (isEditing) {
        setMedicines((previousMedicines) =>
          previousMedicines.map((medicine) =>
            medicine.id === editingMedicine.id ? data : medicine
          )
        );

        setSuccess("Medicine updated successfully.");
      }

      // =====================================================
      // ADD NEW MEDICINE TO TABLE
      // =====================================================

      else {
        setMedicines((previousMedicines) => [
          ...previousMedicines,
          data,
        ]);

        setSuccess("Medicine added successfully.");
      }

      setFormData(emptyForm);
      setEditingMedicine(null);
      setShowForm(false);
    } catch (error) {
      console.error(error);
      setError("Unable to connect to MediTrack backend.");
    } finally {
      setSaving(false);
    }
  };

  // =========================================================
  // DELETE MEDICINE
  // =========================================================

  const handleDelete = async (medicine) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${medicine.medicine_name}"?`
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("Please login again.");
        return;
      }

      const response = await fetch(
        `${API_URL}/medicines/${medicine.id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Unable to delete medicine");
        return;
      }

      // Remove deleted medicine from table
      setMedicines((previousMedicines) =>
        previousMedicines.filter(
          (item) => item.id !== medicine.id
        )
      );

      setSuccess("Medicine deleted successfully.");
    } catch (error) {
      console.error(error);
      setError("Unable to connect to MediTrack backend.");
    }
  };

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="page-container">
        <h2>Medicines</h2>
        <p>Loading medicines...</p>
      </div>
    );
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="page-container">

      {/* =====================================================
          PAGE HEADER
      ====================================================== */}

      <div className="page-header">
        <div>
          <h2>Medicines</h2>

          <p>
            Manage medicines available in your pharmacy.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={showForm ? closeForm : openAddForm}
        >
          {showForm ? "Cancel" : "+ Add Medicine"}
        </button>
      </div>

      {/* =====================================================
          SUCCESS MESSAGE
      ====================================================== */}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      {/* =====================================================
          ERROR MESSAGE
      ====================================================== */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* =====================================================
          ADD / EDIT MEDICINE FORM
      ====================================================== */}

      {showForm && (
        <form
          className="medicine-form"
          onSubmit={handleSubmit}
        >

          <h3>
            {editingMedicine
              ? "Edit Medicine"
              : "Add New Medicine"}
          </h3>

          <div className="form-grid">

            {/* MEDICINE NAME */}

            <div className="form-group">
              <label>
                Medicine Name *
              </label>

              <input
                type="text"
                name="medicine_name"
                placeholder="Example: Paracetamol"
                value={formData.medicine_name}
                onChange={handleChange}
                required
              />
            </div>

            {/* GENERIC NAME */}

            <div className="form-group">
              <label>
                Generic Name
              </label>

              <input
                type="text"
                name="generic_name"
                placeholder="Example: Acetaminophen"
                value={formData.generic_name}
                onChange={handleChange}
              />
            </div>

            {/* STRENGTH */}

            <div className="form-group">
              <label>
                Strength
              </label>

              <input
                type="text"
                name="strength"
                placeholder="Example: 500 mg"
                value={formData.strength}
                onChange={handleChange}
              />
            </div>

            {/* DOSAGE FORM */}

            <div className="form-group">
              <label>
                Dosage Form
              </label>

              <select
                name="dosage_form"
                value={formData.dosage_form}
                onChange={handleChange}
              >
                <option value="">
                  Select form
                </option>

                <option value="Tablet">
                  Tablet
                </option>

                <option value="Capsule">
                  Capsule
                </option>

                <option value="Syrup">
                  Syrup
                </option>

                <option value="Injection">
                  Injection
                </option>

                <option value="Cream">
                  Cream
                </option>

                <option value="Drops">
                  Drops
                </option>

                <option value="Powder">
                  Powder
                </option>

                <option value="Other">
                  Other
                </option>
              </select>
            </div>

            {/* MANUFACTURER */}

            <div className="form-group">
              <label>
                Manufacturer
              </label>

              <input
                type="text"
                name="manufacturer"
                placeholder="Example: ABC Pharma"
                value={formData.manufacturer}
                onChange={handleChange}
              />
            </div>

          </div>

          {/* FORM BUTTONS */}

          <div className="medicine-form-actions">

            <button
              type="submit"
              className="save-button"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingMedicine
                ? "Update Medicine"
                : "Save Medicine"}
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={closeForm}
              disabled={saving}
            >
              Cancel
            </button>

          </div>

        </form>
      )}

      {/* =====================================================
          MEDICINE COUNT
      ====================================================== */}

      <div className="medicine-summary">
        <span>
          Total Medicines
        </span>

        <strong>
          {medicines.length}
        </strong>
      </div>

      {/* =====================================================
          EMPTY STATE
      ====================================================== */}

      {medicines.length === 0 ? (

        <div className="empty-state">

          <div className="empty-icon">
            💊
          </div>

          <h3>
            No medicines found
          </h3>

          <p>
            Add a medicine to start managing
            your pharmacy inventory.
          </p>

          <button
            className="primary-button"
            onClick={openAddForm}
          >
            + Add Your First Medicine
          </button>

        </div>

      ) : (

        /* ===================================================
           MEDICINE TABLE
        ==================================================== */

        <div className="medicine-table-container">

          <table className="medicine-table">

            <thead>

              <tr>

                <th>ID</th>

                <th>
                  Medicine Name
                </th>

                <th>
                  Generic Name
                </th>

                <th>
                  Strength
                </th>

                <th>
                  Dosage Form
                </th>

                <th>
                  Manufacturer
                </th>

                <th>
                  Status
                </th>

                <th>
                  Actions
                </th>

              </tr>

            </thead>

            <tbody>

              {medicines.map((medicine) => (

                <tr key={medicine.id}>

                  {/* ID */}

                  <td>
                    {medicine.id}
                  </td>

                  {/* MEDICINE NAME */}

                  <td>
                    <strong>
                      {medicine.medicine_name}
                    </strong>
                  </td>

                  {/* GENERIC NAME */}

                  <td>
                    {medicine.generic_name || "-"}
                  </td>

                  {/* STRENGTH */}

                  <td>
                    {medicine.strength || "-"}
                  </td>

                  {/* DOSAGE FORM */}

                  <td>
                    {medicine.dosage_form || "-"}
                  </td>

                  {/* MANUFACTURER */}

                  <td>
                    {medicine.manufacturer || "-"}
                  </td>

                  {/* STATUS */}

                  <td>

                    <span
                      className={
                        medicine.is_active
                          ? "status-active"
                          : "status-inactive"
                      }
                    >
                      {medicine.is_active
                        ? "Active"
                        : "Inactive"}
                    </span>

                  </td>

                  {/* ACTIONS */}

                  <td>

                    <div className="medicine-actions">

                      <button
                        type="button"
                        className="edit-button"
                        onClick={() =>
                          openEditForm(medicine)
                        }
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="delete-button"
                        onClick={() =>
                          handleDelete(medicine)
                        }
                      >
                        Delete
                      </button>

                    </div>

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      )}

    </div>
  );
}

export default Medicines;