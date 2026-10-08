/* Prescription medicine selection with intake patterns */

const selectedMedicines = new Map();

function addMedicine(id, name, strength) {
  const key = String(id);
  if (selectedMedicines.has(key)) {
    showToast('Medicine already selected.', 'info');
    const existing = document.getElementById(`selected-med-${key}`);
    if (existing) {
      existing.classList.add('highlight');
      existing.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(() => existing.classList.remove('highlight'), 800);
    }
    return;
  }
  selectedMedicines.set(key, {
    medicine_id: id,
    medicine_name: name,
    dosage: strength || '',
    medicine_intake: '1-0-1',
    number_of_days: 5,
    quantity: 10,
    instructions: '',
  });
  renderSelected();
  showToast(`${name} added.`, 'success');
}

function removeMedicine(id) {
  selectedMedicines.delete(String(id));
  renderSelected();
}

function setIntake(id, pattern) {
  const med = selectedMedicines.get(String(id));
  if (!med) return;
  med.medicine_intake = pattern;
  const input = document.querySelector(`#selected-med-${id} .intake-input`);
  if (input) input.value = pattern;
}

function applyCustomIntake(id) {
  const row = document.getElementById(`selected-med-${id}`);
  if (!row) return;
  const m = row.querySelector('.custom-m').value;
  const a = row.querySelector('.custom-a').value;
  const n = row.querySelector('.custom-n').value;
  setIntake(id, `${m}-${a}-${n}`);
}

function toggleCustom(id) {
  const el = document.querySelector(`#selected-med-${id} .custom-intake`);
  if (el) el.classList.toggle('open');
}

function updateField(id, field, value) {
  const med = selectedMedicines.get(String(id));
  if (!med) return;
  if (field === 'number_of_days' || field === 'quantity') {
    med[field] = parseInt(value, 10) || 1;
  } else {
    med[field] = value;
  }
}

function renderSelected() {
  const container = document.getElementById('selected-medicines');
  if (!container) return;
  if (selectedMedicines.size === 0) {
    container.innerHTML = '<div class="empty-state">No medicines selected. Click + to add.</div>';
    return;
  }
  const presets = ['1-0-1', '1-1-1', '0-1-0', '0-0-1', '1-0-0'];
  let html = '';
  selectedMedicines.forEach((med, key) => {
    const opts = Array.from({ length: 11 }, (_, i) =>
      `<option value="${i}">${i}</option>`
    ).join('');
    html += `
      <div class="selected-med" id="selected-med-${key}">
        <h4>
          <span>${med.medicine_name}</span>
          <button type="button" class="btn-icon danger" onclick="removeMedicine('${key}')" title="Remove">−</button>
        </h4>
        <div class="form-grid">
          <div class="form-group">
            <label>Dosage / Strength</label>
            <input class="form-control" value="${med.dosage || ''}"
              onchange="updateField('${key}','dosage',this.value)">
          </div>
          <div class="form-group">
            <label>Number of Days</label>
            <input type="number" min="1" class="form-control" value="${med.number_of_days}"
              onchange="updateField('${key}','number_of_days',this.value)">
          </div>
          <div class="form-group">
            <label>Quantity</label>
            <input type="number" min="1" class="form-control" value="${med.quantity}"
              onchange="updateField('${key}','quantity',this.value)">
          </div>
          <div class="form-group">
            <label>Medicine Intake (M-A-N)</label>
            <input class="form-control intake-input" value="${med.medicine_intake}" readonly>
          </div>
        </div>
        <label style="font-size:0.85rem;font-weight:600;">Intake Pattern Presets</label>
        <div class="intake-presets">
          ${presets.map((p) =>
            `<button type="button" onclick="setIntake('${key}','${p}')">${p}</button>`
          ).join('')}
          <button type="button" onclick="toggleCustom('${key}')">Custom Pattern</button>
        </div>
        <div class="custom-intake">
          <div class="form-group">
            <label>Morning</label>
            <select class="form-control custom-m">${opts}</select>
          </div>
          <div class="form-group">
            <label>Afternoon</label>
            <select class="form-control custom-a">${opts}</select>
          </div>
          <div class="form-group">
            <label>Night</label>
            <select class="form-control custom-n">${opts}</select>
          </div>
          <div class="form-group" style="align-self:end;">
            <button type="button" class="btn btn-secondary btn-sm" onclick="applyCustomIntake('${key}')">Apply</button>
          </div>
        </div>
        <div class="form-group" style="margin-top:0.75rem;">
          <label>Instructions</label>
          <textarea class="form-control" rows="2"
            onchange="updateField('${key}','instructions',this.value)">${med.instructions || ''}</textarea>
        </div>
      </div>`;
  });
  container.innerHTML = html;
}

async function savePrescription() {
  const patientId = document.getElementById('rx-patient-id')?.value;
  const diagnosis = document.getElementById('rx-diagnosis')?.value || '';
  const notes = document.getElementById('rx-notes')?.value || '';
  if (selectedMedicines.size === 0) {
    showToast('Please select at least one medicine.', 'error');
    return;
  }
  const btn = document.getElementById('btn-save-rx');
  if (btn) btn.classList.add('loading');
  try {
    const data = await apiFetch('/api/prescriptions', {
      method: 'POST',
      body: {
        patient_id: patientId,
        diagnosis,
        notes,
        medicines: Array.from(selectedMedicines.values()),
      },
    });
    showToast(data.message || 'Prescription saved.', 'success');
    setTimeout(() => {
      window.location.href = '/doctor/prescription-history';
    }, 800);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    if (btn) btn.classList.remove('loading');
  }
}

function filterMedicineList() {
  const q = (document.getElementById('med-search')?.value || '').toLowerCase();
  document.querySelectorAll('.med-list-item').forEach((el) => {
    const name = (el.dataset.name || '').toLowerCase();
    el.style.display = name.includes(q) ? '' : 'none';
  });
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('selected-medicines')) {
    renderSelected();
  }
  document.querySelectorAll('.btn-add-med').forEach((btn) => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.med-list-item');
      if (!item) return;
      addMedicine(item.dataset.id, item.dataset.name, item.dataset.strength || '');
    });
  });
});
