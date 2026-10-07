import { useEffect, useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function Prescriptions() {
  const token = localStorage.getItem("access_token");

  const [patients, setPatients] = useState([]);
  const [medicines, setMedicines] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);

  const [selectedPrescription, setSelectedPrescription] =
    useState(null);

  const [prescriptionMedicines, setPrescriptionMedicines] =
    useState([]);

  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // =========================================================
  // PRESCRIPTION FORM
  // =========================================================

  const [prescriptionForm, setPrescriptionForm] = useState({
    patient_id: "",
    doctor_id: "",
    prescription_date:
      new Date().toISOString().split("T")[0],
    prescription_image: "",
  });

  // =========================================================
  // MEDICINE FORM
  // =========================================================

  const [medicineForm, setMedicineForm] = useState({
    medicine_id: "",
    dosage: "",
    frequency: "",
    timing: "",
    food_instruction: "",
    duration_days: "",
    quantity: "",
  });

  // =========================================================
  // ERROR HANDLER
  // =========================================================

  const getErrorMessage = async (response) => {
    try {
      const data = await response.json();

      if (data?.detail) {
        if (Array.isArray(data.detail)) {
          return data.detail
            .map(
              (item) =>
                item.msg || JSON.stringify(item)
            )
            .join(", ");
        }

        return data.detail;
      }

      return "Something went wrong.";
    } catch {
      return `Request failed with status ${response.status}`;
    }
  };

  // =========================================================
  // LOAD PATIENTS
  // =========================================================

  const loadPatients = async () => {
    try {
      const response = await fetch(
        `${API_URL}/patients`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          await getErrorMessage(response)
        );
      }

      const data = await response.json();

      setPatients(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      setError(err.message);
    }
  };

  // =========================================================
  // LOAD MEDICINES
  // =========================================================

  const loadMedicines = async () => {
    try {
      const response = await fetch(
        `${API_URL}/medicines`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          await getErrorMessage(response)
        );
      }

      const data = await response.json();

      setMedicines(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      setError(err.message);
    }
  };

  // =========================================================
  // LOAD PRESCRIPTIONS
  // =========================================================

  const loadPrescriptions = async () => {
    try {
      const response = await fetch(
        `${API_URL}/prescriptions`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          await getErrorMessage(response)
        );
      }

      const data = await response.json();

      setPrescriptions(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      setError(err.message);
    }
  };

  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    if (!token) {
      setError("You are not logged in.");
      setInitialLoading(false);
      return;
    }

    const loadAllData = async () => {
      setInitialLoading(true);

      await Promise.all([
        loadPatients(),
        loadMedicines(),
        loadPrescriptions(),
      ]);

      setInitialLoading(false);
    };

    loadAllData();
  }, []);

  // =========================================================
  // CREATE PRESCRIPTION
  // =========================================================

  const createPrescription = async (event) => {
    event.preventDefault();

    setError("");
    setMessage("");
    setLoading(true);

    try {
      if (!prescriptionForm.patient_id) {
        throw new Error(
          "Please select a patient."
        );
      }

      const body = {
        patient_id: Number(
          prescriptionForm.patient_id
        ),

        doctor_id: prescriptionForm.doctor_id
          ? Number(prescriptionForm.doctor_id)
          : null,

        prescription_date:
          prescriptionForm.prescription_date,

        prescription_image:
          prescriptionForm.prescription_image ||
          null,
      };

      const response = await fetch(
        `${API_URL}/prescriptions`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify(body),
        }
      );

      if (!response.ok) {
        throw new Error(
          await getErrorMessage(response)
        );
      }

      const data = await response.json();

      setSelectedPrescription(data);

      setMessage(
        `Prescription #${data.id} created successfully.`
      );

      setPrescriptionForm({
        patient_id: "",
        doctor_id: "",
        prescription_date:
          new Date().toISOString().split("T")[0],
        prescription_image: "",
      });

      await loadPrescriptions();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // ADD MEDICINE TO PRESCRIPTION
  // =========================================================

  const addMedicine = async (event) => {
    event.preventDefault();

    setError("");
    setMessage("");
    setLoading(true);

    try {
      if (!selectedPrescription) {
        throw new Error(
          "Please create or select a prescription first."
        );
      }

      if (!medicineForm.medicine_id) {
        throw new Error(
          "Please select a medicine."
        );
      }

      if (!medicineForm.dosage.trim()) {
        throw new Error(
          "Please enter the dosage."
        );
      }

      if (!medicineForm.frequency.trim()) {
        throw new Error(
          "Please enter the frequency."
        );
      }

      if (!medicineForm.duration_days) {
        throw new Error(
          "Please enter the duration."
        );
      }

      if (!medicineForm.quantity) {
        throw new Error(
          "Please enter the quantity."
        );
      }

      const body = {
        medicine_id: Number(
          medicineForm.medicine_id
        ),

        dosage: medicineForm.dosage,

        frequency: medicineForm.frequency,

        timing:
          medicineForm.timing || null,

        food_instruction:
          medicineForm.food_instruction || null,

        duration_days: Number(
          medicineForm.duration_days
        ),

        quantity: Number(
          medicineForm.quantity
        ),
      };

      const response = await fetch(
        `${API_URL}/prescriptions/${selectedPrescription.id}/medicines`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify(body),
        }
      );

      if (!response.ok) {
        throw new Error(
          await getErrorMessage(response)
        );
      }

      await response.json();

      setMessage(
        "Medicine added to prescription successfully."
      );

      setMedicineForm({
        medicine_id: "",
        dosage: "",
        frequency: "",
        timing: "",
        food_instruction: "",
        duration_days: "",
        quantity: "",
      });

      await loadPrescriptionMedicines(
        selectedPrescription.id
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // LOAD PRESCRIPTION MEDICINES
  // =========================================================

  const loadPrescriptionMedicines = async (
    prescriptionId
  ) => {
    try {
      const response = await fetch(
        `${API_URL}/prescriptions/${prescriptionId}/medicines`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          await getErrorMessage(response)
        );
      }

      const data = await response.json();

      setPrescriptionMedicines(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      setError(err.message);
    }
  };

  // =========================================================
  // SELECT EXISTING PRESCRIPTION
  // =========================================================

  const selectPrescription = async (
    prescription
  ) => {
    setSelectedPrescription(
      prescription
    );

    setMessage("");
    setError("");

    await loadPrescriptionMedicines(
      prescription.id
    );
  };

  // =========================================================
  // GET PATIENT NAME
  // =========================================================

  const getPatientName = (patientId) => {
    const patient = patients.find(
      (item) => item.id === patientId
    );

    if (!patient) {
      return `Patient #${patientId}`;
    }

    return (
      patient.name ||
      patient.full_name ||
      patient.user_name ||
      `Patient #${patientId}`
    );
  };

  // =========================================================
  // GET MEDICINE NAME
  // =========================================================

  const getMedicineName = (medicineId) => {
    const medicine = medicines.find(
      (item) => item.id === medicineId
    );

    if (!medicine) {
      return `Medicine #${medicineId}`;
    }

    return (
      medicine.medicine_name ||
      medicine.name ||
      `Medicine #${medicineId}`
    );
  };

  // =========================================================
  // LOADING
  // =========================================================

  if (initialLoading) {
    return (
      <div className="page-container">
        <h2>Prescription Management</h2>
        <p>Loading prescription data...</p>
      </div>
    );
  }

  // =========================================================
  // JSX
  // =========================================================

  return (
    <div className="page-container">

      {/* ===================================================
          HEADER
      ==================================================== */}

      <div className="page-header">

        <div>

          <h1>
            Prescription Management
          </h1>

          <p>
            Create prescriptions and manage
            prescribed medicines.
          </p>

        </div>

      </div>

      {/* ===================================================
          MESSAGES
      ==================================================== */}

      {message && (
        <div className="success-message">
          {message}
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* ===================================================
          CREATE PRESCRIPTION
      ==================================================== */}

      <div className="card">

        <h2>
          Create Prescription
        </h2>

        <form
          onSubmit={createPrescription}
        >

          <div className="form-grid">

            {/* PATIENT */}

            <div className="form-group">

              <label>
                Patient *
              </label>

              <select
                value={
                  prescriptionForm.patient_id
                }
                onChange={(event) =>
                  setPrescriptionForm({
                    ...prescriptionForm,
                    patient_id:
                      event.target.value,
                  })
                }
                required
              >

                <option value="">
                  Select Patient
                </option>

                {patients.map(
                  (patient) => (

                    <option
                      key={patient.id}
                      value={patient.id}
                    >
                      {getPatientName(
                        patient.id
                      )}
                    </option>

                  )
                )}

              </select>

            </div>

            {/* DOCTOR */}

            <div className="form-group">

              <label>
                Doctor ID{" "}
                <span className="optional">
                  (Optional)
                </span>
              </label>

              <input
                type="number"
                min="1"
                placeholder="Enter doctor ID"
                value={
                  prescriptionForm.doctor_id
                }
                onChange={(event) =>
                  setPrescriptionForm({
                    ...prescriptionForm,
                    doctor_id:
                      event.target.value,
                  })
                }
              />

            </div>

            {/* DATE */}

            <div className="form-group">

              <label>
                Prescription Date
              </label>

              <input
                type="date"
                value={
                  prescriptionForm.prescription_date
                }
                onChange={(event) =>
                  setPrescriptionForm({
                    ...prescriptionForm,
                    prescription_date:
                      event.target.value,
                  })
                }
                required
              />

            </div>

            {/* IMAGE */}

            <div className="form-group">

              <label>
                Prescription Image{" "}
                <span className="optional">
                  (Optional)
                </span>
              </label>

              <input
                type="text"
                placeholder="Image path / URL"
                value={
                  prescriptionForm.prescription_image
                }
                onChange={(event) =>
                  setPrescriptionForm({
                    ...prescriptionForm,
                    prescription_image:
                      event.target.value,
                  })
                }
              />

            </div>

          </div>

          <button
            type="submit"
            className="primary-button"
            disabled={loading}
          >
            {loading
              ? "Creating..."
              : "Create Prescription"}
          </button>

        </form>

      </div>

      {/* ===================================================
          PRESCRIPTION HISTORY
      ==================================================== */}

      <div className="card">

        <div className="section-header">

          <div>

            <h2>
              Prescription History
            </h2>

            <p>
              Select a prescription to view
              its prescribed medicines.
            </p>

          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={loadPrescriptions}
          >
            ↻ Refresh
          </button>

        </div>

        {prescriptions.length === 0 ? (

          <div className="empty-state">

            <div className="empty-icon">
              📋
            </div>

            <h3>
              No prescriptions found
            </h3>

            <p>
              Create a prescription to
              start managing patient medication.
            </p>

          </div>

        ) : (

          <div className="table-container">

            <table>

              <thead>

                <tr>

                  <th>
                    ID
                  </th>

                  <th>
                    Patient
                  </th>

                  <th>
                    Date
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                    Action
                  </th>

                </tr>

              </thead>

              <tbody>

                {prescriptions.map(
                  (prescription) => (

                    <tr
                      key={
                        prescription.id
                      }
                    >

                      <td>
                        #
                        {
                          prescription.id
                        }
                      </td>

                      <td>
                        {getPatientName(
                          prescription.patient_id
                        )}
                      </td>

                      <td>
                        {
                          prescription.prescription_date
                        }
                      </td>

                      <td>

                        <span className="status-badge">
                          {
                            prescription.status
                          }
                        </span>

                      </td>

                      <td>

                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() =>
                            selectPrescription(
                              prescription
                            )
                          }
                        >
                          View
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

      {/* ===================================================
          SELECTED PRESCRIPTION
      ==================================================== */}

      {selectedPrescription && (

        <div className="card">

          <div className="selected-prescription-header">

            <div>

              <h2>
                Prescription #
                {
                  selectedPrescription.id
                }
              </h2>

              <p>
                <strong>
                  Patient:
                </strong>{" "}
                {getPatientName(
                  selectedPrescription.patient_id
                )}
              </p>

              <p>
                <strong>
                  Date:
                </strong>{" "}
                {
                  selectedPrescription.prescription_date
                }
              </p>

              <p>
                <strong>
                  Status:
                </strong>{" "}
                {
                  selectedPrescription.status
                }
              </p>

            </div>

          </div>

          {/* =================================================
              ADD MEDICINE
          ================================================== */}

          <div className="section-divider">

            <h3>
              Add Medicine
            </h3>

            <form
              onSubmit={addMedicine}
            >

              <div className="form-grid">

                {/* MEDICINE */}

                <div className="form-group">

                  <label>
                    Medicine *
                  </label>

                  <select
                    value={
                      medicineForm.medicine_id
                    }
                    onChange={(event) =>
                      setMedicineForm({
                        ...medicineForm,
                        medicine_id:
                          event.target.value,
                      })
                    }
                    required
                  >

                    <option value="">
                      Select Medicine
                    </option>

                    {medicines.map(
                      (medicine) => (

                        <option
                          key={medicine.id}
                          value={medicine.id}
                        >
                          {
                            medicine.medicine_name
                          }
                        </option>

                      )
                    )}

                  </select>

                </div>

                {/* DOSAGE */}

                <div className="form-group">

                  <label>
                    Dosage *
                  </label>

                  <input
                    type="text"
                    placeholder="Example: 500 mg"
                    value={
                      medicineForm.dosage
                    }
                    onChange={(event) =>
                      setMedicineForm({
                        ...medicineForm,
                        dosage:
                          event.target.value,
                      })
                    }
                    required
                  />

                </div>

                {/* FREQUENCY */}

                <div className="form-group">

                  <label>
                    Frequency *
                  </label>

                  <input
                    type="text"
                    placeholder="Example: Twice a day"
                    value={
                      medicineForm.frequency
                    }
                    onChange={(event) =>
                      setMedicineForm({
                        ...medicineForm,
                        frequency:
                          event.target.value,
                      })
                    }
                    required
                  />

                </div>

                {/* TIMING */}

                <div className="form-group">

                  <label>
                    Timing
                  </label>

                  <input
                    type="text"
                    placeholder="Example: Morning and Night"
                    value={
                      medicineForm.timing
                    }
                    onChange={(event) =>
                      setMedicineForm({
                        ...medicineForm,
                        timing:
                          event.target.value,
                      })
                    }
                  />

                </div>

                {/* FOOD */}

                <div className="form-group">

                  <label>
                    Food Instruction
                  </label>

                  <input
                    type="text"
                    placeholder="Example: After food"
                    value={
                      medicineForm.food_instruction
                    }
                    onChange={(event) =>
                      setMedicineForm({
                        ...medicineForm,
                        food_instruction:
                          event.target.value,
                      })
                    }
                  />

                </div>

                {/* DURATION */}

                <div className="form-group">

                  <label>
                    Duration (Days) *
                  </label>

                  <input
                    type="number"
                    min="1"
                    placeholder="Example: 5"
                    value={
                      medicineForm.duration_days
                    }
                    onChange={(event) =>
                      setMedicineForm({
                        ...medicineForm,
                        duration_days:
                          event.target.value,
                      })
                    }
                    required
                  />

                </div>

                {/* QUANTITY */}

                <div className="form-group">

                  <label>
                    Quantity *
                  </label>

                  <input
                    type="number"
                    min="1"
                    placeholder="Example: 10"
                    value={
                      medicineForm.quantity
                    }
                    onChange={(event) =>
                      setMedicineForm({
                        ...medicineForm,
                        quantity:
                          event.target.value,
                      })
                    }
                    required
                  />

                </div>

              </div>

              <button
                type="submit"
                className="primary-button"
                disabled={loading}
              >
                {loading
                  ? "Adding..."
                  : "Add Medicine"}
              </button>

            </form>

          </div>

          {/* =================================================
              PRESCRIBED MEDICINES
          ================================================== */}

          <div className="section-divider">

            <h3>
              Prescribed Medicines
            </h3>

            {prescriptionMedicines.length ===
            0 ? (

              <div className="empty-state">

                <div className="empty-icon">
                  💊
                </div>

                <p>
                  No medicines added to
                  this prescription yet.
                </p>

              </div>

            ) : (

              <div className="table-container">

                <table>

                  <thead>

                    <tr>

                      <th>
                        Medicine
                      </th>

                      <th>
                        Dosage
                      </th>

                      <th>
                        Frequency
                      </th>

                      <th>
                        Timing
                      </th>

                      <th>
                        Food
                      </th>

                      <th>
                        Duration
                      </th>

                      <th>
                        Quantity
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {prescriptionMedicines.map(
                      (item) => (

                        <tr
                          key={item.id}
                        >

                          <td>
                            <strong>
                              {getMedicineName(
                                item.medicine_id
                              )}
                            </strong>
                          </td>

                          <td>
                            {item.dosage}
                          </td>

                          <td>
                            {item.frequency}
                          </td>

                          <td>
                            {item.timing ||
                              "-"}
                          </td>

                          <td>
                            {
                              item.food_instruction ||
                              "-"
                            }
                          </td>

                          <td>
                            {
                              item.duration_days
                            }{" "}
                            days
                          </td>

                          <td>
                            {item.quantity}
                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            )}

          </div>

        </div>

      )}

    </div>
  );
}

export default Prescriptions;