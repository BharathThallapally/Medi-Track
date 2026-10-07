import { useEffect, useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function Purchases() {
  const [purchases, setPurchases] = useState([]);
  const [patients, setPatients] = useState([]);
  const [medicines, setMedicines] = useState([]);
  const [batches, setBatches] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);
  const [prescribedMedicines, setPrescribedMedicines] = useState([]);
  const [selectedPurchase, setSelectedPurchase] = useState(null);
  const [selectedPrescribedMedicine, setSelectedPrescribedMedicine] =
    useState(null);

  const [loading, setLoading] = useState(true);
  const [loadingPrescriptionMedicines, setLoadingPrescriptionMedicines] =
    useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [purchaseForm, setPurchaseForm] = useState({
    patient_id: "",
    prescription_id: "",
    total_amount: "",
    email: "",
    phone: "",
    email_enabled: true,
    whatsapp_enabled: false,
    sms_enabled: false,
    notification_consent: false,
  });

  const [itemForm, setItemForm] = useState({
    medicine_id: "",
    batch_id: "",
    quantity: "",
    unit_price: "",
  });

  const token = localStorage.getItem("access_token");

  const getErrorMessage = (data, fallbackMessage) => {
    if (!data) {
      return fallbackMessage;
    }

    if (typeof data === "string") {
      return data;
    }

    if (data.detail) {
      if (typeof data.detail === "string") {
        return data.detail;
      }

      if (Array.isArray(data.detail)) {
        return data.detail
          .map((item) => item.msg || JSON.stringify(item))
          .join(", ");
      }

      if (typeof data.detail === "object") {
        return (
          data.detail.msg ||
          data.detail.message ||
          JSON.stringify(data.detail)
        );
      }
    }

    if (data.message) {
      if (typeof data.message === "string") {
        return data.message;
      }

      return JSON.stringify(data.message);
    }

    return fallbackMessage;
  };

  useEffect(() => {
    loadPurchases();
    loadPatients();
    loadMedicines();
    loadPrescriptions();
  }, []);

  const loadPurchases = async () => {
    try {
      setLoading(true);
      setError("");

      if (!token) {
        throw new Error(
          "Authentication token not found. Please login again."
        );
      }

      const response = await fetch(`${API_URL}/purchases`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data, "Failed to load purchases")
        );
      }

      setPurchases(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Purchase loading error:", err);
      setError(err.message || "Failed to load purchases");
    } finally {
      setLoading(false);
    }
  };

  const loadPatients = async () => {
    try {
      if (!token) {
        return;
      }

      const response = await fetch(`${API_URL}/patients`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data, "Failed to load patients")
        );
      }

      setPatients(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Patient loading error:", err);
      setError(err.message || "Failed to load patients");
    }
  };

  const loadMedicines = async () => {
    try {
      if (!token) {
        return;
      }

      const response = await fetch(`${API_URL}/medicines`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data, "Failed to load medicines")
        );
      }

      setMedicines(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Medicine loading error:", err);
      setError(err.message || "Failed to load medicines");
    }
  };

  const loadPrescriptions = async () => {
    try {
      if (!token) {
        return;
      }

      const response = await fetch(`${API_URL}/prescriptions`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data, "Failed to load prescriptions")
        );
      }

      setPrescriptions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Prescription loading error:", err);

      setError(
        err.message || "Failed to load prescriptions"
      );
    }
  };

  const loadPrescriptionMedicines = async (prescriptionId) => {
    if (!prescriptionId) {
      setPrescribedMedicines([]);
      setSelectedPrescribedMedicine(null);
      return;
    }

    try {
      setLoadingPrescriptionMedicines(true);
      setError("");

      const response = await fetch(
        `${API_URL}/prescriptions/${prescriptionId}/medicines`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(
            data,
            "Failed to load prescribed medicines"
          )
        );
      }

      const medicineList = Array.isArray(data) ? data : [];

      setPrescribedMedicines(medicineList);

      if (medicineList.length > 0) {
        const firstMedicine = medicineList[0];

        setSelectedPrescribedMedicine(firstMedicine);

        setItemForm((previous) => ({
          ...previous,
          medicine_id: String(firstMedicine.medicine_id),
          batch_id: "",
          quantity: String(firstMedicine.quantity || ""),
        }));

        await loadBatches(firstMedicine.medicine_id);
      } else {
        setSelectedPrescribedMedicine(null);

        setItemForm((previous) => ({
          ...previous,
          medicine_id: "",
          batch_id: "",
          quantity: "",
        }));

        setBatches([]);
      }
    } catch (err) {
      console.error(
        "Prescription medicine loading error:",
        err
      );

      setPrescribedMedicines([]);
      setSelectedPrescribedMedicine(null);
      setBatches([]);

      setError(
        err.message ||
          "Failed to load prescribed medicines"
      );
    } finally {
      setLoadingPrescriptionMedicines(false);
    }
  };

  const loadBatches = async (medicineId) => {
    if (!medicineId) {
      setBatches([]);
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/medicine-batches?medicine_id=${medicineId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data, "Failed to load batches")
        );
      }

      setBatches(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Batch loading error:", err);

      setBatches([]);

      setError(
        err.message || "Failed to load medicine batches"
      );
    }
  };

  const getMedicineName = (medicineId) => {
    const medicine = medicines.find(
      (item) => Number(item.id) === Number(medicineId)
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

  const getPatientDisplayName = (patient) => {
    if (patient.name) {
      return patient.name;
    }

    if (patient.user_name) {
      return patient.user_name;
    }

    if (patient.full_name) {
      return patient.full_name;
    }

    return `Patient #${patient.id}`;
  };

  const getPatientPrescriptions = () => {
    if (!purchaseForm.patient_id) {
      return [];
    }

    return prescriptions.filter(
      (prescription) =>
        Number(prescription.patient_id) ===
        Number(purchaseForm.patient_id)
    );
  };

  const handlePatientChange = (event) => {
    const patientId = event.target.value;

    setPurchaseForm({
      patient_id: patientId,
      prescription_id: "",
      total_amount: "",
      email: "",
      phone: "",
      email_enabled: true,
      whatsapp_enabled: false,
      sms_enabled: false,
      notification_consent: false,
    });

    setMessage("");
    setError("");
  };

  const handleCreatePurchase = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");

    if (!purchaseForm.patient_id) {
      setError("Please select a patient.");
      return;
    }

    if (
      purchaseForm.total_amount === "" ||
      Number(purchaseForm.total_amount) < 0
    ) {
      setError("Please enter a valid total amount.");
      return;
    }

    if (!purchaseForm.email_enabled) {
      setError(
        "Email notifications must be enabled. WhatsApp and SMS are coming soon."
      );
      return;
    }

    if (!purchaseForm.email.trim()) {
      setError(
        "Email is required for expiry notifications."
      );
      return;
    }

    if (!purchaseForm.notification_consent) {
      setError(
        "Please confirm that the patient has explicitly consented to receive expiry notifications by Email."
      );
      return;
    }

    try {
      if (!token) {
        throw new Error(
          "Authentication token not found. Please login again."
        );
      }

      const response = await fetch(`${API_URL}/purchases`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          patient_id: Number(purchaseForm.patient_id),

          prescription_id: purchaseForm.prescription_id
            ? Number(purchaseForm.prescription_id)
            : null,

          total_amount: Number(
            purchaseForm.total_amount
          ),

          email: purchaseForm.email.trim()
            ? purchaseForm.email.trim()
            : null,

          phone: purchaseForm.phone.trim()
            ? purchaseForm.phone.trim()
            : null,

          email_enabled: purchaseForm.email_enabled,

          whatsapp_enabled:
            purchaseForm.whatsapp_enabled,

          sms_enabled: purchaseForm.sms_enabled,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(
            data,
            "Failed to create purchase"
          )
        );
      }

      setMessage(
        `Purchase #${data.id} created successfully.`
      );

      setPurchaseForm({
        patient_id: "",
        prescription_id: "",
        total_amount: "",
        email: "",
        phone: "",
        email_enabled: true,
        whatsapp_enabled: false,
        sms_enabled: false,
        notification_consent: false,
      });

      await loadPurchases();
    } catch (err) {
      console.error("Create purchase error:", err);

      setError(
        err.message || "Failed to create purchase"
      );
    }
  };

  const handleSelectPurchase = async (purchase) => {
    setSelectedPurchase(purchase);

    setMessage("");
    setError("");

    setItemForm({
      medicine_id: "",
      batch_id: "",
      quantity: "",
      unit_price: "",
    });

    setBatches([]);
    setPrescribedMedicines([]);
    setSelectedPrescribedMedicine(null);

    if (purchase.prescription_id) {
      await loadPrescriptionMedicines(
        purchase.prescription_id
      );
    }
  };

  const handlePrescribedMedicineChange = async (
    event
  ) => {
    const medicineId = event.target.value;

    const prescribedMedicine =
      prescribedMedicines.find(
        (item) =>
          Number(item.medicine_id) ===
          Number(medicineId)
      );

    setSelectedPrescribedMedicine(
      prescribedMedicine || null
    );

    setItemForm({
      ...itemForm,
      medicine_id: medicineId,
      batch_id: "",
      quantity: prescribedMedicine
        ? String(
            prescribedMedicine.quantity || ""
          )
        : "",
    });

    setError("");

    await loadBatches(medicineId);
  };

  const handleAddItem = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");

    if (!selectedPurchase) {
      setError("Please select a purchase.");
      return;
    }

    if (!selectedPurchase.prescription_id) {
      setError(
        "This purchase is not linked to a prescription."
      );
      return;
    }

    if (!itemForm.medicine_id) {
      setError(
        "Please select a prescribed medicine."
      );
      return;
    }

    if (!itemForm.batch_id) {
      setError(
        "Please select a medicine batch."
      );
      return;
    }

    if (
      !itemForm.quantity ||
      Number(itemForm.quantity) <= 0
    ) {
      setError("Quantity must be greater than zero.");
      return;
    }

    if (
      itemForm.unit_price === "" ||
      Number(itemForm.unit_price) < 0
    ) {
      setError("Please enter a valid unit price.");
      return;
    }

    try {
      if (!token) {
        throw new Error(
          "Authentication token not found. Please login again."
        );
      }

      const response = await fetch(
        `${API_URL}/purchases/items`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            purchase_id: selectedPurchase.id,
            medicine_id: Number(
              itemForm.medicine_id
            ),
            batch_id: Number(
              itemForm.batch_id
            ),
            quantity: Number(
              itemForm.quantity
            ),
            unit_price: Number(
              itemForm.unit_price
            ),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(
            data,
            "Failed to add medicine to purchase"
          )
        );
      }

      setItemForm({
        medicine_id: "",
        batch_id: "",
        quantity: "",
        unit_price: "",
      });

      setBatches([]);

      if (selectedPurchase.prescription_id) {
        await loadPrescriptionMedicines(
          selectedPurchase.prescription_id
        );
      }

      await loadPurchases();

      try {
        const completeResponse = await fetch(
          `${API_URL}/purchases/${selectedPurchase.id}/complete`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const completeData =
          await completeResponse.json();

        if (!completeResponse.ok) {
          console.error(
            "Purchase completion error:",
            completeData
          );

          setMessage(
            "Medicine added successfully. Purchase completion is pending."
          );

          return;
        }

        if (completeData.completed) {
          if (completeData.already_sent) {
            setMessage(
              "Purchase completed. Digital medicine sheet was already sent."
            );
          } else {
            setMessage(
              "Purchase completed successfully. Digital medicine sheet sent to the patient."
            );
          }
        } else {
          setMessage(
            "Medicine added successfully. Waiting for the remaining prescribed medicines."
          );
        }

        await loadPurchases();
      } catch (completionError) {
        console.error(
          "Automatic purchase completion error:",
          completionError
        );

        setMessage(
          "Medicine added successfully. Purchase completion is pending."
        );
      }
    } catch (err) {
      console.error(
        "Add purchase item error:",
        err
      );

      setError(
        err.message ||
          "Failed to add medicine to purchase"
      );
    }
  };

  const handleClosePurchase = () => {
    setSelectedPurchase(null);

    setItemForm({
      medicine_id: "",
      batch_id: "",
      quantity: "",
      unit_price: "",
    });

    setBatches([]);
    setPrescribedMedicines([]);
    setSelectedPrescribedMedicine(null);

    setMessage("");
    setError("");
  };

  return (
    <div className="page-container">
      {message && (
        <div className="success-message">
          {message}
        </div>
      )}

      {error && (
        <div className="error-message">
          {String(error)}
        </div>
      )}

      <div className="page-header">
        <div>
          <h2>Purchases</h2>

          <p>
            Create patient purchases, configure
            notification channels, and add prescribed
            medicines from specific medicine batches.
          </p>
        </div>
      </div>

      <div className="form-card">
        <h3>Create New Purchase</h3>

        <form
          onSubmit={handleCreatePurchase}
          className="medicine-form"
        >
          <div className="form-group">
            <label>Patient</label>

            <select
              value={purchaseForm.patient_id}
              onChange={handlePatientChange}
            >
              <option value="">
                Select Patient
              </option>

              {patients.map((patient) => (
                <option
                  key={patient.id}
                  value={patient.id}
                >
                  {getPatientDisplayName(patient)}

                  {patient.user_id
                    ? ` - Patient #${patient.id}`
                    : ""}
                </option>
              ))}
            </select>
          </div>

          {purchaseForm.patient_id && (
            <>
              <div className="section-divider">
                <h4>Patient Contact Details</h4>

                <p>
                  Enter or confirm the patient's contact
                  details for digital medicine sheets and
                  expiry notifications.
                </p>
              </div>

              <div className="form-group">
                <label>
                  Email
                </label>

                <input
                  type="email"
                  placeholder="Enter patient email"
                  value={purchaseForm.email}
                  onChange={(event) =>
                    setPurchaseForm({
                      ...purchaseForm,
                      email: event.target.value,
                    })
                  }
                />
              </div>

              <div className="form-group">
                <label>
                  Mobile / WhatsApp Number
                </label>

                <input
                  type="tel"
                  placeholder="Enter mobile number"
                  value={purchaseForm.phone}
                  onChange={(event) =>
                    setPurchaseForm({
                      ...purchaseForm,
                      phone: event.target.value,
                    })
                  }
                />
              </div>

              <div className="section-divider">
                <h4>
                  Notification Channels
                </h4>

                <p>
                  The pharmacy selects how the patient
                  will receive the medicine sheet and
                  expiry notifications.
                </p>
              </div>

              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={
                      purchaseForm.email_enabled
                    }
                    onChange={(event) =>
                      setPurchaseForm({
                        ...purchaseForm,
                        email_enabled:
                          event.target.checked,
                      })
                    }
                  />

                  <span>
                    Email
                  </span>
                </label>
              </div>

              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={false}
                    disabled
                  />

                  <span>
                    WhatsApp{" "}
                    <span className="optional-label">
                      (Coming soon)
                    </span>
                  </span>
                </label>
              </div>

              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={false}
                    disabled
                  />

                  <span>
                    SMS{" "}
                    <span className="optional-label">
                      (Coming soon)
                    </span>
                  </span>
                </label>
              </div>

              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={
                      purchaseForm.notification_consent
                    }
                    onChange={(event) =>
                      setPurchaseForm({
                        ...purchaseForm,
                        notification_consent:
                          event.target.checked,
                      })
                    }
                  />

                  <span>
                    Patient has explicitly consented to receive
                    expiry notifications by Email.
                  </span>
                </label>
              </div>
            </>
          )}

          <div className="form-group">
            <label>
              Prescription{" "}
              <span className="optional-label">
                (Optional)
              </span>
            </label>

            <select
              value={purchaseForm.prescription_id}
              onChange={(event) =>
                setPurchaseForm({
                  ...purchaseForm,
                  prescription_id:
                    event.target.value,
                })
              }
              disabled={!purchaseForm.patient_id}
            >
              <option value="">
                {!purchaseForm.patient_id
                  ? "Select patient first"
                  : getPatientPrescriptions().length === 0
                  ? "No prescriptions found"
                  : "Select Prescription"}
              </option>

              {getPatientPrescriptions().map(
                (prescription) => (
                  <option
                    key={prescription.id}
                    value={prescription.id}
                  >
                    Prescription #
                    {prescription.id}
                    {" - "}
                    {prescription.prescription_date}
                    {" - "}
                    {prescription.status}
                  </option>
                )
              )}
            </select>
          </div>

          <div className="form-group">
            <label>
              Total Amount
            </label>

            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="Enter total amount"
              value={purchaseForm.total_amount}
              onChange={(event) =>
                setPurchaseForm({
                  ...purchaseForm,
                  total_amount:
                    event.target.value,
                })
              }
            />
          </div>

          <button
            type="submit"
            className="primary-button"
          >
            Create Purchase
          </button>
        </form>
      </div>

      <div className="table-card">
        <div className="section-header">
          <div>
            <h3>
              Purchase History
            </h3>

            <p>
              Purchases created by your pharmacy.
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={loadPurchases}
          >
            Refresh
          </button>
        </div>

        {loading ? (
          <p className="empty-message">
            Loading purchases...
          </p>
        ) : purchases.length === 0 ? (
          <p className="empty-message">
            No purchases found.
          </p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Patient ID</th>
                  <th>Prescription ID</th>
                  <th>Total Amount</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {purchases.map((purchase) => (
                  <tr key={purchase.id}>
                    <td>
                      #{purchase.id}
                    </td>

                    <td>
                      {purchase.patient_id}
                    </td>

                    <td>
                      {purchase.prescription_id
                        ? purchase.prescription_id
                        : "—"}
                    </td>

                    <td>
                      ₹
                      {Number(
                        purchase.total_amount || 0
                      ).toFixed(2)}
                    </td>

                    <td>
                      {purchase.created_at
                        ? new Date(
                            purchase.created_at
                          ).toLocaleDateString()
                        : "—"}
                    </td>

                    <td>
                      <button
                        type="button"
                        className="small-button"
                        onClick={() =>
                          handleSelectPurchase(
                            purchase
                          )
                        }
                      >
                        Add Medicines
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedPurchase && (
        <div className="form-card purchase-item-card">
          <div className="section-header">
            <div>
              <h3>
                Add Medicines to Purchase #
                {selectedPurchase.id}
              </h3>

              <p>
                Patient ID:{" "}
                {selectedPurchase.patient_id}
              </p>

              <p>
                Prescription ID:{" "}
                {selectedPurchase.prescription_id ||
                  "—"}
              </p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={handleClosePurchase}
            >
              Close
            </button>
          </div>

          {!selectedPurchase.prescription_id && (
            <div className="error-message">
              This purchase is not linked to a
              prescription. Please create a new purchase
              with a prescription selected.
            </div>
          )}

          {selectedPurchase.prescription_id &&
            loadingPrescriptionMedicines && (
              <div className="empty-message">
                Loading prescribed medicines...
              </div>
            )}

          {selectedPurchase.prescription_id &&
            !loadingPrescriptionMedicines &&
            prescribedMedicines.length === 0 && (
              <div className="empty-message">
                No medicines are attached to this
                prescription.
              </div>
            )}

          {selectedPurchase.prescription_id &&
            !loadingPrescriptionMedicines &&
            prescribedMedicines.length > 0 && (
              <form
                onSubmit={handleAddItem}
                className="medicine-form"
              >
                <div className="form-group">
                  <label>
                    Prescribed Medicine
                  </label>

                  <select
                    value={itemForm.medicine_id}
                    onChange={
                      handlePrescribedMedicineChange
                    }
                  >
                    <option value="">
                      Select Prescribed Medicine
                    </option>

                    {prescribedMedicines.map(
                      (prescribedMedicine) => (
                        <option
                          key={prescribedMedicine.id}
                          value={
                            prescribedMedicine.medicine_id
                          }
                        >
                          {getMedicineName(
                            prescribedMedicine.medicine_id
                          )}
                          {" - "}
                          {prescribedMedicine.dosage}
                        </option>
                      )
                    )}
                  </select>
                </div>

                {selectedPrescribedMedicine && (
                  <div className="card">
                    <h4>
                      Prescription Instructions
                    </h4>

                    <p>
                      <strong>
                        Medicine:
                      </strong>{" "}
                      {getMedicineName(
                        selectedPrescribedMedicine.medicine_id
                      )}
                    </p>

                    <p>
                      <strong>
                        Dosage:
                      </strong>{" "}
                      {selectedPrescribedMedicine.dosage}
                    </p>

                    <p>
                      <strong>
                        Frequency:
                      </strong>{" "}
                      {selectedPrescribedMedicine.frequency}
                    </p>

                    <p>
                      <strong>
                        Timing:
                      </strong>{" "}
                      {selectedPrescribedMedicine.timing ||
                        "Not specified"}
                    </p>

                    <p>
                      <strong>
                        Food Instruction:
                      </strong>{" "}
                      {selectedPrescribedMedicine.food_instruction ||
                        "Not specified"}
                    </p>

                    <p>
                      <strong>
                        Duration:
                      </strong>{" "}
                      {selectedPrescribedMedicine.duration_days}{" "}
                      day(s)
                    </p>

                    <p>
                      <strong>
                        Prescribed Quantity:
                      </strong>{" "}
                      {selectedPrescribedMedicine.quantity}
                    </p>
                  </div>
                )}

                <div className="form-group">
                  <label>
                    Medicine Batch
                  </label>

                  <select
                    value={itemForm.batch_id}
                    onChange={(event) =>
                      setItemForm({
                        ...itemForm,
                        batch_id:
                          event.target.value,
                      })
                    }
                    disabled={!itemForm.medicine_id}
                  >
                    <option value="">
                      {itemForm.medicine_id
                        ? "Select Batch"
                        : "Select prescribed medicine first"}
                    </option>

                    {batches.map((batch) => (
                      <option
                        key={batch.id}
                        value={batch.id}
                      >
                        {batch.batch_number} - Expiry:{" "}
                        {batch.expiry_date}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>
                    Quantity
                  </label>

                  <input
                    type="number"
                    min="1"
                    placeholder="Enter quantity"
                    value={itemForm.quantity}
                    onChange={(event) =>
                      setItemForm({
                        ...itemForm,
                        quantity:
                          event.target.value,
                      })
                    }
                  />
                </div>

                <div className="form-group">
                  <label>
                    Unit Price
                  </label>

                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="Enter unit price"
                    value={itemForm.unit_price}
                    onChange={(event) =>
                      setItemForm({
                        ...itemForm,
                        unit_price:
                          event.target.value,
                      })
                    }
                  />
                </div>

                <button
                  type="submit"
                  className="primary-button"
                >
                  Add Prescribed Medicine
                </button>
              </form>
            )}
        </div>
      )}
    </div>
  );
}

export default Purchases;