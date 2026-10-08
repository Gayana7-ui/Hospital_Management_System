/* Real-time queue polling */

async function refreshQueue(containerId, intervalMs = 5000) {
  const container = document.getElementById(containerId);
  if (!container) return;

  async function load() {
    try {
      const data = await apiFetch('/api/tokens/queue');
      const tokens = data.data || [];
      if (!tokens.length) {
        container.innerHTML = '<div class="empty-state">No patients in queue.</div>';
        return;
      }
      let html = `<div class="table-wrap"><table class="data"><thead>
        <tr><th>Token</th><th>Patient</th><th>Doctor</th><th>Time</th><th>Position</th><th>Status</th><th>Action</th></tr>
        </thead><tbody>`;
      tokens.forEach((t) => {
        html += `<tr>
          <td><strong>${t.token_number}</strong></td>
          <td>${t.patient_name || ''} (${t.patient_id || ''})</td>
          <td>${t.doctor_name || '-'}</td>
          <td>${t.appointment_time || '-'}</td>
          <td>${t.queue_position}</td>
          <td><span class="badge ${badgeClass(t.status)}">${t.status}</span></td>
          <td>
            <select class="form-control" style="width:auto;display:inline-block;"
              onchange="updateTokenStatus(${t.id}, this.value)">
              <option value="">Update...</option>
              <option value="Waiting">Waiting</option>
              <option value="In Consultation">In Consultation</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </td>
        </tr>`;
      });
      html += '</tbody></table></div>';
      container.innerHTML = html;
    } catch (err) {
      console.warn('Queue refresh failed:', err.message);
    }
  }

  await load();
  setInterval(load, intervalMs);
}

async function updateTokenStatus(tokenId, status) {
  if (!status) return;
  try {
    await apiFetch(`/api/tokens/${tokenId}/status`, {
      method: 'POST',
      body: { status },
    });
    showToast('Token status updated.', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function updateAppointmentStatus(apptId, status) {
  if (!status) return;
  try {
    await apiFetch(`/api/appointments/${apptId}/status`, {
      method: 'POST',
      body: { status },
    });
    showToast('Appointment status updated.', 'success');
    setTimeout(() => location.reload(), 600);
  } catch (err) {
    showToast(err.message, 'error');
  }
}
