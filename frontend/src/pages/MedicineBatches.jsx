import { useEffect, useState } from "react";

function MedicineBatches() {
  const API_URL = "http://127.0.0.1:8000";

  const emptyForm = {
    medicine_id: "",
    batch_number: "",
    manufacturing_date: "",
    expiry_date: "",
  };

  const [medicines, setMedicines] = useState([]);
  const [batches, setBatches] = useState([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [editingBatch, setEditingBatch] = useState(null);

  const [formData, setFormData] = useState(emptyForm);

  // =========================================================
  // FETCH MEDICINES AND BATCHES
  // =========================================================

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("Please login again.");
        return;
      }

      // -----------------------------------------------------
      // FETCH MEDICINES
      // -----------------------------------------------------

      const medicineResponse = await fetch(
        `${API_URL}/medicines`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const medicineData = await medicineResponse.json();

      if (!medicineResponse.ok) {
        setError(
          medicineData.detail ||
            "Unable to fetch medicines"
        );
        return;
      }

      setMedicines(medicineData);

      // -----------------------------------------------------
      // FETCH EXPIRY LIST
      // -----------------------------------------------------

      const batchResponse = await fetch(
        `${API_URL}/medicine-batches/expiry-list`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const batchData = await batchResponse.json();

      if (!batchResponse.ok) {
        setError(
          batchData.detail ||
            "Unable to fetch medicine batches"
        );
        return;
      }

      setBatches(batchData);
    } catch (error) {
      console.error(error);

      setError(
        "Unable to connect to MediTrack backend."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // =========================================================
  // FORM CHANGE
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
    setEditingBatch(null);
    setFormData(emptyForm);
    setError("");
    setSuccess("");
    setShowForm(true);
  };

  // =========================================================
  // OPEN EDIT FORM
  // =========================================================

  const openEditForm = async (batch) => {
    setError("");
    setSuccess("");

    try {
      const token = localStorage.getItem("access_token");

      const response = await fetch(
        `${API_URL}/medicine-batches/${batch.batch_id}`,
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
            "Unable to load batch details"
        );
        return;
      }

      setEditingBatch(data);

      setFormData({
        medicine_id:
          data.medicine_id?.toString() || "",
        batch_number:
          data.batch_number || "",
        manufacturing_date:
          data.manufacturing_date || "",
        expiry_date:
          data.expiry_date || "",
      });

      setShowForm(true);

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } catch (error) {
      console.error(error);

      setError(
        "Unable to connect to MediTrack backend."
      );
    }
  };

  // =========================================================
  // CLOSE FORM
  // =========================================================

  const closeForm = () => {
    setShowForm(false);
    setEditingBatch(null);
    setFormData(emptyForm);
    setError("");
  };

  // =========================================================
  // ADD / UPDATE BATCH
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

      const isEditing = editingBatch !== null;

      const url = isEditing
        ? `${API_URL}/medicine-batches/${editingBatch.id}`
        : `${API_URL}/medicine-batches`;

      const method = isEditing ? "PUT" : "POST";

      const response = await fetch(url, {
        method: method,

        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },

        body: JSON.stringify({
          medicine_id: Number(formData.medicine_id),

          batch_number:
            formData.batch_number,

          manufacturing_date:
            formData.manufacturing_date || null,

          expiry_date:
            formData.expiry_date,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            (isEditing
              ? "Unable to update medicine batch"
              : "Unable to create medicine batch")
        );

        return;
      }

      // -----------------------------------------------------
      // SUCCESS
      // -----------------------------------------------------

      if (isEditing) {
        setSuccess(
          "Medicine batch updated successfully."
        );
      } else {
        setSuccess(
          "Medicine batch added successfully."
        );
      }

      setFormData(emptyForm);
      setEditingBatch(null);
      setShowForm(false);

      // Refresh expiry list
      await fetchData();
    } catch (error) {
      console.error(error);

      setError(
        "Unable to connect to MediTrack backend."
      );
    } finally {
      setSaving(false);
    }
  };

  // =========================================================
  // EXPIRY STATUS
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
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="page-container">
        <h2>Medicine Batches</h2>
        <p>Loading medicine batches...</p>
      </div>
    );
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="page-container">

      {/* ===================================================
          HEADER
      ==================================================== */}

      <div className="page-header">

        <div>

          <h2>
            Medicine Batches
          </h2>

          <p>
            Track medicine batches and expiry dates.
          </p>

        </div>

        <button
          className="primary-button"
          onClick={
            showForm
              ? closeForm
              : openAddForm
          }
        >
          {showForm
            ? "Cancel"
            : "+ Add Batch"}
        </button>

      </div>

      {/* ===================================================
          SUCCESS
      ==================================================== */}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      {/* ===================================================
          ERROR
      ==================================================== */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* ===================================================
          ADD / EDIT FORM
      ==================================================== */}

      {showForm && (

        <form
          className="medicine-form"
          onSubmit={handleSubmit}
        >

          <h3>
            {editingBatch
              ? "Edit Medicine Batch"
              : "Add Medicine Batch"}
          </h3>

          <div className="form-grid">

            {/* MEDICINE */}

            <div className="form-group">

              <label>
                Medicine *
              </label>

              <select
                name="medicine_id"
                value={formData.medicine_id}
                onChange={handleChange}
                required
              >

                <option value="">
                  Select medicine
                </option>

                {medicines.map(
                  (medicine) => (

                    <option
                      key={medicine.id}
                      value={medicine.id}
                    >
                      {medicine.medicine_name}
                    </option>

                  )
                )}

              </select>

            </div>

            {/* BATCH NUMBER */}

            <div className="form-group">

              <label>
                Batch Number *
              </label>

              <input
                type="text"
                name="batch_number"
                placeholder="Example: BATCH-001"
                value={formData.batch_number}
                onChange={handleChange}
                required
              />

            </div>

            {/* MANUFACTURING DATE */}

            <div className="form-group">

              <label>
                Manufacturing Date
              </label>

              <input
                type="date"
                name="manufacturing_date"
                value={
                  formData.manufacturing_date
                }
                onChange={handleChange}
              />

            </div>

            {/* EXPIRY DATE */}

            <div className="form-group">

              <label>
                Expiry Date *
              </label>

              <input
                type="date"
                name="expiry_date"
                value={
                  formData.expiry_date
                }
                onChange={handleChange}
                required
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
                : editingBatch
                ? "Update Batch"
                : "Save Batch"}
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

      {/* ===================================================
          SUMMARY
      ==================================================== */}

      <div className="medicine-summary">

        <span>
          Total Batches
        </span>

        <strong>
          {batches.length}
        </strong>

      </div>

      {/* ===================================================
          EMPTY STATE
      ==================================================== */}

      {batches.length === 0 ? (

        <div className="empty-state">

          <div className="empty-icon">
            📦
          </div>

          <h3>
            No medicine batches found
          </h3>

          <p>
            Add a batch to start tracking
            medicine expiry dates.
          </p>

          <button
            className="primary-button"
            onClick={openAddForm}
          >
            + Add Your First Batch
          </button>

        </div>

      ) : (

        /* =================================================
           TABLE
        ================================================== */

        <div className="medicine-table-container">

          <table className="medicine-table">

            <thead>

              <tr>

                <th>
                  ID
                </th>

                <th>
                  Medicine
                </th>

                <th>
                  Batch Number
                </th>

                <th>
                  Manufacturing Date
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

                <th>
                  Actions
                </th>

              </tr>

            </thead>

            <tbody>

              {batches.map(
                (batch) => (

                  <tr
                    key={batch.batch_id}
                    className={getStatusClass(
                      batch.status
                    )}
                  >

                    {/* ID */}

                    <td>
                      {batch.batch_id}
                    </td>

                    {/* MEDICINE */}

                    <td>

                      <strong>
                        {batch.medicine_name}
                      </strong>

                    </td>

                    {/* BATCH */}

                    <td>
                      {batch.batch_number}
                    </td>

                    {/* MANUFACTURING DATE */}

                    <td>
                      {batch.manufacturing_date
                        ? new Date(
                            batch.manufacturing_date
                          ).toLocaleDateString(
                            "en-IN"
                          )
                        : "-"}
                    </td>

                    {/* EXPIRY DATE */}

                    <td>

                      {new Date(
                        batch.expiry_date
                      ).toLocaleDateString(
                        "en-IN"
                      )}

                    </td>

                    {/* DAYS */}

                    <td>

                      {batch.days_remaining < 0
                        ? `${Math.abs(
                            batch.days_remaining
                          )} days ago`
                        : batch.days_remaining === 0
                        ? "Today"
                        : `${batch.days_remaining} days`}

                    </td>

                    {/* STATUS */}

                    <td>

                      <span
                        className={`expiry-badge ${getStatusClass(
                          batch.status
                        )}`}
                      >
                        {getStatusText(
                          batch.status
                        )}
                      </span>

                    </td>

                    {/* ACTIONS */}

                    <td>

                      <button
                        type="button"
                        className="edit-button"
                        onClick={() =>
                          openEditForm(batch)
                        }
                      >
                        Edit
                      </button>

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

export default MedicineBatches;